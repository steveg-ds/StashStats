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
    - Methods:
        - search_yarn: Full-text yarn search returning validated Yarn objects.
        - get_stash_list: Fetches all stash entries with pack details, using a local JSON cache.
        - create_stash: Posts a new stash entry to the user's Ravelry stash.
        - update_stash: PUTs updated stash data and invalidates the local cache entry.
        - get_full_yarn: Fetches complete yarn data including colorways by yarn ID.
    """
    # TODO: eventually I should set up redis/ memory caching to reduce API hits
    REQ: 'Req' = Field(default_factory=Req)

    def search_yarn(
        self,
        query: str,
        sort: str = "best",
        page_size: int = 10,
    ) -> Union[List['Yarn'], None]:
        """
        Search Ravelry yarn database by keyword.
        - Input
            - query (str): Search keyword(s).
            - sort (str): Sort order e.g. 'best'. Defaults to 'best'.
            - page_size (int): Results per page. Defaults to 10.
        - output: List of Yarn objects, or None if no results.
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

    def get_stash_list(self) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch all stash entries for the configured user, enriched with pack details.

        Paginates the stash list endpoint, then fetches per-entry detail for any
        entries not in the local JSON cache or with a changed updated_at sentinel.
        - output: List of stash entry dicts with 'packs', 'history', and 'original_values' added. None if stash is empty.
        """
        import os
        import json
        import concurrent.futures
        
        username = os.getenv("USERNAME") or "Thotsky"
        endpoint = f"people/{username}/stash/list.json"
        
        all_stashes = []
        page = 1
        while True:
            result = self.REQ.get_request(
                endpoint=endpoint, 
                params={"page_size": 100, "page": page}
            )
            if not result or "stash" not in result or not result["stash"]:
                break
            all_stashes.extend(result["stash"])
            if len(result["stash"]) < 100:
                break
            page += 1
            
        if not all_stashes:
            return None
            
        # Load cache
        cache_file = "stash_cache.json"
        cache = {}
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r") as f:
                    cache = json.load(f)
            except Exception:
                pass

        # dirty_items: entries absent from cache or with a changed updated_at sentinel
        dirty_items = []
        for s in all_stashes:
            if "id" not in s:
                continue
            stash_id = str(s["id"])
            updated_at = s.get("updated_at")
            if stash_id in cache and cache[stash_id].get("updated_at") == updated_at:
                s["packs"] = cache[stash_id].get("packs") or []
                s["history"] = cache[stash_id].get("history") or []
                s["original_values"] = cache[stash_id].get("original_values")
            else:
                dirty_items.append(s)
                
        if dirty_items:
            def fetch_detail(item):
                """
                Fetch full stash entry detail for a single stash item.
                - Input
                    - item (dict): Stash summary dict with at minimum an 'id' key.
                - output: Tuple (stash_id, detail_dict) or (stash_id, None) on failure.
                """
                import time
                s_id = item.get("id")
                if not s_id:
                    return None, None
                time.sleep(0.2)  # rate limit compliance
                detail_endpoint = f"people/{username}/stash/{s_id}.json"
                try:
                    res = self.REQ.get_request(detail_endpoint)
                    if res and "stash" in res:
                        return s_id, res["stash"]
                except Exception as e:
                    self.LOGGER.error(f"Error fetching stash detail {s_id}: {e}")
                return s_id, None
                
            max_workers = min(3, len(dirty_items))
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                results = list(executor.map(fetch_detail, dirty_items))
                
            cache_updated = False
            for s_id, stash_detail in results:
                if stash_detail:
                    s_id_str = str(s_id)
                    new_packs = stash_detail.get("packs") or []
                    yarn_info = stash_detail.get("yarn") or {}
                    new_totals = get_primary_totals(new_packs, yarn_info)
                    
                    if s_id_str in cache:
                        old_packs = cache[s_id_str].get("packs") or []
                        old_totals = get_primary_totals(old_packs, yarn_info)
                        
                        delta = {
                            "yards": new_totals["yards"] - old_totals["yards"],
                            "meters": new_totals["meters"] - old_totals["meters"],
                            "skeins": new_totals["skeins"] - old_totals["skeins"],
                            "grams": new_totals["grams"] - old_totals["grams"]
                        }
                        
                        # Only record a history event when pack totals actually changed
                        if any(val != 0.0 for val in delta.values()):
                            up_date_str = stash_detail.get("updated_at") or ""
                            date_part = up_date_str.split(" ")[0].replace("/", "-") if up_date_str else ""
                            event = {
                                "date": date_part,
                                "yards": delta["yards"],
                                "meters": delta["meters"],
                                "skeins": delta["skeins"],
                                "grams": delta["grams"]
                            }
                            cache[s_id_str].setdefault("history", []).append(event)
                        
                        cache[s_id_str]["updated_at"] = stash_detail.get("updated_at")
                        cache[s_id_str]["packs"] = new_packs
                        # Preserve first-seen baseline; never overwrite with a later snapshot
                        if "original_values" not in cache[s_id_str]:
                            cache[s_id_str]["original_values"] = old_totals
                    else:
                        cache[s_id_str] = {
                            "updated_at": stash_detail.get("updated_at"),
                            "packs": new_packs,
                            "original_values": new_totals,
                            "history": []
                        }
                        
                    cache_updated = True
                    for item in all_stashes:
                        if item["id"] == s_id:
                            item["packs"] = new_packs
                            item["history"] = cache[s_id_str].get("history") or []
                            item["original_values"] = cache[s_id_str].get("original_values")
                            break
                            
            if cache_updated:
                try:
                    with open(cache_file, "w") as f:
                        json.dump(cache, f, indent=2)
                except Exception:
                    pass
                    
        return all_stashes

    def create_stash(self, stash_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Post a new stash entry to the user's Ravelry stash.
        - Input
            - stash_data (dict): Stash payload per Ravelry API spec.
        - output: API response dict, or None on failure.
        """
        import os
        username = os.getenv("USERNAME") or "Thotsky"
        endpoint = f"people/{username}/stash/create.json"
        return self.REQ.post_request(endpoint=endpoint, data=stash_data)

    def update_stash(self, stash_id: Union[str, int], stash_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a stash entry via PUT and invalidate local cache for that entry."""
        import os
        import json

        username = os.getenv("USERNAME") or "Thotsky"
        endpoint = f"people/{username}/stash/{stash_id}.json"
        result = self.REQ.put_request(endpoint=endpoint, data=stash_data)

        # Invalidate cache so next load re-fetches fresh pack details
        cache_file = "stash_cache.json"
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r") as f:
                    cache = json.load(f)
                stash_id_str = str(stash_id)
                if stash_id_str in cache:
                    # Remove updated_at sentinel AND zero packs so delta
                    # calculation on next fetch uses fresh baseline, not stale.
                    cache[stash_id_str].pop("updated_at", None)
                    cache[stash_id_str]["packs"] = []
                    with open(cache_file, "w") as f:
                        json.dump(cache, f, indent=2)
            except Exception as e:
                self.LOGGER.error(f"Cache invalidation failed for stash {stash_id}: {e}")

        return result

    def get_full_yarn(self, yarn_id: Union[str, int]) -> Optional['Yarn']:
        """
        Fetch complete yarn detail including colorways by Ravelry yarn ID.
        - Input
            - yarn_id (str | int): Ravelry numeric yarn ID.
        - output: Fully populated Yarn object with colorways, or None on failure.
        """
        try:
            result = self.REQ.get_request(
                endpoint=f"yarns/{yarn_id}.json", params={'include': 'colorways'}
            )
            if result is not None:
                yarn = Yarn(**result['yarn'])
                yarn.colorways = result['colorways']

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
        import pandas as pd
        username = os.getenv("USERNAME") or "Thotsky"
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
