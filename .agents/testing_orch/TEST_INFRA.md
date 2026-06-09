# E2E Test Infra: StashStats

## Test Philosophy
- Opaque-box, requirement-driven. No dependency on implementation design.
- Methodology: Category-Partition + BVA + Pairwise + Workload Testing.

## Feature Inventory
| # | Feature | Source (requirement) | Tier 1 | Tier 2 | Tier 3 |
|---|---------|---------------------|:------:|:------:|:------:|
| F1 | SQLite Database Engine | ORIGINAL_REQUEST R1 | 5 | 5 | ✓ |
| F2 | RAVELRY_USERNAME Config | ORIGINAL_REQUEST R2 | 5 | 5 | ✓ |
| F3 | Analytics Tab Fix | ORIGINAL_REQUEST R3 | 5 | 5 | ✓ |
| F4 | Debounce Input | ORIGINAL_REQUEST R4 | 5 | 5 | ✓ |
| F5 | Redis Caching | ORIGINAL_REQUEST R5 | 5 | 5 | ✓ |
| F6 | Date Pickers UI | ORIGINAL_REQUEST R6 | 5 | 5 | ✓ |
| F7 | Docker Image Optimization | ORIGINAL_REQUEST R7 | 5 | 5 | ✓ |

## Test Architecture
- **Test Runner**: Pytest and Playwright
- **Invocation**: `pytest tests/test_new_e2e.py` or `pytest -k "test_name"`
- **Directory Layout**:
  - `tests/test_new_e2e.py` — contains all new test cases across Tiers 1-4.
  - `.agents/testing_orch/TEST_INFRA.md` — this test design.

---

## Detailed Test Cases Design

### Tier 1 - Feature Coverage (5 per feature = 35 total)

#### F1. SQLite Database Engine
1. **test_sqlite_file_exists**: After first load, verify the SQLite DB file is created at `SQLITE_DB_PATH` or the default `/app/data/stash.db`.
2. **test_sqlite_journal_mode**: Query SQLite database connection pragmas to confirm journal_mode is WAL.
3. **test_sqlite_schema_original_values**: Verify schema of `original_values` table (columns: `stash_id`, `yards`, `meters`, `skeins`, `grams`, `created_at`).
4. **test_sqlite_schema_stash_history**: Verify schema of `stash_history` table (columns: `id` (INTEGER PRIMARY KEY AUTOINCREMENT), `stash_id`, `event_date`, `yards`, `meters`, `skeins`, `grams`, `created_at`).
5. **test_sqlite_concurrency**: Perform multiple fast reads/writes in threads to verify `check_same_thread=False` prevents crashes.

#### F2. RAVELRY_USERNAME Config
6. **test_env_username_removed**: Scan source code to ensure NO occurrences of `os.getenv("USERNAME")` exist (it must be `RAVELRY_USERNAME`).
7. **test_docker_compose_has_ravelry_username**: Scan `docker-compose.yml` to verify `RAVELRY_USERNAME` env var is defined.
8. **test_env_example_has_ravelry_username**: Scan `.env.example` to verify it has `RAVELRY_USERNAME` and no `USERNAME`.
9. **test_default_username_fallback**: If `RAVELRY_USERNAME` is unset, ensure the system defaults to `"KMLadyBugCrotchets"`.
10. **test_custom_username_in_api_calls**: If `RAVELRY_USERNAME` is set to a custom value (e.g. `"TestUser"`), verify the API calls use that custom value in the URL path.

#### F3. Analytics Tab Fix
11. **test_analytics_initial_render**: Switch to Analytics tab; verify that the graph (Plotly element) renders immediately without requiring selector changes.
12. **test_analytics_tab_switch_preserves_dropdown**: Confirm dropdown `analytics-metric-selector` is present when tab is switched.
13. **test_analytics_metrics_dropdown_interaction**: Change dropdown to "Yards" and confirm the graph updates correctly.
14. **test_analytics_metrics_dropdown_skeins**: Change dropdown to "Skeins" and confirm the graph updates correctly.
15. **test_analytics_layout_structure**: Verify that the Analytics tab layout div exists and has the expected classes.

#### F4. Debounce Input
16. **test_debounce_search_input_attr**: Inspect `#stash-search-query` or corresponding query element to verify the `debounce=True` attribute is set.
17. **test_debounce_single_keystroke**: Type 1 character; confirm no request goes out immediately until Enter is pressed or focus is lost.
18. **test_debounce_rapid_typing**: Type 5 characters rapidly; verify only 1 API call / callback is triggered.
19. **test_debounce_no_page_reset**: Verify accordion state doesn't reset after typing each character before debounce threshold.
20. **test_debounce_empty_query**: Empty the search input; verify no call is sent until debounce completes or Enter is pressed.

#### F5. Redis Caching
21. **test_cache_get_full_yarn**: Retrieve yarn info twice; check that second call does not call Ravelry API (mocked) and has a TTL of 24h.
22. **test_cache_get_project_map**: Retrieve project map twice; verify cache hit and TTL of 10 minutes.
23. **test_cache_get_stash_list**: Retrieve stash list twice; verify cache hit and TTL of 5 minutes.
24. **test_cache_invalidation_on_update**: Retrieve stash list, update a stash item, and verify stash list cache is invalidated (next call must fetch fresh).
25. **test_cache_keys_format**: Inspect Redis keys to verify formats `yarn:{yarn_id}`, `proj_map:{username}`, and `stash_list:{username}`.

#### F6. Date Pickers UI
26. **test_date_picker_stash_add_default**: Stash-add form contains a DatePickerSingle default-valued to today's date in YYYY-MM-DD.
27. **test_date_picker_stash_add_id_pattern**: DatePickerSingle in search results has ID pattern `{"type": "stash-date-added", "index": <yarn_id>}`.
28. **test_date_picker_log_usage_default**: Log Usage modal tab contains a DatePickerSingle default-valued to today's date in YYYY-MM-DD.
29. **test_date_picker_log_usage_id**: Log Usage modal DatePickerSingle has ID `"edit-stash-usage-date"`.
30. **test_date_picker_stash_add_custom_date**: Change DatePickerSingle date in stash-add form to a custom date, submit, and verify `pack.purchased_date` is sent to Ravelry API as the custom date.

#### F7. Docker Image Optimization
31. **test_docker_image_size**: Verify that built `stashstats-web` image size is under 400MB.
32. **test_docker_multi_stage_structure**: Inspect Dockerfile to verify multi-stage build structure (Stage 1 `builder`, Stage 2 `runtime`).
33. **test_docker_no_build_tools_in_runtime**: Inspect final image/Dockerfile to confirm `gcc`, `libpq-dev`, or other build tools are not present in Stage 2.
34. **test_docker_venv_copied**: Verify venv is copied from builder to runtime stage.
35. **test_docker_compose_services_count**: Verify that running compose stack has exactly 2 services (web, cache).

---

### Tier 2 - Boundary & Corner Cases (5 per feature = 35 total)

#### F1. SQLite Database Engine
36. **test_sqlite_escaped_queries**: Save original values containing SQL injection patterns or single quotes; verify no errors and correct retrieval.
37. **test_sqlite_very_large_floats**: Save extremum values for double precision (e.g. 1e308, 0, -1); verify storage and retrieval.
38. **test_sqlite_empty_history**: Retrieve history for a non-existent stash ID; verify it returns an empty list instead of None or error.
39. **test_sqlite_invalid_types**: Attempt to save None/nulls into non-nullable schema columns; verify graceful database failure or input validation.
40. **test_sqlite_locked_retry**: Test database behavior when busy (WAL mode should handle concurrent reads/writes without locked errors).

#### F2. RAVELRY_USERNAME Config
41. **test_username_special_characters**: Verify that user names with special characters (URL encoding) are correctly handled in API path construction.
42. **test_username_empty_env**: If RAVELRY_USERNAME is empty string in env, verify it fallback to default.
43. **test_username_extremely_long**: Verify a very long user name doesn't crash URL generation or overflow buffers.
44. **test_username_spaces**: Verify a user name with leading/trailing spaces is stripped or handled properly.
45. **test_username_numeric**: Verify a numeric-only username is treated as string and functions correctly.

#### F3. Analytics Tab Fix
46. **test_analytics_no_stash_data**: Switch to analytics when stash list is empty; verify graph renders empty/graceful message without crashing.
47. **test_analytics_rapid_tab_switching**: Switch rapidly between search and analytics tabs; verify no race conditions or double renders.
48. **test_analytics_metrics_dropdown_rapid_clicks**: Toggle metrics rapidly; verify only the last selected metric graph renders.
49. **test_analytics_unexpected_api_error**: If stash list API fails with 500, verify analytics tab displays error message instead of blank/loading.
50. **test_analytics_zero_values**: Stashes with zero yards/skeins; verify the graph handles them and is plotted.

#### F4. Debounce Input
51. **test_debounce_extremely_fast_typing**: Type 50 characters in 100ms; verify only 1 callback triggered.
52. **test_debounce_focus_loss**: Type 1 character and click outside; verify callback triggers immediately.
53. **test_debounce_special_keys**: Press Arrow keys, Backspace, or Esc; verify debounce does not trigger redundant queries.
54. **test_debounce_very_long_input**: Paste 1000 characters; verify debounce functions and triggers query with full string.
55. **test_debounce_unicode_characters**: Type emoji or unicode; verify query functions after debounce.

#### F5. Redis Caching
56. **test_cache_redis_offline**: Cache operations fail/timeout if Redis is offline, but the app falls back to direct API calls without crashing.
57. **test_cache_ttl_expiration**: Fetch yarn, wait until TTL expires (simulated/mocked), fetch again; verify new API request is sent.
58. **test_cache_eviction_under_memory_pressure**: Check behavior when cache limits are reached.
59. **test_cache_invalid_json_in_cache**: Put corrupt/invalid JSON in Redis cache; verify application recovers and fetches from API.
60. **test_cache_high_concurrency**: Simulating 10 requests for same yarn_id concurrently; verify cache thundering herd protection (or simple cache-fill).

#### F6. Date Pickers UI
61. **test_date_picker_stash_add_leap_year**: Select February 29 on leap year; verify saved date is correct.
62. **test_date_picker_log_usage_invalid_format**: Manually inputting a bad date string (e.g. "invalid"); verify it rejects or uses fallback/today.
63. **test_date_picker_future_date**: Select future date; verify it is handled correctly by the system.
64. **test_date_picker_past_date**: Select very old date (e.g. 1970-01-01); verify it is saved correctly.
65. **test_date_picker_null_date**: Clear date input; verify default date (today) is sent.

#### F7. Docker Image Optimization
66. **test_docker_stage1_cleanup**: Ensure builder stage files are not present in final runtime filesystem.
67. **test_docker_read_only_root**: Verify runtime image runs fine with read-only root FS (with volumes mounted).
68. **test_docker_missing_data_dir**: Verify that if host volume `./data` is not present, the container auto-creates it or handles it.
69. **test_docker_incorrect_permissions**: Verify permissions of `/app/data/stash.db` allow the app to write.
70. **test_docker_gunicorn_worker_threads**: Verify that Gunicorn is configured with exactly `--workers 1 --threads 4` (or similar) to avoid db lockups.

---

### Tier 3 - Cross-Feature Combinations (7 total)

71. **test_cross_db_date_picker_usage**: Log stash usage using the Log Usage modal DatePicker with a custom date, and check that `stash_history` in SQLite contains the exact date entered.
72. **test_cross_cache_username_change**: Change RAVELRY_USERNAME env var, verify cache key changes (e.g. `stash_list:newuser`), and no cache leak between users.
73. **test_cross_analytics_cache_invalidation**: Update stash usage, causing cache invalidation of `stash_list`, then switch to Analytics and verify the graph immediately reflects the updated data.
74. **test_cross_debounce_api_error_analytics**: Type search query, trigger debounce API call, mock an API error, then switch to Analytics to see if error handling functions correctly.
75. **test_cross_date_picker_empty_cache**: Add a yarn with custom date (F6) when cache is empty (F5); verify it successfully passes the custom date and triggers correct cache invalidation.
76. **test_cross_sqlite_redis_desync**: Verify database updates and cache invalidation are consistent under high frequency updates.
77. **test_cross_docker_env_sqlite_path**: Verify that in the docker compose runtime (F7), the SQLite database is written to the custom path specified in `SQLITE_DB_PATH` (F1).

---

### Tier 4 - Real-World Application Scenarios (5 total)

78. **test_scenario_search_and_stash_new_yarn**:
    - User searches for "Wool".
    - Debounce waits and fetches list.
    - User clicks accordion header of first result.
    - User selects a specific date (today - 2 days) on the DatePicker.
    - User enters 5 skeins, Batch X dyelot, and submits.
    - Verify Ravelry API gets the correct custom date, and database saves original values.
79. **test_scenario_log_usage_and_view_analytics**:
    - User selects an existing stashed yarn.
    - Opens Log Usage modal.
    - Selects a custom date (yesterday).
    - Inputs usage of 2 skeins and submits.
    - Verifies history event is logged in SQLite with yesterday's date.
    - Switches to Analytics tab and verifies the graph displays correct history / total skeins.
80. **test_scenario_caching_and_fast_navigation**:
    - User visits home page, triggering cache load for stash list and projects.
    - User clicks search and then clicks back to stash list.
    - Verify no new API calls are made (all served from Redis cache).
    - User edits a stash item, invalidating cache.
    - User navigates back to list, verifying new API call is made and cache is refilled.
81. **test_scenario_docker_deployment_and_migration**:
    - Deploy container stack with empty `/app/data` volume.
    - Verify app starts, auto-runs migrations on SQLite DB, and is ready on port 8050.
    - Perform a stash add; check SQLite DB contains tables and is in WAL mode.
    - Tear down stack, verify SQLite database is persisted in `./data/stash.db`.
82. **test_scenario_multi_user_isolation**:
    - Change RAVELRY_USERNAME, verify we see that user's stash list, cached separately, and history tracked separately.

---

## Coverage Thresholds
- Tier 1: 35 tests
- Tier 2: 35 tests
- Tier 3: 7 tests
- Tier 4: 5 tests
- **Total: 82 tests**
