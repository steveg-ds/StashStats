## 2026-06-10 - [Parallel API Calls and Analytics Memoization]
**Learning:** Sequential N+1 API calls for search results were the primary bottleneck. Parallelizing with `ThreadPoolExecutor` provided a ~79% speedup. Also, Pydantic private attributes must be handled carefully when used for instance-level caching.
**Action:** Use `ThreadPoolExecutor` for batch API requests. For caching in Pydantic models, use `Field(default_factory=dict, init=False, exclude=True)`.
