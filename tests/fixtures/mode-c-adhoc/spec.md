# API Contract: POST /api/v1/comments

- `body` field is required, must be a string.
- `body` must be at most 200 characters. Requests exceeding this must be rejected
  with HTTP 400 and an error message identifying the field.
- `body` must not be empty or whitespace-only; reject with HTTP 400.
- Response on success: HTTP 201 with the created comment JSON.
