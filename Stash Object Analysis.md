# Ravelry Stash Object Data Analysis Report

This report analyzes the structured data payloads returned by the Ravelry API when working with stash objects. It details the properties stored in each layout of a Stash record (creation, details page/show, and updating).

## 1. Stash Creation Response Structure

When sending a POST request to `/people/{username}/stash/create.json` (e.g., creating a stash with yarn ID `4031` and dye lot `CURL-1`), the API returns a structured JSON payload containing a `stash` object.

### Key Data Fields
- **Metadata**:
  - `id`: The unique integer identifying this specific user stash entry (e.g., `33105850`).
  - `created_at` / `updated_at`: Timestamp strings in the format `YYYY/MM/DD HH:MM:SS -Zone`.
  - `user_id`: Integer representing the owner.
  - `permalink`: String slug based on the yarn name.
- **User Attributes**:
  - `dye_lot`: User-provided string detailing the dye lot.
  - `location`: Free-text string noting where the user stores this stash item.
  - `notes` / `notes_html`: Detailed description and markdown/HTML rendered user notes.
- **Relationships**:
  - `stash_status`: An object detailing status e.g. `{"id": 1, "name": "In stash"}`.
  - `yarn`: The full parent yarn model schema containing availability, weight description (`yarn_weight_name`), fiber breakdowns (`yarn_fibers`), care/manufacturing attributes (`yarn_attributes`), origin countries (`yarn_provenance`), and images/media links (`photos`).
  - `packs`: An array containing details of yarn packs/skeins allocations. Each pack object stores:
    - `skeins`: Number of skeins owned.
    - `dye_lot`: Dye lot matching the main record.
    - `grams_per_skein` / `yards_per_skein` / `meters_per_skein`: Specific measurements derived from the parent yarn or overwritten by the user.

---

## 2. Stash Update & Mutation Behavior

When submitting updates via POST to `/people/{username}/stash/{id}.json`, properties are modified.

### Mutation Analysis
- **`updated_at`**: Moves to the timestamp of the patch operation.
- **`location` / `notes`**: Replaced with user's new inputs (e.g., location changes from `"Box"` to `"Closet Box 3"`).
- **`notes_html`**: Automatically regenerated and wrapped in HTML paragraphs (e.g., `\n<p>CURL update notes</p>\n`).
- **Stable References**: Core identifiers (`id`, `user_id`, `created_at`) and nested `yarn` parameters remain unchanged.

---

## 3. Detailed Payload Schema Comparison

| Schema Group | Field Name | Type | Description |
|---|---|---|---|
| **Root Stash** | `id` | `Integer` | Stash ID |
| | `name` | `String` | Calculated item name e.g. "Cascade Yarns ® Magnum" |
| | `location` | `String` | Custom physical storage location |
| | `notes` | `String` | Text notes |
| | `stash_status` | `Object` | Status status dictionary (ID and Name) |
| **Parent Yarn**| `id` | `Integer` | Raw Ravelry Yarn ID |
| | `discontinued` | `Boolean` | Discontinuation status |
| | `yarn_fibers` | `Array` | Percentage allocation of fibers (e.g., 100% Wool) |
| **Packs** | `skeins` | `Float` | Quantity of skeins owned |
| | `dye_lot` | `String` | Product dye lot |
| | `grams_per_skein`| `Integer` | Individual weight representation |