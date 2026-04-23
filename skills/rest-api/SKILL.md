---
name: rest-api
display_name: "REST API Call"
description: "Make HTTP requests to external APIs — GET, POST, PUT, PATCH, DELETE"
category: general
icon: globe
skill_type: tool
catalog_type: core
tool_schema:
  name: rest_api_call
  description: "Make an HTTP request to an external REST API"
  parameters:
    type: object
    properties:
      url:
        type: "string"
        description: "The full URL to send the request to"
      method:
        type: "string"
        description: "HTTP method"
        enum: ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]
        default: "GET"
      headers:
        type: "string"
        description: "Request headers as a JSON string, e.g. {\"Authorization\": \"Bearer token\", \"Content-Type\": \"application/json\"}"
        default: ""
      body:
        type: "string"
        description: "Request body as a JSON string (for POST, PUT, PATCH)"
        default: ""
    required: [url]
---
# REST API Call
Make HTTP requests to external REST APIs.

- **url** — The full URL to send the request to.
- **method** — HTTP method: GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS (default: GET).
- **headers** — Optional JSON string of request headers.
- **body** — Optional JSON string for request body (POST, PUT, PATCH).

Returns the HTTP status code and response body (JSON formatted when possible, text otherwise). Supports redirects and timeouts up to 30 seconds.
