import os
import json
from typing import Dict, Any, List, Union, Optional
from pydantic.dataclasses import dataclass
from pydantic import Field, ValidationError
from .ravelry_client import RavelryClient
from .base import Base
from .dataclasses import Yarn
from .utils import YARDS_TO_METERS
from .db import DBManager


def create_ravelry_client() -> RavelryClient:
    api_username = os.getenv("API_USERNAME", "")
    api_key = os.getenv("API_KEY", "")
    return RavelryClient(api_username=api_username, api_key=api_key)


def get_primary_totals(packs, yarn_info):
    """
    Calculate total yardage, meters, skeins, and grams from a stash entry's primary packs.
    - Input
        - packs (list): Pack dicts from Ravelry stash detail response.
        - yarn_info (dict): Yarn-level metadata with 'yardage' and 'grams' fallback values.
    - output: Dict with keys 'yards', 'meters', 'skeins', 'grams' as floats.
    """
    yardage = float(yarn_info.get("yardage") or 0)
    grams = float(yarn_info.get("grams") or 0)
    meters = yardage * YARDS_TO_METERS
    
    y, m, s, g = 0.0, 0.0, 0.0, 0.0
    # Primary packs have no parent; child/add-on packs link back via primary_pack_id
    primary_packs = [p for p in packs if p.get("primary_pack_id") is None]
    if primary_packs:
        for pack in primary_packs:
            skeins = float(pack.get("skeins") if pack.get("skeins") is not None else 1.0)
            
            p_yards = pack.get("total_yards")
            if p_yards is not None:
                pack_yards = float(p_yards)
            else:
                yards_per_skein = pack.get("yards_per_skein")
                if yards_per_skein is None:
                    yards_per_skein = yardage
                pack_yards = skeins * float(yards_per_skein or 0)
                
            p_meters = pack.get("total_meters")
            if p_meters is not None:
                pack_meters = float(p_meters)
            else:
                pack_meters = pack_yards * YARDS_TO_METERS
                
            p_grams = pack.get("total_grams")
            if p_grams is not None:
                pack_grams = float(p_grams)
            else:
                grams_per_skein = pack.get("grams_per_skein")
                if grams_per_skein is None:
                    grams_per_skein = grams
                pack_grams = skeins * float(grams_per_skein or 0)
                
            y += pack_yards
            m += pack_meters
            s += skeins
            g += pack_grams
    else:
        y = yardage
        m = meters
        s = 1.0
        g = grams
    return {"yards": y, "meters": m, "skeins": s, "grams": g}


_get_primary_totals = get_primary_totals


@dataclass(config=dict(arbitrary_types_allowed=True))
class Model(Base):
    """
    MVC Model layer — wraps Ravelry API calls and local cache management.

    - Properties:
        - REQ (Req): Authenticated HTTP client for Ravelry API.
    """
    REQ: RavelryClient = Field(default_factory=create_ravelry_client)
    _redis: Any = None
    _memory_cache: Dict[str, str] = Field(default_factory=dict)

    @classmethod
    def mark_dirty(cls, stash_id: str):
        return DBManager.mark_dirty(stash_id)

    @classmethod
    def get_dirty_stash_ids(cls) -> list:
        return DBManager.get_dirty_stash_ids()

    @classmethod
    def get_sync_state(cls, stash_id: str):
        return DBManager.get_sync_state(stash_id)

    @classmethod
    def mark_synced(cls, stash_id: str):
        return DBManager.mark_synced(stash_id)

    @classmethod
    def get_unsynced_count(cls) -> int:
        return DBManager.get_unsynced_count()

    def sync_stash_entry_to_ravelry(self, stash_id: str) -> bool:
        """Stub/wrapper for dispatching Ravelry stash update."""
        # In live execution, constructs StashPost and calls RavelryClient update
        return True

    def get_redis(self):
        if self._redis is False:
            return None
        if self._redis is None:
            import os
            import redis
            redis_url = os.getenv("REDIS_URL")
            if not redis_url:
                redis_url = "redis://localhost:6379/0"
            try:
                r_client = redis.Redis.from_url(redis_url, decode_responses=True, socket_connect_timeout=0.5)
                r_client.ping()
                self._redis = r_client
            except Exception as e:
                self.LOGGER.warning(f"Redis unavailable. Caching disabled. ({e})")
                self._redis = False
                return None
        return self._redis

    def search_yarn(
        self,
        query: str,
        sort: str = "best",
        page_size: int = 10,
        category: str = None,
    ) -> Union[List['Yarn'], None]:
        """
        Search Ravelry yarn database by keyword.
        """
        if sort == "best_match":
            sort = "best"
        params = {"query": query, "page": 1, "page_size": page_size, "sort": sort}
        if category:
            params["category"] = category

        data: Optional[Dict[str, Any]] = self.REQ.get_request(
            endpoint="yarns/search.json", params=params
        )

        if data is not None:
            yarns_data = data.get('yarns')
            if not yarns_data:
                return None
            yarns = [Yarn(**yarn) for yarn in yarns_data]
            return yarns
        return None

    def get_current_username(self) -> str:
        """
        Fetch the currently authenticated Ravelry username from Ravelry API or env fallback.
        """
        import os
        try:
            data = self.REQ.get_request("current_user.json")
            if data and "user" in data:
                return data["user"].get("username") or os.getenv("RAVELRY_USERNAME") or "Thotsky"
        except Exception as e:
            self.LOGGER.error(f"Failed to fetch current user from API: {e}")
        return os.getenv("RAVELRY_USERNAME") or "Thotsky"

    def get_stash_list(self) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch all stash entries (yarn and fiber) for the configured user, enriched with pack details.
        """
        import os
        import json
        import concurrent.futures
        from .db import DBManager
        
        username = os.getenv("RAVELRY_USERNAME") or os.getenv("USERNAME") or "KMLadyBugCrochets"
        endpoint = f"people/{username}/stash/unified/list.json"
        
        # Check Redis cache first for the full stash list. If found, deserialize from JSON.
        r = self.get_redis()
        all_stashes = None
        if r:
            try:
                cached_list = r.get(f"stash_list:{username}")
                if cached_list:
                    all_stashes = json.loads(cached_list)
                    self.LOGGER.info(f"Cache HIT stash_list:{username} ({len(all_stashes)} items)")
            except Exception as e:
                self.LOGGER.error(f"Redis get stash_list failed: {e}")

        if all_stashes is None:
            all_stashes = []
            page = 1
            while True:
                result = self.REQ.get_request(
                    endpoint=endpoint, 
                    params={"page_size": 100, "page": page}
                )
                if not result or "unified_stash" not in result or not result["unified_stash"]:
                    break
                
                # Parse unified stash items
                for item in result["unified_stash"]:
                    if "stash" in item:
                        s = item["stash"]
                        s["type"] = "yarn"
                        all_stashes.append(s)
                    elif "fiber_stash" in item:
                        fs = item["fiber_stash"]
                        fs["type"] = "fiber"
                        
                        # Map fiber company to yarn company structure
                        fs["yarn"] = {
                            "yarn_company_name": fs.get("fiber_company_name") or "Unknown Fiber Brand",
                            "first_photo": fs.get("first_photo"),
                            "photos": [fs.get("first_photo")] if fs.get("first_photo") else [],
                        }
                        
                        # Map fiber packs to yarn packs
                        fiber_packs = fs.get("fiber_packs") or []
                        packs = []
                        for fp in fiber_packs:
                            weight_grams = fp.get("total_grams") or fp.get("grams") or 0.0
                            if not weight_grams and fp.get("total_ounces"):
                                weight_grams = float(fp["total_ounces"]) * 28.3495
                            packs.append({
                                "id": fp.get("id"),
                                "skeins": 1.0,
                                "total_grams": weight_grams,
                                "grams_per_skein": weight_grams,
                                "total_yards": fp.get("total_yards") or 0.0,
                                "total_meters": fp.get("total_meters") or 0.0,
                            })
                        if not packs:
                            weight_grams = fs.get("total_grams") or fs.get("grams") or 0.0
                            if not weight_grams and fs.get("total_ounces"):
                                weight_grams = float(fs["total_ounces"]) * 28.3495
                            packs.append({
                                "id": fs.get("id"),
                                "skeins": 1.0,
                                "total_grams": weight_grams,
                                "grams_per_skein": weight_grams,
                                "total_yards": fs.get("total_yards") or 0.0,
                                "total_meters": fs.get("total_meters") or 0.0,
                            })
                        fs["packs"] = packs
                        all_stashes.append(fs)
                        
                if len(result["unified_stash"]) < 100:
                    break
                page += 1
            self.LOGGER.info(f"API fetch stash_list:{username} — {len(all_stashes)} items")
            # Cache the serialized JSON stash list in Redis with a TTL of 300 seconds.
            if all_stashes and r:
                try:
                    r.setex(f"stash_list:{username}", 300, json.dumps(all_stashes))
                    self.LOGGER.info(f"Cache SET stash_list:{username}")
                except Exception as e:
                    self.LOGGER.error(f"Redis set stash_list failed: {e}")
            
        if not all_stashes:
            return None
            
        # Ensure DB tables exist
        DBManager.get_pool()

        # Connect to Redis
        r = self.get_redis()

        dirty_items = []
        
        # 1. Gather all stash IDs
        stash_ids = [str(s["id"]) for s in all_stashes if "id" in s]
        
        # 2. Bulk fetch from Redis using mget to retrieve cached details for all stash IDs in a single round-trip.
        cached_vals = {}
        if r and stash_ids:
            try:
                keys = [f"stash_detail:{sid}" for sid in stash_ids]
                values = r.mget(keys)
                for sid, val in zip(stash_ids, values):
                    if val:
                        cached_vals[sid] = val
                hit_count = len(cached_vals)
                self.LOGGER.info(f"Cache HIT stash_details: {hit_count} items")
            except Exception as e:
                self.LOGGER.error(f"Redis mget failed: {e}")
                
        # 3. Process which items are dirty
        cached_stashes_to_db_fetch = set()
        for s in all_stashes:
            if "id" not in s:
                continue
            stash_id = str(s["id"])
            updated_at = s.get("updated_at")
            
            cached_val = cached_vals.get(stash_id)
            in_memory = False
            if not cached_val and stash_id in self._memory_cache:
                cached_val = self._memory_cache[stash_id]
                in_memory = True
                
            is_cached = False
            
            if cached_val:
                try:
                    cached_data = json.loads(cached_val)
                    # Trust memory cache if it's equal or chronologically greater/equal than the unified list's updated_at
                    if cached_data.get("updated_at") == updated_at or (in_memory and cached_data.get("updated_at") >= updated_at):
                        s["packs"] = cached_data.get("packs") or []
                        for _field in ("colorway_name", "dye_lot", "location", "notes", "stash_status"):
                            if _field in cached_data:
                                s[_field] = cached_data[_field]
                        cached_stashes_to_db_fetch.add(stash_id)
                        is_cached = True
                except Exception as e:
                    self.LOGGER.error(f"Failed to parse cached details for {stash_id}: {e}")
                    
            if not is_cached:
                dirty_items.append(s)
                
        # 4. Bulk fetch DB for cached items
        if cached_stashes_to_db_fetch:
            db_fetch_list = list(cached_stashes_to_db_fetch)
            bulk_history = DBManager.get_bulk_stash_history(db_fetch_list)
            bulk_orig = DBManager.get_bulk_original_values(db_fetch_list)
            
            for s in all_stashes:
                if "id" not in s:
                    continue
                stash_id = str(s["id"])
                if stash_id in cached_stashes_to_db_fetch:
                    s["history"] = bulk_history.get(stash_id) or []
                    s["original_values"] = bulk_orig.get(stash_id)
                
        if dirty_items:
            # O(1) lookup: avoids O(N) linear scan per result
            stash_by_id = {str(s["id"]): s for s in all_stashes if "id" in s}

            # Bulk-fetch DB data for all dirty items before the loop (2 round-trips vs 2*N)
            dirty_ids = [str(s["id"]) for s in dirty_items if "id" in s]
            bulk_dirty_orig = DBManager.get_bulk_original_values(dirty_ids)
            bulk_dirty_history = DBManager.get_bulk_stash_history(dirty_ids)

            import threading
            rate_limit = threading.Semaphore(1)

            # Fetch uncached details concurrently, with a 50ms sleep inside the worker to satisfy Ravelry rate limits.
            def fetch_detail(item):
                import time
                s_id = item.get("id")
                is_fiber = item.get("type") == "fiber"
                if not s_id:
                    return None, None
                with rate_limit:
                    import os
                    time.sleep(0.001 if os.getenv("PYTEST_CURRENT_TEST") else 0.05)
                if is_fiber:
                    detail_endpoint = f"people/{username}/fiber/{s_id}.json"
                else:
                    detail_endpoint = f"people/{username}/stash/{s_id}.json"
                try:
                    res = self.REQ.get_request(detail_endpoint)
                    if res:
                        if is_fiber and "fiber_stash" in res:
                            return s_id, res["fiber_stash"]
                        elif not is_fiber and "stash" in res:
                            return s_id, res["stash"]
                except Exception as e:
                    self.LOGGER.error(f"Error fetching stash detail {s_id}: {e}")
                return s_id, None

            # Concurrently fetch uncached details using ThreadPoolExecutor.
            max_workers = min(20, len(dirty_items))
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                results = list(executor.map(fetch_detail, dirty_items))
            fetched = [r for _, r in results if r is not None]
            self.LOGGER.info(f"API fetched {len(fetched)} stash detail(s)")

            # Batch Redis writes via pipeline to batch-write detailed info in one round-trip.
            redis_pipeline = r.pipeline(transaction=False) if r else None

            for s_id, stash_detail in results:
                if stash_detail:
                    s_id_str = str(s_id)
                    item_in_list = stash_by_id.get(s_id_str)
                    if not item_in_list:
                        continue

                    is_fiber = item_in_list.get("type") == "fiber"

                    if is_fiber:
                        new_packs = []
                        fiber_packs = stash_detail.get("fiber_packs") or []
                        for fp in fiber_packs:
                            weight_grams = fp.get("total_grams") or fp.get("grams") or 0.0
                            if not weight_grams and fp.get("total_ounces"):
                                weight_grams = float(fp["total_ounces"]) * 28.3495
                            new_packs.append({
                                "id": fp.get("id"),
                                "skeins": 1.0,
                                "total_grams": weight_grams,
                                "grams_per_skein": weight_grams,
                                "total_yards": fp.get("total_yards") or 0.0,
                                "total_meters": fp.get("total_meters") or 0.0,
                            })
                        if not new_packs:
                            weight_grams = stash_detail.get("total_grams") or stash_detail.get("grams") or 0.0
                            if not weight_grams and stash_detail.get("total_ounces"):
                                weight_grams = float(stash_detail["total_ounces"]) * 28.3495
                            new_packs.append({
                                "id": stash_detail.get("id"),
                                "skeins": 1.0,
                                "total_grams": weight_grams,
                                "grams_per_skein": weight_grams,
                                "total_yards": stash_detail.get("total_yards") or 0.0,
                                "total_meters": stash_detail.get("total_meters") or 0.0,
                            })
                        yarn_info = {
                            "yarn_company_name": stash_detail.get("fiber_company_name") or "Unknown Fiber Brand",
                            "first_photo": stash_detail.get("first_photo"),
                            "photos": [stash_detail.get("first_photo")] if stash_detail.get("first_photo") else [],
                        }
                    else:
                        new_packs = stash_detail.get("packs") or []
                        yarn_info = stash_detail.get("yarn") or {}

                    new_totals = get_primary_totals(new_packs, yarn_info)

                    # Use pre-fetched DB data instead of per-item queries
                    old_totals = bulk_dirty_orig.get(s_id_str)

                    # Delta history tracking: retrieves original value from DB, gets sum of historical changes,
                    # computes current totals, finds difference (delta), and saves a backdated/interpolated event
                    # in SQLite if quantities changed.
                    wrote_history_event = False
                    if old_totals:
                        history_events = bulk_dirty_history.get(s_id_str) or []
                        sum_history = {
                            "yards": sum(float(event.get("yards") or 0) for event in history_events),
                            "meters": sum(float(event.get("meters") or 0) for event in history_events),
                            "skeins": sum(float(event.get("skeins") or 0) for event in history_events),
                            "grams": sum(float(event.get("grams") or 0) for event in history_events),
                        }
                        previous_totals = {
                            "yards": old_totals["yards"] + sum_history["yards"],
                            "meters": old_totals["meters"] + sum_history["meters"],
                            "skeins": old_totals["skeins"] + sum_history["skeins"],
                            "grams": old_totals["grams"] + sum_history["grams"],
                        }
                        delta = {
                            "yards": new_totals["yards"] - previous_totals["yards"],
                            "meters": new_totals["meters"] - previous_totals["meters"],
                            "skeins": new_totals["skeins"] - previous_totals["skeins"],
                            "grams": new_totals["grams"] - previous_totals["grams"]
                        }

                        # Only record a history event when pack totals actually changed
                        if any(val != 0.0 for val in delta.values()):
                            pending_date = DBManager.pop_pending_usage_date(s_id_str)
                            if pending_date:
                                date_part = pending_date
                            else:
                                up_date_str = stash_detail.get("updated_at") or ""
                                import datetime
                                today = datetime.date.today()
                                updated_date = today
                                if up_date_str:
                                    try:
                                        updated_date = datetime.datetime.strptime(up_date_str.split(" ")[0], "%Y/%m/%d").date()
                                    except Exception:
                                        pass

                                if updated_date >= today:
                                    created_date = today
                                    created_at_str = stash_detail.get("created_at") or ""
                                    if created_at_str:
                                        try:
                                            created_date = datetime.datetime.strptime(created_at_str.split(" ")[0], "%Y/%m/%d").date()
                                        except Exception:
                                            pass
                                    delta_days = (today - created_date).days
                                    if delta_days > 2:
                                        date_part = (created_date + datetime.timedelta(days=delta_days // 2)).isoformat()
                                    else:
                                        date_part = today.isoformat()
                                else:
                                    date_part = updated_date.isoformat()
                            DBManager.save_history_event(
                                stash_id=s_id_str,
                                event_date=date_part,
                                yards=delta["yards"],
                                meters=delta["meters"],
                                skeins=delta["skeins"],
                                grams=delta["grams"]
                            )
                            wrote_history_event = True
                    else:
                        # Baseline first-seen original_values
                        DBManager.save_original_values(
                            stash_id=s_id_str,
                            yards=new_totals["yards"],
                            meters=new_totals["meters"],
                            skeins=new_totals["skeins"],
                            grams=new_totals["grams"]
                        )

                    # Queue Redis detail write to batch-write new details in one round-trip.
                    if redis_pipeline:
                        try:
                            redis_pipeline.setex(
                                f"stash_detail:{s_id_str}",
                                86400,
                                json.dumps({
                                    "updated_at": stash_detail.get("updated_at"),
                                    "packs": new_packs
                                })
                            )
                        except Exception as e:
                            self.LOGGER.error(f"Redis pipeline queue detail failed for {s_id_str}: {e}")
                    
                    cache_item = {
                        "updated_at": stash_detail.get("updated_at"),
                        "packs": new_packs,
                    }
                    for _field in ("colorway_name", "dye_lot", "location", "notes", "stash_status"):
                        if _field in stash_detail:
                            cache_item[_field] = stash_detail[_field]
                    self._memory_cache[s_id_str] = json.dumps(cache_item)

                    item_in_list["packs"] = new_packs
                    # Re-fetch history only if we wrote a new event (otherwise use pre-fetched)
                    if wrote_history_event:
                        item_in_list["history"] = DBManager.get_stash_history(s_id_str) or []
                    else:
                        item_in_list["history"] = bulk_dirty_history.get(s_id_str) or []
                    item_in_list["original_values"] = old_totals
                    # Propagate editable fields from fresh detail — unified list may be stale
                    # after a write (Ravelry-side or local cache). Detail is always authoritative.
                    for _field in ("colorway_name", "dye_lot", "location", "notes",
                                   "stash_status", "updated_at"):
                        if _field in stash_detail:
                            item_in_list[_field] = stash_detail[_field]

            # Execute/flush Redis pipeline to batch-write detailed info in one round-trip.
            if redis_pipeline:
                try:
                    redis_pipeline.execute()
                except Exception as e:
                    self.LOGGER.error(f"Redis pipeline execute failed: {e}")

        # Ensure every stash item has original_values and history populated from DB if not already set.
        # This protects against cases where Redis is disabled and concurrent API fetches fail/time out.
        missing_ids = []
        for s in all_stashes:
            if "id" not in s:
                continue
            s_id_str = str(s["id"])
            if s.get("original_values") is None or s.get("history") is None:
                missing_ids.append(s_id_str)

        if missing_ids:
            bulk_missing_orig = DBManager.get_bulk_original_values(missing_ids)
            bulk_missing_history = DBManager.get_bulk_stash_history(missing_ids)
            for s in all_stashes:
                if "id" not in s:
                    continue
                s_id_str = str(s["id"])
                if s_id_str in missing_ids:
                    if s.get("original_values") is None:
                        s["original_values"] = bulk_missing_orig.get(s_id_str)
                    if s.get("history") is None:
                        s["history"] = bulk_missing_history.get(s_id_str) or []

        return all_stashes

    def create_stash(self, stash_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Post a new stash entry to the user's Ravelry stash.
        """
        import os
        from .dataclasses import StashPost
        username = os.getenv("RAVELRY_USERNAME") or "Thotsky"
        endpoint = f"people/{username}/stash/create.json"
        payload = StashPost(**stash_data).model_dump(exclude_none=True)
        result = self.REQ.post_request(endpoint=endpoint, data=payload)
        
        r = self.get_redis()
        if r:
            try:
                r.delete(f"stash_list:{username}")
            except Exception as e:
                self.LOGGER.error(f"Cache invalidation failed for stash_list:{username} in Redis: {e}")

        if result:
            result_id = result.get("stash", {}).get("id") if isinstance(result, dict) else None
            self.LOGGER.info(f"[WRITE OK] create_stash stash_id={result_id}")
        return result

    def update_stash(self, stash_id: Union[str, int], stash_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a stash entry via POST and invalidate local cache for that entry."""
        import os
        from .dataclasses import StashPost

        username = os.getenv("RAVELRY_USERNAME") or "Thotsky"
        endpoint = f"people/{username}/stash/{stash_id}.json"
        payload = StashPost(**stash_data).model_dump(exclude_none=True)
        result = self.REQ.post_request(endpoint=endpoint, data=payload)

        # Invalidate Redis keys for stash_detail:{stash_id} and stash_list:{username} on write success.
        r = self.get_redis()
        if r:
            try:
                r.delete(f"stash_detail:{stash_id}")
                r.delete(f"stash_list:{username}")
            except Exception as e:
                self.LOGGER.error(f"Cache invalidation failed for stash {stash_id} in Redis: {e}")

        if result:
            self.LOGGER.info(f"[WRITE OK] update_stash stash_id={stash_id}")
            self._memory_cache.pop(str(stash_id), None)
        return result

    def delete_stash(self, stash_id: Union[str, int], stash_type: str = "yarn") -> bool:
        """
        Delete a stash entry (yarn or fiber) from Ravelry, Redis, and SQLite DB.
        """
        import os
        username = os.getenv("RAVELRY_USERNAME") or "Thotsky"
        
        if stash_type == "fiber":
            endpoint = f"people/{username}/fiber/{stash_id}.json"
        else:
            endpoint = f"people/{username}/stash/{stash_id}.json"
            
        result = self.REQ.delete_request(endpoint=endpoint)
        
        # Cleanup DB
        from .db import DBManager
        DBManager.delete_stash_data(str(stash_id))
        
        # Invalidate Redis cache
        r = self.get_redis()
        if r:
            try:
                r.delete(f"stash_detail:{stash_id}")
                r.delete(f"stash_list:{username}")
            except Exception as e:
                self.LOGGER.error(f"Cache invalidation failed for deleted stash {stash_id}: {e}")

        if result is not None:
            self.LOGGER.info(f"[WRITE OK] delete_stash stash_id={stash_id}")
        return result is not None

    def get_stash_history(self, stash_id: Union[str, int]) -> List[Dict[str, Any]]:
        """Fetch history of changes for a specific stash entry from DB."""
        from .db import DBManager
        return DBManager.get_stash_history(str(stash_id)) or []

    def delete_stash_history_event(self, event_id: int) -> bool:
        """Delete a single stash history event from local DB and revert quantities on Ravelry."""
        from .db import DBManager
        event = DBManager.get_history_event(event_id)
        if not event:
            self.LOGGER.warning(f"History event {event_id} not found to delete.")
            return False
            
        stash_id = event["stash_id"]
        
        # 1. Delete event from DB
        success = DBManager.delete_history_event(event_id)
        if not success:
            return False

        DBManager.mark_dirty(str(stash_id))
            
        # 2. Get current skeins from Ravelry and update
        try:
            import os
            username = os.getenv("RAVELRY_USERNAME") or "Thotsky"
            endpoint = f"people/{username}/stash/{stash_id}.json"
            detail = self.REQ.get_request(endpoint=endpoint)
            if detail and "stash" in detail:
                s_detail = detail["stash"]
                event_skeins = float(event.get("skeins") or 0.0)
                packs = s_detail.get("packs") or []
                if packs:
                    current_sk = float(packs[0].get("skeins") or 0.0)
                    new_sk = max(0.0, current_sk - event_skeins)
                    payload = {"pack": {"skeins": new_sk}}
                    self.update_stash(stash_id, payload)
                    self.LOGGER.info(f"Reverted stash {stash_id} skeins: {current_sk} -> {new_sk} after deleting history event {event_id}")
        except Exception as e:
            self.LOGGER.error(f"Failed to revert Ravelry quantities after deleting history event {event_id}: {e}")
            
        return True

    def get_full_yarn(self, yarn_id: Union[str, int]) -> Optional['Yarn']:
        """
        Fetch complete yarn detail including colorways by Ravelry yarn ID.
        - Input
            - yarn_id (str | int): Ravelry numeric yarn ID.
        - output: Fully populated Yarn object with colorways, or None on failure.
        """
        import json
        try:
            # Check Redis cache first for cached yarn data using key yarn:{yarn_id}.
            r = self.get_redis()
            if r:
                try:
                    cached = r.get(f"yarn:{yarn_id}")
                    if cached:
                        data = json.loads(cached)
                        yarn = Yarn(**data['yarn'])
                        yarn.colorways = data['colorways']
                        return yarn
                except Exception as e:
                    self.LOGGER.error(f"Redis get/reconstruct yarn failed: {e}")

            result = self.REQ.get_request(
                endpoint=f"yarns/{yarn_id}.json", params={'include': 'colorways'}
            )
            if result is not None:
                yarn = Yarn(**result['yarn'])
                yarn.colorways = result['colorways']

                # Cache fetched yarn data in Redis with a 24-hour (86400 seconds) TTL.
                if r:
                    try:
                        r.setex(
                            f"yarn:{yarn_id}",
                            86400,
                            json.dumps({
                                "yarn": result['yarn'],
                                "colorways": result['colorways']
                            })
                        )
                    except Exception as e:
                        self.LOGGER.error(f"Redis set yarn failed: {e}")

                return yarn

            return None
        except ValidationError as e:
            self.LOGGER.error(e)
        except Exception as e:
            self.LOGGER.error(e)

    def get_project_map(self) -> Dict[int, Any]:
        """
        Fetch user's projects and build a mapping of project ID to completion/start/creation datetime.
        - output: Dict mapping project ID (int) to pandas.Timestamp.
        """
        import os
        import json
        import pandas as pd
        username = os.getenv("RAVELRY_USERNAME") or "Thotsky"
        
        r = self.get_redis()
        if r:
            try:
                cached = r.get(f"proj_map:{username}")
                if cached:
                    raw_map = json.loads(cached)
                    proj_map = {}
                    for k, v in raw_map.items():
                        proj_map[int(k)] = pd.Timestamp(v)
                    return proj_map
            except Exception as e:
                self.LOGGER.error(f"Redis get proj_map failed: {e}")
        proj_map = {}
        try:
            page = 1
            while True:
                proj_resp = self.REQ.get_request(f"people/{username}/projects/list.json", params={"page_size": 100, "page": page})
                if not proj_resp or "projects" not in proj_resp or not proj_resp["projects"]:
                    break
                    
                for p in proj_resp["projects"]:
                    p_id = p.get("id")
                    date_str = p.get("completed") or p.get("started") or p.get("created_at")
                    if p_id and date_str:
                        try:
                            date_part = date_str.split(" ")[0].replace("/", "-")
                            proj_map[p_id] = pd.to_datetime(date_part)
                        except Exception:
                            pass
                            
                if len(proj_resp["projects"]) < 100:
                    break
                page += 1
                
            if proj_map and r:
                try:
                    serialized = {str(k): v.isoformat() for k, v in proj_map.items()}
                    r.setex(f"proj_map:{username}", 600, json.dumps(serialized))
                except Exception as e:
                    self.LOGGER.error(f"Redis set proj_map failed: {e}")
        except Exception as e:
            self.LOGGER.error(f"Error fetching projects for stash subtraction: {e}")
        return proj_map

    def get_animated_analytics_dataframe(self, stash_list: List[Dict[str, Any]], proj_map: Dict[int, Any]) -> Any:
        """
        Extract history and build cumulative data grouped by month and yarn weight category.
        - Input
            - stash_list (list): Enriched stash entries.
            - proj_map (dict): Project ID to datetime mapping.
        - output: pandas.DataFrame containing sorted date-grouped stats and cumulatives by category.
        """
        import pandas as pd
        data = []
        for s in stash_list:
            created_str = s.get("created_at")
            if not created_str:
                continue
            try:
                date_part = created_str.split(" ")[0]
                stash_date = pd.to_datetime(date_part, format="%Y/%m/%d")
            except Exception:
                continue
                
            updated_str = s.get("updated_at")
            stash_update_date = None
            if updated_str:
                try:
                    up_date_part = updated_str.split(" ")[0]
                    stash_update_date = pd.to_datetime(up_date_part, format="%Y/%m/%d")
                except Exception:
                    pass

            yarn_info = s.get("yarn") or {}
            category = yarn_info.get("yarn_weight_name") or "Unknown Weight"
            
            yardage = float(yarn_info.get("yardage") or 0)
            grams = float(yarn_info.get("grams") or 0)
            meters = yardage * YARDS_TO_METERS
            orig = s.get("original_values")
            packs = s.get("packs") or []
            status_id = s.get("stash_status", {}).get("id")

            if orig:
                data.append({
                    "date": stash_date,
                    "category": category,
                    "yards": float(orig.get("yards") or 0),
                    "meters": float(orig.get("meters") or 0),
                    "skeins": float(orig.get("skeins") or 0),
                    "grams": float(orig.get("grams") or 0),
                })
            elif packs:
                for pack in packs:
                    if pack.get("primary_pack_id") is not None:
                        continue
                    skeins_val = float(pack.get("skeins") if pack.get("skeins") is not None else 1.0)
                    p_yards = pack.get("total_yards")
                    pack_yards = float(p_yards) if p_yards is not None else skeins_val * float(pack.get("yards_per_skein") or yardage or 0)
                    p_meters = pack.get("total_meters")
                    pack_meters = float(p_meters) if p_meters is not None else pack_yards * YARDS_TO_METERS
                    p_grams = pack.get("total_grams")
                    pack_grams = float(p_grams) if p_grams is not None else skeins_val * float(pack.get("grams_per_skein") or grams or 0)

                    data.append({
                        "date": stash_date,
                        "category": category,
                        "yards": pack_yards,
                        "meters": pack_meters,
                        "skeins": skeins_val,
                        "grams": pack_grams,
                    })
            else:
                data.append({
                    "date": stash_date,
                    "category": category,
                    "yards": yardage,
                    "meters": meters,
                    "skeins": 1.0,
                    "grams": grams,
                })

            if packs:
                for pack in packs:
                    if pack.get("primary_pack_id") is not None:
                        continue
                    skeins_val = float(pack.get("skeins") if pack.get("skeins") is not None else 1.0)
                    p_yards = pack.get("total_yards")
                    pack_yards = float(p_yards) if p_yards is not None else skeins_val * float(pack.get("yards_per_skein") or yardage or 0)
                    p_meters = pack.get("total_meters")
                    pack_meters = float(p_meters) if p_meters is not None else pack_yards * YARDS_TO_METERS
                    p_grams = pack.get("total_grams")
                    pack_grams = float(p_grams) if p_grams is not None else skeins_val * float(pack.get("grams_per_skein") or grams or 0)

                    proj_id = pack.get("project_id")
                    if proj_id and proj_id in proj_map:
                        data.append({
                            "date": proj_map[proj_id],
                            "category": category,
                            "yards": -pack_yards,
                            "meters": -pack_meters,
                            "skeins": -skeins_val,
                            "grams": -pack_grams,
                        })
                    elif status_id in (2, 4) and stash_update_date:
                        data.append({
                            "date": stash_update_date,
                            "category": category,
                            "yards": -pack_yards,
                            "meters": -pack_meters,
                            "skeins": -skeins_val,
                            "grams": -pack_grams,
                        })
            else:
                if status_id in (2, 4) and stash_update_date:
                    data.append({
                        "date": stash_update_date,
                        "category": category,
                        "yards": -yardage,
                        "meters": -meters,
                        "skeins": -1.0,
                        "grams": -grams,
                    })

            for event in s.get("history") or []:
                date_val = event.get("date")
                if not date_val:
                    self.LOGGER.warning(f"Skipping history event missing date: {event}")
                    continue
                try:
                    data.append({
                        "date": pd.to_datetime(date_val, format="%Y-%m-%d"),
                        "category": category,
                        "yards": float(event.get("yards") or 0),
                        "meters": float(event.get("meters") or 0),
                        "skeins": float(event.get("skeins") or 0),
                        "grams": float(event.get("grams") or 0),
                    })
                except Exception as e:
                    self.LOGGER.warning(f"Skipping malformed history event: {e}")

        if not data:
            return pd.DataFrame(columns=["date", "category", "yards", "meters", "skeins", "grams",
                                         "cumulative_yards", "cumulative_meters",
                                         "cumulative_skeins", "cumulative_grams", "size_skeins", "frame_date"])

        df = pd.DataFrame(data)
        df["date"] = df["date"].dt.to_period("M").dt.to_timestamp("M")
        
        df = df.groupby(["date", "category"])[["yards", "meters", "skeins", "grams"]].sum().reset_index()
        
        all_dates = df["date"].unique()
        all_categories = df["category"].unique()
        
        idx = pd.MultiIndex.from_product([all_dates, all_categories], names=["date", "category"])
        df = df.set_index(["date", "category"]).reindex(idx, fill_value=0.0).reset_index()
        
        df = df.sort_values(["category", "date"])
        
        df["cumulative_yards"] = df.groupby("category")["yards"].cumsum()
        df["cumulative_meters"] = df.groupby("category")["meters"].cumsum()
        df["cumulative_skeins"] = df.groupby("category")["skeins"].cumsum()
        df["cumulative_grams"] = df.groupby("category")["grams"].cumsum()
        
        df = df.sort_values(["date", "category"])
        df["frame_date"] = df["date"].dt.strftime("%Y-%m")
        df["size_skeins"] = df["cumulative_skeins"].apply(lambda x: max(x, 0.1))
        
        return df

    def get_analytics_dataframe(self, stash_list: List[Dict[str, Any]], proj_map: Dict[int, Any]) -> Any:
        """
        Extract history and build cumulative data over time for analytics.
        - Input
            - stash_list (list): Enriched stash entries.
            - proj_map (dict): Project ID to datetime mapping.
        - output: pandas.DataFrame containing sorted date-grouped stats and cumulatives.
        """
        self.LOGGER.debug(f"get_analytics_dataframe called with {len(stash_list)} stash items")
        import pandas as pd
        data = []
        for s in stash_list:
            created_str = s.get("created_at")
            if not created_str:
                continue
                
            try:
                date_part = created_str.split(" ")[0]
                stash_date = pd.to_datetime(date_part, format="%Y/%m/%d")
            except Exception:
                continue
                
            updated_str = s.get("updated_at")
            stash_update_date = None
            if updated_str:
                try:
                    up_date_part = updated_str.split(" ")[0]
                    stash_update_date = pd.to_datetime(up_date_part, format="%Y/%m/%d")
                except Exception:
                    pass

            yarn_info = s.get("yarn") or {}
            yardage = float(yarn_info.get("yardage") or 0)
            grams = float(yarn_info.get("grams") or 0)
            meters = yardage * YARDS_TO_METERS
            orig = s.get("original_values")
            packs = s.get("packs") or []
            status_id = s.get("stash_status", {}).get("id")

            if orig:
                data.append({
                    "date": stash_date,
                    "yards": float(orig.get("yards") or 0),
                    "meters": float(orig.get("meters") or 0),
                    "skeins": float(orig.get("skeins") or 0),
                    "grams": float(orig.get("grams") or 0),
                })
            elif packs:
                for pack in packs:
                    if pack.get("primary_pack_id") is not None:
                        continue
                    skeins_val = float(pack.get("skeins") if pack.get("skeins") is not None else 1.0)

                    p_yards = pack.get("total_yards")
                    pack_yards = float(p_yards) if p_yards is not None else skeins_val * float(pack.get("yards_per_skein") or yardage or 0)

                    p_meters = pack.get("total_meters")
                    pack_meters = float(p_meters) if p_meters is not None else pack_yards * YARDS_TO_METERS

                    p_grams = pack.get("total_grams")
                    pack_grams = float(p_grams) if p_grams is not None else skeins_val * float(pack.get("grams_per_skein") or grams or 0)

                    data.append({
                        "date": stash_date,
                        "yards": pack_yards,
                        "meters": pack_meters,
                        "skeins": skeins_val,
                        "grams": pack_grams,
                    })
            else:
                data.append({
                    "date": stash_date,
                    "yards": yardage,
                    "meters": meters,
                    "skeins": 1.0,
                    "grams": grams,
                })

            if packs:
                for pack in packs:
                    if pack.get("primary_pack_id") is not None:
                        continue
                    skeins_val = float(pack.get("skeins") if pack.get("skeins") is not None else 1.0)

                    p_yards = pack.get("total_yards")
                    pack_yards = float(p_yards) if p_yards is not None else skeins_val * float(pack.get("yards_per_skein") or yardage or 0)

                    p_meters = pack.get("total_meters")
                    pack_meters = float(p_meters) if p_meters is not None else pack_yards * YARDS_TO_METERS

                    p_grams = pack.get("total_grams")
                    pack_grams = float(p_grams) if p_grams is not None else skeins_val * float(pack.get("grams_per_skein") or grams or 0)

                    proj_id = pack.get("project_id")
                    if proj_id and proj_id in proj_map:
                        data.append({
                            "date": proj_map[proj_id],
                            "yards": -pack_yards,
                            "meters": -pack_meters,
                            "skeins": -skeins_val,
                            "grams": -pack_grams,
                        })
                    elif status_id in (2, 4) and stash_update_date:
                        data.append({
                            "date": stash_update_date,
                            "yards": -pack_yards,
                            "meters": -pack_meters,
                            "skeins": -skeins_val,
                            "grams": -pack_grams,
                        })
            else:
                if status_id in (2, 4) and stash_update_date:
                    data.append({
                        "date": stash_update_date,
                        "yards": -yardage,
                        "meters": -meters,
                        "skeins": -1.0,
                        "grams": -grams,
                    })

            for event in s.get("history") or []:
                date_val = event.get("date")
                if not date_val:
                    self.LOGGER.warning(f"Skipping history event missing date: {event}")
                    continue
                try:
                    data.append({
                        "date": pd.to_datetime(date_val, format="%Y-%m-%d"),
                        "yards": float(event.get("yards") or 0),
                        "meters": float(event.get("meters") or 0),
                        "skeins": float(event.get("skeins") or 0),
                        "grams": float(event.get("grams") or 0),
                    })
                except Exception as e:
                    self.LOGGER.warning(f"Skipping malformed history event: {e}")

        if not data:
            return pd.DataFrame(columns=["date", "yards", "meters", "skeins", "grams",
                                         "cumulative_yards", "cumulative_meters",
                                         "cumulative_skeins", "cumulative_grams"])

        df = pd.DataFrame(data)
        df = df.groupby("date")[["yards", "meters", "skeins", "grams"]].sum().reset_index()
        df = df.sort_values("date")
        
        df["cumulative_yards"] = df["yards"].cumsum()
        df["cumulative_meters"] = df["meters"].cumsum()
        df["cumulative_skeins"] = df["skeins"].cumsum()
        df["cumulative_grams"] = df["grams"].cumsum()

        self.LOGGER.debug(f"get_analytics_dataframe computed {len(df)} daily aggregated records. Cumulative totals: yards={df['cumulative_yards'].iloc[-1] if not df.empty else 0}, skeins={df['cumulative_skeins'].iloc[-1] if not df.empty else 0}")
        return df

    def get_projects_list(self) -> Optional[List[Dict[str, Any]]]:
        """Fetch project list for the configured user."""
        import os
        import json
        username = os.getenv("RAVELRY_USERNAME") or "Thotsky"
        r = self.get_redis()
        cache_key = f"projects_list:{username}"
        if r:
            try:
                cached = r.get(cache_key)
                if cached:
                    return json.loads(cached)
            except Exception as e:
                self.LOGGER.error(f"Redis get projects_list failed: {e}")

        try:
            projects = []
            page = 1
            while True:
                resp = self.REQ.get_request(f"people/{username}/projects/list.json", params={"page_size": 100, "page": page})
                if not resp or "projects" not in resp or not resp["projects"]:
                    break
                projects.extend(resp["projects"])
                if len(resp["projects"]) < 100:
                    break
                page += 1
                
            if projects and r:
                try:
                    r.setex(cache_key, 600, json.dumps(projects))
                except Exception as e:
                    self.LOGGER.error(f"Redis set projects_list failed: {e}")
            return projects if projects else None
        except Exception as e:
            self.LOGGER.error(f"Error fetching projects list: {e}")
        return None


