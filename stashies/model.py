"""Data model layer for StashStats. Handles Ravelry API interactions including yarn search, stash retrieval with caching, stash creation, and updates."""
from pydantic.dataclasses import dataclass
from pydantic import Field, ValidationError
from typing import Dict, Any, List, Union, Optional
from .base_req import Req
from .base import Base
from .dataclasses import Yarn


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
    meters = yardage * 0.9144
    
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
                pack_meters = pack_yards * 0.9144
                
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


@dataclass
class Model(Base):
    """
    MVC Model layer — wraps Ravelry API calls and local cache management.

    - Properties:
        - REQ (Req): Authenticated HTTP client for Ravelry API.
    """
    REQ: 'Req' = Field(default_factory=Req)
    _redis: Any = None

    def get_redis(self):
        if self._redis is None:
            import os
            import redis
            redis_url = os.getenv("REDIS_URL")
            if not redis_url:
                redis_url = "redis://localhost:6379/0"
            try:
                self._redis = redis.Redis.from_url(redis_url, decode_responses=True)
            except Exception as e:
                self.LOGGER.error(f"Redis initialization failed: {e}")
        return self._redis

    def search_yarn(
        self,
        query: str,
        sort: str = "best",
        page_size: int = 10,
    ) -> Union[List['Yarn'], None]:
        """
        Search Ravelry yarn database by keyword.
        """
        params = {"query": query, "page": 1, "page_size": page_size, "sort": sort}

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
        
        username = os.getenv("RAVELRY_USERNAME") or "Thotsky"
        endpoint = f"people/{username}/stash/unified/list.json"
        
        r = self.get_redis()
        all_stashes = None
        if r:
            try:
                cached_list = r.get(f"stash_list:{username}")
                if cached_list:
                    all_stashes = json.loads(cached_list)
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
            if all_stashes and r:
                try:
                    r.setex(f"stash_list:{username}", 300, json.dumps(all_stashes))
                except Exception as e:
                    self.LOGGER.error(f"Redis set stash_list failed: {e}")
            
        if not all_stashes:
            return None
            
        # Ensure DB tables exist
        DBManager.get_pool()

        # Connect to Redis
        r = self.get_redis()

        dirty_items = []
        for s in all_stashes:
            if "id" not in s:
                continue
            stash_id = str(s["id"])
            updated_at = s.get("updated_at")
            
            # Read from Redis cache
            cached_val = None
            if r:
                try:
                    cached_val = r.get(f"stash_detail:{stash_id}")
                except Exception as e:
                    self.LOGGER.error(f"Redis get failed: {e}")

            if cached_val:
                try:
                    cached_data = json.loads(cached_val)
                    if cached_data.get("updated_at") == updated_at:
                        s["packs"] = cached_data.get("packs") or []
                        # Retrieve history and original_values from SQLite
                        s["history"] = DBManager.get_stash_history(stash_id) or []
                        s["original_values"] = DBManager.get_original_values(stash_id)
                        continue
                except Exception as e:
                    self.LOGGER.error(f"Failed to parse cached details for {stash_id}: {e}")

            dirty_items.append(s)
                
        if dirty_items:
            def fetch_detail(item):
                import time
                s_id = item.get("id")
                is_fiber = item.get("type") == "fiber"
                if not s_id:
                    return None, None
                time.sleep(0.2)  # rate limit compliance
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
                
            max_workers = min(3, len(dirty_items))
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                results = list(executor.map(fetch_detail, dirty_items))
                
            for s_id, stash_detail in results:
                if stash_detail:
                    s_id_str = str(s_id)
                    
                    item_in_list = None
                    for item in all_stashes:
                        if str(item.get("id")) == s_id_str:
                            item_in_list = item
                            break
                            
                    is_fiber = item_in_list.get("type") == "fiber" if item_in_list else False
                    
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
                    
                    old_totals = DBManager.get_original_values(s_id_str)
                    
                    if old_totals:
                        history_events = DBManager.get_stash_history(s_id_str) or []
                        sum_history = {
                            "yards": sum(event["yards"] for event in history_events),
                            "meters": sum(event["meters"] for event in history_events),
                            "skeins": sum(event["skeins"] for event in history_events),
                            "grams": sum(event["grams"] for event in history_events),
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
                    else:
                        # Baseline first-seen original_values
                        DBManager.save_original_values(
                            stash_id=s_id_str,
                            yards=new_totals["yards"],
                            meters=new_totals["meters"],
                            skeins=new_totals["skeins"],
                            grams=new_totals["grams"]
                        )
                    
                    # Store details in Redis with 24 hour TTL
                    if r:
                        try:
                            r.setex(
                                f"stash_detail:{s_id_str}",
                                86400,
                                json.dumps({
                                    "updated_at": stash_detail.get("updated_at"),
                                    "packs": new_packs
                                })
                            )
                        except Exception as e:
                            self.LOGGER.error(f"Redis set failed for {s_id_str}: {e}")

                    if item_in_list:
                        item_in_list["packs"] = new_packs
                        item_in_list["history"] = DBManager.get_stash_history(s_id_str) or []
                        item_in_list["original_values"] = DBManager.get_original_values(s_id_str)
                            
        return all_stashes

    def create_stash(self, stash_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Post a new stash entry to the user's Ravelry stash.
        """
        import os
        username = os.getenv("RAVELRY_USERNAME") or "Thotsky"
        endpoint = f"people/{username}/stash/create.json"
        result = self.REQ.post_request(endpoint=endpoint, data=stash_data)
        
        r = self.get_redis()
        if r:
            try:
                r.delete(f"stash_list:{username}")
            except Exception as e:
                self.LOGGER.error(f"Cache invalidation failed for stash_list:{username} in Redis: {e}")
                
        return result

    def update_stash(self, stash_id: Union[str, int], stash_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a stash entry via POST and invalidate local cache for that entry."""
        import os

        username = os.getenv("RAVELRY_USERNAME") or "Thotsky"
        endpoint = f"people/{username}/stash/{stash_id}.json"
        result = self.REQ.post_request(endpoint=endpoint, data=stash_data)

        # Invalidate Redis cache
        r = self.get_redis()
        if r:
            try:
                r.delete(f"stash_detail:{stash_id}")
                r.delete(f"stash_list:{username}")
            except Exception as e:
                self.LOGGER.error(f"Cache invalidation failed for stash {stash_id} in Redis: {e}")

        return result

    def get_full_yarn(self, yarn_id: Union[str, int]) -> Optional['Yarn']:
        """
        Fetch complete yarn detail including colorways by Ravelry yarn ID.
        - Input
            - yarn_id (str | int): Ravelry numeric yarn ID.
        - output: Fully populated Yarn object with colorways, or None on failure.
        """
        import json
        try:
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
            proj_resp = self.REQ.get_request(f"people/{username}/projects/list.json", params={"page_size": 100})
            if proj_resp and "projects" in proj_resp:
                for p in proj_resp["projects"]:
                    p_id = p.get("id")
                    date_str = p.get("completed") or p.get("started") or p.get("created_at")
                    if p_id and date_str:
                        try:
                            date_part = date_str.split(" ")[0].replace("/", "-")
                            proj_map[p_id] = pd.to_datetime(date_part)
                        except Exception:
                            pass
            if proj_map and r:
                try:
                    serialized = {str(k): v.isoformat() for k, v in proj_map.items()}
                    r.setex(f"proj_map:{username}", 600, json.dumps(serialized))
                except Exception as e:
                    self.LOGGER.error(f"Redis set proj_map failed: {e}")
        except Exception as e:
            self.LOGGER.error(f"Error fetching projects for stash subtraction: {e}")
        return proj_map

    def get_analytics_dataframe(self, stash_list: List[Dict[str, Any]], proj_map: Dict[int, Any]) -> Any:
        """
        Extract history and build cumulative data over time for analytics.
        - Input
            - stash_list (list): Enriched stash entries.
            - proj_map (dict): Project ID to datetime mapping.
        - output: pandas.DataFrame containing sorted date-grouped stats and cumulatives.
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
            yardage = float(yarn_info.get("yardage") or 0)
            grams = float(yarn_info.get("grams") or 0)
            meters = yardage * 0.9144
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
                    pack_meters = float(p_meters) if p_meters is not None else pack_yards * 0.9144

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
                    pack_meters = float(p_meters) if p_meters is not None else pack_yards * 0.9144

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
                try:
                    data.append({
                        "date": pd.to_datetime(event["date"], format="%Y-%m-%d"),
                        "yards": float(event["yards"]),
                        "meters": float(event["meters"]),
                        "skeins": float(event["skeins"]),
                        "grams": float(event["grams"]),
                    })
                except Exception:
                    pass

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
            resp = self.REQ.get_request(f"people/{username}/projects/list.json", params={"page_size": 100})
            if resp and "projects" in resp:
                projects = resp["projects"]
                if r:
                    try:
                        r.setex(cache_key, 600, json.dumps(projects))
                    except Exception as e:
                        self.LOGGER.error(f"Redis set projects_list failed: {e}")
                return projects
        except Exception as e:
            self.LOGGER.error(f"Error fetching projects list: {e}")
        return None

    def get_queue_list(self) -> Optional[List[Dict[str, Any]]]:
        """Fetch queued projects for the configured user."""
        import os
        import json
        username = os.getenv("RAVELRY_USERNAME") or "Thotsky"
        r = self.get_redis()
        cache_key = f"queue_list:{username}"
        if r:
            try:
                cached = r.get(cache_key)
                if cached:
                    return json.loads(cached)
            except Exception as e:
                self.LOGGER.error(f"Redis get queue_list failed: {e}")

        try:
            resp = self.REQ.get_request(f"people/{username}/queue/list.json", params={"page_size": 100})
            if resp and "queued_projects" in resp:
                queue = resp["queued_projects"]
                if r:
                    try:
                        r.setex(cache_key, 600, json.dumps(queue))
                    except Exception as e:
                        self.LOGGER.error(f"Redis set queue_list failed: {e}")
                return queue
        except Exception as e:
            self.LOGGER.error(f"Error fetching queue list: {e}")
        return None

    def get_needles_list(self) -> Optional[List[Dict[str, Any]]]:
        """Fetch owned needles/hooks for the configured user."""
        import os
        import json
        username = os.getenv("RAVELRY_USERNAME") or "Thotsky"
        r = self.get_redis()
        cache_key = f"needles_list:{username}"
        if r:
            try:
                cached = r.get(cache_key)
                if cached:
                    return json.loads(cached)
            except Exception as e:
                self.LOGGER.error(f"Redis get needles_list failed: {e}")

        try:
            resp = self.REQ.get_request(f"people/{username}/needles/list.json")
            if resp and "needle_records" in resp:
                needles = resp["needle_records"]
                if r:
                    try:
                        r.setex(cache_key, 3600, json.dumps(needles))
                    except Exception as e:
                        self.LOGGER.error(f"Redis set needles_list failed: {e}")
                return needles
        except Exception as e:
            self.LOGGER.error(f"Error fetching needles list: {e}")
        return None

    def reposition_queue_item(self, queue_id: Union[str, int], new_position: int) -> bool:
        """Reposition a queued project and invalidate queue cache."""
        import os
        import json
        username = os.getenv("RAVELRY_USERNAME") or "Thotsky"
        endpoint = f"people/{username}/queue/{queue_id}/reposition.json"
        
        try:
            result = self.REQ.post_request(endpoint, data={"insert_at": new_position})
            if result:
                # Invalidate queue cache
                r = self.get_redis()
                if r:
                    try:
                        r.delete(f"queue_list:{username}")
                    except Exception as e:
                        self.LOGGER.error(f"Redis delete queue_list failed: {e}")
                return True
        except Exception as e:
            self.LOGGER.error(f"Error repositioning queue item {queue_id}: {e}")
        return False

    def remove_queue_item(self, queue_id: Union[str, int]) -> bool:
        """Delete a queued project and invalidate queue cache."""
        import os
        username = os.getenv("RAVELRY_USERNAME") or "Thotsky"
        endpoint = f"people/{username}/queue/{queue_id}.json"
        
        try:
            result = self.REQ.delete_request(endpoint)
            # Ravelry returns empty dict or standard response on delete.
            # Even if result is empty dict, it succeeded if no HTTPError was raised.
            # Invalidate queue cache
            r = self.get_redis()
            if r:
                try:
                    r.delete(f"queue_list:{username}")
                except Exception as e:
                    self.LOGGER.error(f"Redis delete queue_list failed: {e}")
            return True
        except Exception as e:
            self.LOGGER.error(f"Error deleting queue item {queue_id}: {e}")
        return False
