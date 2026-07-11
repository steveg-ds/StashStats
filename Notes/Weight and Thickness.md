Within the Ravelry API’s Yarn Database, Weight and Thickness are not treated as simple descriptive text strings, but rather as standardized, quantifiable data models that bridge the gap between physical fiber and digital classification. Because the thickness of a yarn dictates the entire mathematical foundation of a knitting or crochet pattern, the API relies on a dedicated global taxonomy to track and standardize these metrics across hundreds of thousands of materials.

Here is how the sources describe Weight and Thickness in the larger context of the Yarn Database:

### 1. The Standardized `YarnWeight` Taxonomy

To maintain consistency across its massive database, Ravelry categorizes all yarn thicknesses into standard metric classifications. Developers can access this master list via the `/yarn_weights.json` endpoint, which retrieves all of the active yarn weights currently recognized by the platform.

When the API returns a **`YarnWeight`** object, it provides highly specific technical measurements that define the physical thickness of the fiber:

- **Physical Density:** The object includes physical measurements like `wpi` (wraps per inch) and the number of strands or `ply` that make up the yarn.
- **Standardized Gauges:** It establishes the baseline mathematical constraints for crafting with that thickness, returning exact fields for `knit_gauge`, `crochet_gauge`, `min_gauge`, and `max_gauge`.

### 2. Integration Across Yarns and Patterns

This underlying taxonomy is deeply integrated into both the Yarn and Pattern databases, acting as a relational bridge between the raw material and the instructional design.

- **Yarn Payloads:** When an application queries a specific yarn from the database, the full payload includes the associated `YarnWeight` object, embedding these standardized metrics directly into the yarn's profile.
- **Pattern Specifications:** Similarly, when querying pattern data, the API returns a `yarn_weight_id` and a `yarn_weight_description` to explicitly define the thickness of the yarn required to achieve the design's intended fit and gauge.

### 3. Personalization within "The Notebook"

The API also accounts for the reality that crafters often use handspun yarn or materials that are not officially indexed in the global database. Within a user's personal "Stash," the platform adapts weight and thickness data to accommodate user modifications:

- **Inventory Tracking:** Stash records return the official `yarn_weight_name` as well as a `long_yarn_weight_name` to describe the stored yarn's thickness.
- **Custom Weights:** If a user logs a custom or handspun yarn, the API utilizes a `personal_yarn_weight` attribute. This field accepts a standardized `YarnWeight` object, allowing the user's custom inventory to remain structurally consistent with the rest of the database's gauge and yardage calculations.

### 4. Data Science and Behavioral Analytics

Because Ravelry's yarn weight data is strictly categorized, it is a highly valuable resource for data scientists analyzing crafter behavior. Official third-party libraries, such as the `ravelRy` wrapper for the R programming language, fully support the `yarn_weights` endpoint out of the box.

Researchers use this accessible data to extract insights from the platform. For example, data scientists utilizing R and Python alongside the API have modeled users' "Queue" histories to map changing preferences in yarn thickness over time. In one documented case study, researchers were able to programmatically determine that a specific user was shifting away from "fingering weight yarn" (a very thin yarn) and was instead actively queuing projects that required thicker "lace and DK weight" yarns. This granular weight data was subsequently used to formulate accurate real-world retail recommendations and gift purchases.