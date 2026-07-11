**Brands and Shops function as the real-world commercial anchors of the Ravelry Yarn Database**, bridging the gap between abstract fiber classification and physical retail ecosystems. While the core Yarn Database catalogs the physical properties of fibers, the Ravelry API treats the creators (Brands/Yarn Companies) and the distributors (Shops) as robust, independent data entities that power geographic discovery and inventory tracking.

Here is how the sources describe Brands and Shops within the larger context of the Yarn Database and platform features:

### 1. Yarn Companies (Brands) as Taxonomic Parent Entities

In the Ravelry API, brands are classified as **`YarnCompany`** objects. Rather than just being a text label attached to a ball of yarn, these companies are treated as distinct entities that can be searched and analyzed on their own.

- **Search and Discovery:** Developers can query the `/yarn_companies/search.json` endpoint to browse the directory of manufacturers and independent dyers. Third-party tools, such as the `ravelRy` package for R, feature dedicated functions like `search_yarn_companies()` to easily pull this data for analysis.
- **Company Portfolios:** When querying a `YarnCompany`, the API returns descriptive corporate metadata, including the company's `url`, their `logo_url`, and a critical `yarns_count` metric that reveals the total number of distinct yarn lines they produce.
- **Nested Payload Integration:** Within the core Yarn Database, the relationship is bidirectional. When retrieving a specific `Yarn` object, the full payload inherently includes the `yarn_company_name` and the complete nested `YarnCompany` profile, ensuring that applications always have the manufacturer's context when displaying a yarn.

### 2. Shop Discovery and Geographic Filtering

Ravelry maintains an extensive directory of retail locations where crafters can purchase yarn. The API exposes this through a highly specialized shop locator endpoint (`/shops/search.json`), which serves as a powerful tool for third-party mobile applications designed for crafters on the go.

- **Geographical Querying:** Developers can perform location-based searches by passing exact `lat` (latitude), `lng` (longitude), and `radius` parameters (configured in either `miles` or `km`) to find nearby stores.
- **Local Yarn Store (LYS) Filtering:** A standout feature of the API is its ability to distinguish between independent small businesses and large corporate chains. By passing the parameter `shop_type_id = 1`, developers can explicitly restrict search results to "Local Yarn Stores," filtering out big-box retailers like Wal-Mart or Michael's.
- **Rich Retail Metadata:** When a **`Shop`** object is retrieved, it returns a massive array of practical information for brick-and-mortar shoppers. The payload includes exact `latitude`/`longitude` coordinates, hours of operation (`ShopSchedule`), contact information (`shop_email`, `phone`), and accessibility indicators like `wheelchair_access`, `parking`, `free_wifi`, and `seating`. It also lists the specific `yarn_brands` that the store is known to carry.

### 3. Tying Inventory to Provenance (Stash and Packs)

Brands and Shops are deeply integrated into the user's personal "Notebook," specifically within their Stash and Project records. The API tracks not just what yarn a user owns, but _where_ it came from.

- **Material Allocations (Packs):** When a user allocates yarn to a project (a `Pack` object), the API allows them to record granular purchase provenance. A `Pack` tracks the `shop_id` and `shop_name` to explicitly record where the yarn was acquired. If the item was purchased outside of a registered shop, users can log custom metadata like `purchased_city`, `purchased_country_id`, and `purchased_date`.
- **Financial Tracking:** These inventory records also allow users to track the financial investment in their craft, logging the `total_paid` and the `total_paid_currency` for the yarn they sourced from these shops and brands.

### 4. Retail Synergies: The In-Store Sales Program

Beyond just acting as a directory for yarn, the API directly integrates Local Yarn Shops into Ravelry's digital commerce infrastructure for pattern distribution.

- Through the `/in_store_sales/…` endpoints, participating brick-and-mortar shops can act as retail vendors for independent pattern designers. If a customer is buying yarn for a project in a physical store, the shop can use the API to process a pattern purchase at the register.
- The API handles the transaction by creating a cart, adding the wholesale price of the digital pattern to the shop's monthly Ravelry bill, and delivering the PDF directly to the customer's email or Ravelry library, effectively blending physical yarn retail with digital pattern distribution.