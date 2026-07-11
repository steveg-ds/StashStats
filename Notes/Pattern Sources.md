**Pattern Sources** serve as the vital publishing containers for the Ravelry platform’s massive repository of Pattern Data. While a "Pattern" represents the technical specifications of a single design, a "Pattern Source" represents the physical or digital publication—such as a book, magazine, booklet, or website—where that design was originally published or compiled.

In the larger context of the Ravelry API, Pattern Sources function as parent entities that group individual patterns together, bridging the gap between isolated crafting instructions and real-world publishing and commerce.

Here is how the sources describe Pattern Sources within the Ravelry ecosystem:

### 1. The Relational Bridge Between Designs and Publications

The API relies on a complex, many-to-many relationship between individual patterns and their sources, as a single design might be published in a standalone PDF, later compiled into a magazine, and eventually published in a hardcover book.

- **Bottom-Up View:** When developers retrieve a full `Pattern` object payload, the data includes a nested `pattern_sources` array, allowing applications to see exactly which publications feature that specific design.
- **Top-Down View:** Conversely, developers can query a specific publication using the `/pattern_sources/{id}/patterns.json` endpoint. This call retrieves the entire "set of patterns that a given source contains," allowing apps to display all the designs featured in a single magazine or book.

### 2. Source-Specific Metadata

Because Pattern Sources represent publications rather than crafting instructions, the `PatternSource` object has a distinct metadata model focused on publishing and retail details.

- **Publication Details:** A source payload includes the publication's name, author, issue number, publisher ID, publication date, and a boolean flag indicating if the publication is `out_of_print`.
- **Retail and Visuals:** The API tracks the publication's `list_price` and includes direct integrations for `amazon_url` and `amazon_rating` data. To recreate the feeling of a physical bookshelf in third-party apps, the payload also returns a `shelf_image_path` to display the book or magazine's cover art.
- **Taxonomy:** Sources are classified by a `PatternSourceType` object, which defines whether the source is a book, magazine, or website. This object includes system flags like `requires_url` and `can_add_to_library`, which tell the API how to handle the source.

### 3. Integration with the User's "Library"

Pattern Sources are deeply integrated into the user's "Notebook", specifically within their digital and physical pattern Library.

- **Volumes:** When a user logs a book or magazine they own, the API creates a `Volume` object in their library. Developers can use the `/volumes/create.json` endpoint to add items to a user's library by submitting either a single `pattern_id` or an entire `pattern_source_id`.
- **Library Search:** External apps can query a user's library to specifically filter for owned pattern sources by passing `type` parameters like `book`, `magazine`, or `booklet`.

### 4. Commercial Infrastructure and Sales

Beyond organization, Pattern Sources act as major commodities within Ravelry's commercial infrastructure for designers and sellers.

- **Products and Saleables:** When a designer lists an item for sale in their Ravelry store, the API creates a `Product` object. A backend `Saleable` record connects this retail product to its descriptive page—which can be either a single `Pattern` or an entire `PatternSource`.
- **Creating Source Products:** Through the `/products/create.json` endpoint, a designer or store owner can generate a new commercial product by passing a `pattern_source_id`, allowing them to sell an entire digital eBook or magazine collection in a single transaction.
- **Deliveries:** When a user purchases a digital good, the API creates a `Delivery` record. The documentation notes that these delivered products may be associated with entire pattern sources, securely distributing multiple nested pattern PDFs at once.

### 5. Dedicated Discovery

Because Pattern Sources are independent entities, they feature their own dedicated search engine. Developers can query the `/pattern_sources/search.json` endpoint to browse the entire database of publications. Ravelry's API documentation notes that alongside standard full-text searches, developers can pinpoint exact physical books by passing specific parameters like an `isbn` directly into the query.