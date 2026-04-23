---
name: reddit
display_name: "Reddit"
description: "Search and read Reddit — browse subreddits, trending posts, comments, and full-text search. Read-only, no auth required."
category: social
icon: message-circle
skill_type: sandbox
catalog_type: addon
requirements: "httpx>=0.25"
tool_schema:
  name: reddit
  description: "Search and read Reddit — browse subreddits, trending posts, comments, and full-text search. Read-only, no auth required."
  parameters:
    type: object
    properties:
      action:
        type: "string"
        description: "Which operation to perform"
        enum: ['get_hot', 'get_new', 'get_top', 'search', 'get_comments']
      subreddit:
        type: "string"
        description: "Subreddit name without r/ prefix (e.g. 'artificial'). Omit to search all of Reddit."
        default: ""
      query:
        type: "string"
        description: "Search query -- for search action"
        default: ""
      post_id:
        type: "string"
        description: "Post ID -- for get_comments (the alphanumeric ID from the URL, e.g. '1abc2de')"
        default: ""
      limit:
        type: "integer"
        description: "Number of results to return (default 10, max 100)"
        default: 10
      time_filter:
        type: "string"
        description: "Time filter for get_top and search: hour, day, week, month, year, all (default week)"
        default: "week"
    required: [action]
---
# Reddit

Search and read Reddit posts, comments, and subreddit discussions. Read-only — no auth required.

## Actions
- **get_hot** -- Hot posts from a subreddit (or all of Reddit if no subreddit specified)
- **get_new** -- Latest posts from a subreddit
- **get_top** -- Top posts from a subreddit. Use `time_filter` to set range (hour, day, week, month, year, all)
- **search** -- Search posts across Reddit or within a subreddit. Provide `query`, optionally `time_filter`
- **get_comments** -- Read comments on a post. Provide `subreddit` and `post_id`

## Response Format
Each post includes:
- `reddit_url` — the Reddit discussion page URL (on old.reddit.com, ready for browser automation)
- `external_url` — only present if the post links to an external site (not for self/text posts)
- `post_id`, `title`, `author`, `subreddit`, `score`, `num_comments`, `selftext`

**Always use `reddit_url` to open the post on Reddit.** The `external_url` is only the link the post points to (could be an article, image, etc.).

## Tips
- Use `search` to find discussions about specific topics, products, or technologies
- Use `get_hot` on relevant subreddits to see what communities are talking about right now
- Use `get_comments` to understand community sentiment on a topic
- Use `reddit_url` from results to navigate to posts in the browser — it's always a valid old.reddit.com link
- Good subreddits for AI/tech: artificial, MachineLearning, LocalLLaMA, SaaS, AutoGPT, LangChain, devops
