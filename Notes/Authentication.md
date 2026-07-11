---
aliases: []
tags:
  - linker-exclude
---

# Authentication

**Authentication serves as the critical security and access gateway for the Ravelry API**, carefully balancing the platform's desire to support a vast ecosystem of third-party applications with the need to protect sensitive user data and commercial infrastructure. To manage this, developers must provision credentials through the Ravelry Pro portal.

Depending on the application's goals, the API relies on two primary architectural models for authentication: **Basic Authentication** (for personal and read-only scripts) and **OAuth** (for distributed, multi-user applications).

## 1. Basic Authentication

Basic Authentication is heavily utilized by data scientists, researchers, and personal project developers who do not need to authenticate multiple external users. The Ravelry API requires that all Basic Auth requests be transmitted over SSL; attempting to use standard HTTP will result in an immediate 403 Forbidden error.

The API splits Basic Authentication into two distinct access levels:

- **Read-Only Access:** This level is used when an application only needs to harvest public data from the global databases (such as pattern metrics or yarn weights). It utilizes the developer's Access Key as the username and the Secret Key as the password. From an engineering perspective, this involves concatenating the username and password with a colon, converting it to a Base64-encoded string, and appending it to the HTTP Authorization header.
- **Personal Account Access:** If a developer is building a tool solely for their own use (such as a personal Notion syncing script or a local MCP server for an AI assistant), they can bypass complex permission scopes. This method uses the developer's Access Key as the username and a dedicated **Personal Key** (distinct from the Secret Key) as the password. This grants the script full, unrestricted access to the developer's personal "Notebook".

In data science ecosystems, such as R, packages like `ravelRy` streamline this process by securely loading credentials directly from `.Renviron` files, mapping `RAVELRY_USERNAME` and `RAVELRY_PASSWORD` environment variables to the API's Basic Auth headers.

## 2. OAuth 2.0 and OAuth 1.0a

For public web and mobile client applications where end-users must securely log into their own Ravelry accounts, the platform requires dynamic OAuth flows to prevent credential exposure.

- **OAuth 2.0:** The primary standard uses a `client_id` and `client_secret` against Ravelry's authorization and token endpoints. Because Ravelry does not support "Out-of-Band" (OOB) authorization, third-party apps must define a callback URL or internal app scheme to catch the token redirects. Tokens generated via OAuth 2.0 expire in 24 hours, requiring developers to request the `offline` scope to receive a refresh token.
- **OAuth 2.0 Security Constraint:** A critical, often undocumented security validator in Ravelry's OAuth 2.0 gateway is the `state` parameter. Developers must pass a secure, random string that is strictly **greater than eight characters in length**. Submitting a state string shorter than this will result in an immediate authorization failure.
- **OAuth 1.0a:** The API also maintains support for OAuth 1.0a, which relies on a consumer key and consumer secret. Unlike OAuth 2.0, these tokens are long-lived, though they can still expire after periods of inactivity or if a user manually revokes access.

## 3. Authentication Scopes and Permissions

While Personal Basic Auth automatically grants full access to an account, distributed OAuth applications must explicitly request permission scopes to interact with protected user content. This ensures applications only have the exact access they need. Key authorization scopes include:

- **Social & Communication:** `forum-write` (to create, edit, or delete forum posts) and `message-write` (to send and delete direct private messages).
- **Commerce & Pattern Stores:** Independent designers and local yarn shops require specific scopes like `patternstore-read` (to enumerate their products) and `patternstore-pdf` (to generate secure download links for their digital files).
- **Library Access:** The `library-pdf` scope allows applications to directly download PDFs from a user's digital library. Because this involves copyrighted material, tokens requesting this scope expire much faster than standard tokens and may be revoked if rate limits are exceeded.
- **Minimal Scopes:** To protect user privacy, developers can request restricted scopes like `profile-only` (which strictly limits access to the `/current_user.json` endpoint) or `carts-only` (which allows external pattern websites to process checkouts without gaining access to the user's personal messages or stashes).

## 4. Common Troubleshooting and Authentication Errors

When building programmatic crawlers, developers must handle several common authentication pitfalls:

- **Token Expiration (401 Unauthorized):** Because OAuth tokens expire, the API will return standard HTTP 401 Unauthorized errors. Ravelry's documentation specifies that applications must be engineered to catch these 401 responses and automatically re-authenticate the user or utilize a refresh token.
- **Cryptic 500 Internal Server Errors:** A highly common point of failure occurs when developers initially configure their Basic Authentication credentials in local text files (such as passing a `user_rav.txt` file in R scripts). If there are typos in the column headers or formatting misalignments in the credentials, Ravelry's server parsing engine crashes. This generates a misleading **500 Internal Server Error** instead of the expected 401 Unauthorized error, which frequently confuses developers attempting to debug their connection.
