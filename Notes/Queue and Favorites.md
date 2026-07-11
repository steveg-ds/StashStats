Within the Ravelry API’s ecosystem of User Content, **Queue and Favorites** serve as the primary curation and future-planning engines of the "Personal Notebook." While Projects and Stash represent a crafter's active execution and physical inventory, the Queue and Favorites endpoints manage their intent, inspiration, and personal organization.

In the larger context of User Content, the API treats these features as highly relational data models that bridge a user's personal desires with Ravelry's master databases of patterns, yarns, and community posts.

Here is how the sources describe the Queue and Favorites within the Ravelry API:

### 1. The Queue: Planning Future User Content

The Queue allows crafters to digitally organize their upcoming projects. The API manages this through the **`QueuedProject`** object, which acts as a structured blueprint for future crafting.

- **Structured Intent:** A minimal queue entry only requires a `pattern_id` and a `sort_order` to establish its place in the list. However, the data model supports rich personal metadata, allowing users to log who they are making the item for (`make_for`), their personal `notes`, a target `finish_by` date, and the specific `skeins` or quantity of yarn they anticipate needing.
- **Inventory Integration:** The Queue is explicitly linked to the user's personal material tracking. The API allows a `QueuedProject` to be tethered to specific `stash_ids` or `fiber_stash_ids`, meaning users can electronically reserve yarn from their personal stash for a future project before they even begin crafting.
- **Dynamic Ordering:** Because crafters constantly shift their priorities, the API features dedicated endpoints (such as `/queue/order` and `/queue/{id}/reposition`) that allow third-party tools to dynamically move a queued project to a new position in the list.

### 2. Favorites & Bundles: Curating the Platform

Favorites (technically referred to in the API as **`Bookmark`** objects) allow users to curate the massive amount of content generated on Ravelry into their personal Notebook.

- **Omnivorous Bookmarking:** Unlike the Queue, which is strictly for patterns or project ideas, the API allows a user to favorite virtually any entity on the platform. The `Bookmark` object requires a `type` parameter, which can designate the saved item as a `project`, `pattern`, `yarn`, `stash`, `forumpost`, `designer`, `yarnbrand`, or `yarnshop`.
- **Personal Enrichment:** When a user favorites an item, the API does not just save a simple hyperlink. It creates a personalized record where the user can attach their own `comment` and a space-delimited `tag_list` to categorize the bookmark.
- **Bundles:** Because a user's favorites can grow to unmanageable sizes, the API supports hierarchical organization through **`Bundle`** objects. Users can create curated collections (e.g., "Sweaters for Winter") and use the API's `/favorites/{id}/add_to_bundle` or `remove_from_bundle` endpoints to group their bookmarks together. A bundle can also feature its own cover photo, notes, and specific sorting.

### 3. Powering Mobile Utility and Browser Extensions

Because Ravelry relies on third-party developers for mobile experiences, Queue and Favorites are critical endpoints for crafting "on-the-go" utility.

- **Mobile Yarn Shopping:** Mobile apps like _Ravulous_ and _Wooly_ specifically leverage the Queue API to give users pocket-access to their future plans. When standing in a physical yarn store, a user can pull up their queued projects to immediately see the recommended yarn and exact yardages required, preventing them from under-buying or over-buying materials.
- **Browser Integrations:** Ravelry provides an "Add to Queue" browser bookmarklet. This allows users browsing external, non-Ravelry websites to push a pattern they find out on the web directly into their Ravelry API queue structure.

### 4. Injecting Personal Content into Global Discovery

Within the Ravelry API, a user's Queue and Favorites do not merely sit passively in their Notebook; they dynamically alter how that user interacts with global data.

- **Contextual Search:** When a developer queries the global `/patterns/search.json` or `/yarns/search.json` endpoints, they can pass a `personal_attributes=1` flag. This injects a special hash into the global search results that reveals if the authenticated user has already queued or favorited those specific master items.
- **Community Metrics:** User curation directly drives the platform's overall statistics. Master `Pattern` and `Yarn` objects natively return a `favorites_count` and `queued_projects_count`, aggregating the collective intent of the entire community. Designers and yarn companies also possess a `favorites_count`, which acts as a metric of their popularity.
- **Social Broadcasting:** A user's curation habits feed directly into the platform's social network. The API's `/friends/activity` endpoint (and the associated RSS feeds) streams updates to a user's friend group whenever they queue a new pattern or add a new favorite, driving community inspiration.