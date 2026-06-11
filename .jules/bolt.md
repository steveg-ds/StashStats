## 2026-06-11 - [N+1 Query & O(N²) Search Optimization]
**Learning:** Stash enrichment logic was performing individual SQLite queries for every item in the user's stash list and using nested loops for data mapping, leading to significant latency as the stash size grew.
**Action:** Implement batch database retrieval methods using the SQL `IN` clause and utilize dictionary-based lookups (`stash_map`) to transform O(N^2) operations into O(N).
