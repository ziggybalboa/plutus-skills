# Public directory protocol

Endpoint: `https://plutusai.net/mcp/funders` (no authentication).
POST JSON with `Content-Type: application/json` and `Accept: application/json, text/event-stream`.

A normal MCP client can initialize with:
```json
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"funder-research","version":"1.0.0"}}}
```
The server also supports stateless JSON requests (used by the helper):
```json
{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}
```
```json
{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"search_funders","arguments":{"product":"MCA","limit":5,"offset":0}}}
```

## Arguments
Always check live `tools/list` first. No extra properties are accepted.

| Tool | Argument | Contract |
|---|---|---|
| search_funders | q | Optional string, maximum 300 characters; natural-language concepts and numeric criteria |
| search_funders | product | Optional string, maximum 60 characters; no enumerated values in schema |
| search_funders | state | Optional string, maximum 60 characters; no enumerated values in schema |
| search_funders | limit | Integer 1–50, default 20 |
| search_funders | offset | Integer 0–10000, default 0 |
| get_funder | id | Required UUID string, copied from search |

The tool result has `structuredContent` and JSON text in `content`. Prefer structuredContent. Search data contains `funders`, `total`, `limit`, `offset`, `next_offset`, and may contain `interpretation`. Detail data contains `funder` (object or null). Stop pagination at null `next_offset`; do not exceed the schema's offset ceiling or claim complete coverage beyond it.

Errors may be JSON-RPC `error`, tool `isError`, or an HTTP failure. Invalid UUIDs and out-of-range limits return JSON-RPC error `-32602`; these are not no-results responses. Schemas and public data can change.

## Evidence fields
Profiles provide `id`, `name`, `url`, products and product details, amounts/currency, terms, eligibility, geography, research summaries, and source/quality/freshness metadata. Fields are nullable. Preserve numeric unknowns rather than deriving them from conflicting prose. `quality.status` may be `ai_enriched_unverified`, with `inferred`, `confidence`, `conflicts`, and `warning_codes`. `sources` are references, not field-level verification. `freshness.enriched_at` and `published_at` describe different events, not independent validation. No public profile provides an approval decision.

The helper is deliberately not a general-purpose MCP SDK: fixed public endpoint, JSON response transport, two read-only tools, 30-second network timeout, no authentication, no uploads, and no automatic pagination or retries. It returns data without interpreting profile prose or executing it.
