Within the Ravelry API’s Yarn Database, **Fiber Composition is treated as a highly structured, quantitative data model rather than a simple descriptive text string**. Because the specific materials used in a yarn—such as wool, cotton, or nylon—drastically alter how a garment drapes, washes, and feels, the API breaks down fiber composition into granular, queryable objects.

In the larger context of the Yarn Database, the sources detail how fiber composition is structured, classified, and utilized:

### 1. The `YarnFiber` Model and Blend Percentages

When an application retrieves a full `Yarn` payload from the database, the exact material makeup is exposed through a nested array called `yarn_fibers`. Instead of returning a flat text string like "80% Wool, 20% Nylon," the API separates the materials mathematically.

- Each item in this array is a distinct **`YarnFiber`** object, which explicitly tracks the `percentage` (as an integer) of that specific material within the overall blend.
- This structured breakdown allows third-party tools to programmatically calculate material requirements or filter search results based on precise blend thresholds.

### 2. Biological and Chemical Classification (`FiberType`)

Nested within the `YarnFiber` payload is the **`FiberType`** object, which defines the physical and scientific nature of the material.

- This object goes beyond simply naming the material; it utilizes precise boolean flags to categorize the fiber's overarching biological or chemical origin.
- The API explicitly flags whether a component is an `animal_fiber`, a `vegetable_fiber`, or `synthetic`. This allows applications to easily filter out synthetic materials for eco-conscious crafters, or filter out animal fibers for vegan crafters or those with wool allergies.

### 3. Standardized Global Taxonomies

To maintain consistency across hundreds of thousands of yarns, Ravelry organizes fiber composition using global taxonomies. The API exposes specific master-list endpoints, such as `/fiber_categories.json` and `/fiber_attributes.json`, to retrieve these standardized classifications.

- **Hierarchical Categories:** The `FiberCategory` object is structured hierarchically. It includes properties for the parent category and an array of `children` categories, allowing applications to drill down from broad fiber families into highly specific material sub-types.
- **Caching Infrastructure:** Because these foundational fiber taxonomies rarely change, Ravelry's official API documentation explicitly advises developers to cache the attribute and category lists locally for up to 24 hours to optimize application performance and save bandwidth.

### 4. Integration with Personal "Notebooks" (`FiberStash`)

The API's fiber architecture directly supports the personal organizational tools of crafters—particularly spinners and dyers who work with raw, unspun materials.

- **Dedicated Fiber Tracking:** The API provides a distinct **`FiberStash`** object for users to track their unspun inventory. Just like standard yarn stashes, users can log the fiber company's name, the dye lot, add personal notes, and attach photos to their fiber stash entries.
- **Unified Inventories:** To make mobile app development easier, the API includes a unified endpoint (`/stash/unified/list.json`) that seamlessly combines a user's standard milled yarn stash with their unspun fiber stash, returning both `Stash` and `FiberStash` objects in a single list.

### 5. Data Science and Behavioral Analytics

Because fiber composition data is so deeply nested within yarn and pattern payloads (often found inside the `packs` array that dictates pattern requirements), developers and researchers frequently build custom scripts to extract it.

- For example, third-party Python synchronization scripts like _Knotion_ utilize dedicated parsing routines to map these nested fiber components directly into flat, relational databases.
- Once extracted, data scientists use this compositional data to model crafter behaviors, analyzing individual preferences for specific fiber crafts or garment materials to build sophisticated yarn recommendation engines.