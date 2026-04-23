import os
import json
import time
import httpx

DOMAINS = ["https://www.reddit.com", "https://old.reddit.com"]
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Cache-Control": "no-cache",
}


def api_get(url, params=None, timeout=20):
    """Fetch Reddit JSON API with retry across domains.

    Reddit aggressively blocks datacenter IPs. We try each domain up to 2 times
    with delays between attempts to avoid rate limiting.
    """
    last_error = None
    with httpx.Client(timeout=timeout, headers=HEADERS, follow_redirects=True) as c:
        for domain in DOMAINS:
            actual_url = url.replace(DOMAINS[0], domain).replace(DOMAINS[1], domain)
            for attempt in range(2):
                try:
                    r = c.get(actual_url, params=params)
                    if r.status_code == 200:
                        return r.json()
                    if r.status_code in (403, 429, 503):
                        last_error = f"Reddit returned {r.status_code} from {domain}"
                        time.sleep(1.5 + attempt)
                        continue
                    r.raise_for_status()
                except httpx.HTTPStatusError as e:
                    last_error = f"HTTP {e.response.status_code}"
                    time.sleep(1)
                except (httpx.ConnectError, httpx.ReadTimeout) as e:
                    last_error = str(e)
                    time.sleep(1)
        raise httpx.HTTPStatusError(
            f"Reddit API blocked after all retries: {last_error}",
            request=httpx.Request("GET", url),
            response=httpx.Response(403),
        )


def format_post(item):
    d = item.get("data", {})
    permalink = d.get("permalink", "")
    link_url = d.get("url", "")
    # If the link points to reddit itself (self post, gallery, video), don't include it separately
    is_self = link_url.startswith("https://www.reddit.com") or link_url.startswith("/r/") or d.get("is_self", False)
    result = {
        "title": d.get("title", ""),
        "author": d.get("author", ""),
        "subreddit": d.get("subreddit", ""),
        "score": d.get("score", 0),
        "num_comments": d.get("num_comments", 0),
        "reddit_url": f"https://old.reddit.com{permalink}",
        "post_id": d.get("id", ""),
        "selftext": (d.get("selftext", "") or "")[:500] or None,
        "created_utc": d.get("created_utc", 0),
    }
    if not is_self and link_url:
        result["external_url"] = link_url
    return result


def format_comment(item, depth=0):
    d = item.get("data", {})
    body = d.get("body", "") or ""
    if len(body) > 500:
        body = body[:500] + "..."
    return {
        "author": d.get("author", ""),
        "body": body,
        "score": d.get("score", 0),
        "comment_id": d.get("id", ""),
        "depth": depth,
        "created_utc": d.get("created_utc", 0),
    }


# --- Actions ---


def do_get_listing(subreddit, sort, limit, time_filter=""):
    path = f"/r/{subreddit}/{sort}.json" if subreddit else f"/{sort}.json"
    params = {"limit": limit, "raw_json": 1}
    if sort == "top" and time_filter:
        params["t"] = time_filter
    data = api_get(f"{DOMAINS[0]}{path}", params=params)
    children = data.get("data", {}).get("children", [])
    posts = [format_post(c) for c in children if c.get("kind") == "t3"]
    return {"subreddit": subreddit or "all", "sort": sort, "posts": posts, "count": len(posts)}


def do_search(query, subreddit, time_filter, limit):
    if not query:
        return {"error": "query is required for search"}
    path = f"/r/{subreddit}/search.json" if subreddit else "/search.json"
    params = {
        "q": query,
        "limit": limit,
        "sort": "relevance",
        "raw_json": 1,
    }
    if time_filter:
        params["t"] = time_filter
    if subreddit:
        params["restrict_sr"] = "on"
    data = api_get(f"{DOMAINS[0]}{path}", params=params)
    children = data.get("data", {}).get("children", [])
    posts = [format_post(c) for c in children if c.get("kind") == "t3"]
    return {"query": query, "subreddit": subreddit or "all", "posts": posts, "count": len(posts)}


def do_get_comments(subreddit, post_id, limit):
    if not post_id:
        return {"error": "post_id is required for get_comments"}
    if not subreddit:
        return {"error": "subreddit is required for get_comments"}
    data = api_get(
        f"{DOMAINS[0]}/r/{subreddit}/comments/{post_id}.json",
        params={"limit": limit, "depth": 2, "raw_json": 1},
    )
    if not isinstance(data, list) or len(data) < 2:
        return {"error": f"Post {post_id} not found in r/{subreddit}"}

    # First listing is the post itself
    post_children = data[0].get("data", {}).get("children", [])
    post_info = format_post(post_children[0]) if post_children else {}

    # Second listing is comments
    comment_children = data[1].get("data", {}).get("children", [])
    comments = []
    for c in comment_children:
        if c.get("kind") != "t1":
            continue
        comments.append(format_comment(c, depth=0))
        # Include one level of replies
        replies = c.get("data", {}).get("replies")
        if isinstance(replies, dict):
            for rc in replies.get("data", {}).get("children", []):
                if rc.get("kind") == "t1":
                    comments.append(format_comment(rc, depth=1))

    return {"post": post_info, "comments": comments[:limit], "count": min(len(comments), limit)}


# --- Main ---

try:
    inp = json.loads(os.environ.get("INPUT_JSON", "{}"))
    action = inp.get("action", "")
    limit = max(1, min(100, int(inp.get("limit", 10) or 10)))
    subreddit = (inp.get("subreddit", "") or "").strip().lstrip("r/")
    time_filter = inp.get("time_filter", "week") or "week"
    if time_filter not in ("hour", "day", "week", "month", "year", "all"):
        time_filter = "week"

    if action == "get_hot":
        result = do_get_listing(subreddit, "hot", limit)
    elif action == "get_new":
        result = do_get_listing(subreddit, "new", limit)
    elif action == "get_top":
        result = do_get_listing(subreddit, "top", limit, time_filter)
    elif action == "search":
        query = (inp.get("query", "") or "").strip()
        result = do_search(query, subreddit, time_filter, limit)
    elif action == "get_comments":
        post_id = (inp.get("post_id", "") or "").strip()
        result = do_get_comments(subreddit, post_id, limit)
    else:
        result = {"error": f"Unknown action: {action}. Available: get_hot, get_new, get_top, search, get_comments"}

    print(json.dumps(result))

except httpx.HTTPStatusError as e:
    status = e.response.status_code
    if status == 403:
        print(json.dumps({"error": "Reddit API returned 403 (blocked). Reddit blocks requests from cloud/datacenter IPs. Use the browser tool to browse old.reddit.com directly instead."}))
    else:
        detail = ""
        try:
            detail = e.response.json().get("message", "") or str(e.response.json())
        except Exception:
            detail = e.response.text[:200] if hasattr(e.response, 'text') else ""
        print(json.dumps({"error": f"Reddit API error {status}: {detail}" if detail else f"Reddit API error {status}"}))
except Exception as e:
    print(json.dumps({"error": str(e)}))
