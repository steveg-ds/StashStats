In the Ravelry API ecosystem, Designer Information is fundamentally intertwined with Pattern Data. Designers (technically defined in the API as **`PatternAuthor`** objects) are the creators of the platform's core commodity, and their data acts as a vital relational bridge connecting abstract crafting designs to the social and commercial layers of the platform.

Here is how the sources describe Designer Information within the larger context of Pattern Data:

### 1. Nested Identity Within Pattern Payloads

When a developer or application queries the API for a specific knitting or crochet design, the designer's identity is not a separate query, but rather a deeply nested component of the `Pattern` object itself.

- **The `PatternAuthor` Object:** Within a pattern's payload, the designer's information is found under keys like `pattern_author` or `designer`. This object contains the designer's full name or alias (e.g., accessed via `patterns.pattern_author.name`).
- External R packages, such as `ravelRy`, parse this deeply nested JSON so that when a user runs a function like `get_patterns()`, the resulting data frame automatically includes a list-column for the `pattern_author`, allowing researchers to easily map which designers created which patterns.

### 2. Comprehensive Designer Portfolios and Metrics

Beyond simply naming the creator, the API treats designers as distinct, queryable entities with their own metrics. Developers can use specific endpoints—like `/designers/{id}.json` or the `get_designer()` function in R—to retrieve a complete profile.

- **Craft-Specific Statistics:** The `PatternAuthor` payload calculates and exposes the designer's total body of work, providing an overall `patterns_count` alongside highly specific metrics like their `knitting_pattern_count` and `crochet_pattern_count`.
- **Community Popularity:** The API also returns a `favorites_count` for the designer, aggregating how many times the Ravelry community has bookmarked or favorited their specific profile.
- **Featured Bundles:** When querying a designer's profile, developers can pass an `include=featured_bundles` parameter to simultaneously retrieve curated collections of patterns that the designer has chosen to highlight to the public.

### 3. The Bridge Between "User" and "Designer"

Because Ravelry is a social network, the API must manage the distinction between a person's everyday user account and their professional designer identity.

- **Bidirectional Linking:** The data model handles this by linking the two entities bidirectionally. A `PatternAuthor` object contains an array of `users`, representing the standard Ravelry user accounts associated with that designer profile. Conversely, when querying a full `User` profile, the payload includes a `pattern_author` property that links the user back to their professional designer identity.
- **Fallback Metadata:** To ensure designer profiles always have context, the API uses a fallback mechanism. If a designer has not filled out dedicated profile notes for their `PatternAuthor` page, the API will automatically substitute and display the "blurb" from their standard user profile.

### 4. Advanced Pattern Discovery via Designer Identity

Designer information is highly integrated into Ravelry's advanced pattern search engine. Because patterns are strictly tethered to their authors, applications can use designer data as powerful search filters.

- When utilizing the `/patterns/search.json` endpoint, developers can filter the global database of hundreds of thousands of patterns to find specific portfolios. The API documentation recommends using the `designer-link` parameter (passing the designer's permalink) or the `designs-by` parameter (passing the designer's exact name) to isolate search results to a single creator.

### 5. Designer Publishing and Commercial Infrastructure

In the background of the public Pattern Data, Designer Information is also tied to Ravelry's commercial publishing tools, often referred to as "Pro Accounts" or "Businesses."

- **Drafting Patterns:** Before a pattern becomes public, designers use the API to create `DraftPattern` objects. These drafts contain properties like `draft_pattern_author_name` and must be explicitly linked to a designer's `business_id` (their professional account).
- **Pattern Stores:** Designers manage the monetization of their patterns through the `/stores/…` endpoints. The API allows designers to list the pattern stores they administer, retrieve active products within those stores, and export granular transaction histories (`/stores/:id/purchases.json`) for the patterns they have sold.