import datetime
import numpy as np
import pandas as pd
from faker import Faker
from stashies.utils import YARDS_TO_METERS

def get_mock_analytics_dataframe(days: int = 730) -> pd.DataFrame:
    fake = Faker()
    Faker.seed(42)
    np.random.seed(42)

    today = datetime.date.today()
    start_date = today - datetime.timedelta(days=days)
    dates = [start_date + datetime.timedelta(days=i) for i in range(days)]
    
    # Modeled with daily Poisson process for stash additions (lambda = 0.15 events/day)
    stash_events = np.random.poisson(0.15, days)
    # Modeled with daily Poisson process for projects consuming stash (lambda = 0.08 events/day)
    project_events = np.random.poisson(0.08, days)
    
    data = []
    
    for i, date in enumerate(dates):
        # Stash additions
        for _ in range(stash_events[i]):
            # Log-normal distribution of skeins added
            skeins = float(np.random.lognormal(mean=0.8, sigma=0.5))
            skeins = max(1.0, round(skeins))
            
            # Yardage per skein depends on random weights
            weight_type = np.random.choice(["fingering", "dk", "worsted", "bulky"], p=[0.4, 0.2, 0.3, 0.1])
            yd_map = {"fingering": 400.0, "dk": 220.0, "worsted": 200.0, "bulky": 110.0}
            yardage = skeins * yd_map[weight_type]
            grams = skeins * 100.0
            
            data.append({
                "date": pd.to_datetime(date),
                "yards": yardage,
                "meters": yardage * YARDS_TO_METERS,
                "skeins": float(skeins),
                "grams": grams
            })
            
        # Stash consumption
        for _ in range(project_events[i]):
            # Log-normal distribution of skeins consumed
            skeins = float(np.random.lognormal(mean=0.5, sigma=0.4))
            skeins = max(1.0, round(skeins))
            
            weight_type = np.random.choice(["fingering", "dk", "worsted", "bulky"], p=[0.4, 0.2, 0.3, 0.1])
            yd_map = {"fingering": 400.0, "dk": 220.0, "worsted": 200.0, "bulky": 110.0}
            yardage = skeins * yd_map[weight_type]
            grams = skeins * 100.0
            
            data.append({
                "date": pd.to_datetime(date),
                "yards": -yardage,
                "meters": -yardage * YARDS_TO_METERS,
                "skeins": -float(skeins),
                "grams": -grams
            })

    if not data:
        # Fallback empty dataframe structure
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

def get_mock_animated_analytics_dataframe(days: int = 730) -> pd.DataFrame:
    np.random.seed(42)
    today = datetime.date.today()
    start_date = today - datetime.timedelta(days=days)
    dates = [start_date + datetime.timedelta(days=i) for i in range(days)]
    
    categories = ["Lace", "Fingering", "DK", "Worsted", "Bulky"]
    probs = [0.15, 0.35, 0.20, 0.20, 0.10]
    
    data = []
    
    for i, date in enumerate(dates):
        month_start = pd.to_datetime(date).to_period("M").to_timestamp("M")
        
        # Arrivals (Poisson lambda = 0.2)
        events = np.random.poisson(0.2)
        for _ in range(events):
            cat = np.random.choice(categories, p=probs)
            skeins = float(np.random.lognormal(mean=0.8, sigma=0.5))
            skeins = max(1.0, round(skeins))
            yd_map = {"Lace": 600.0, "Fingering": 400.0, "DK": 220.0, "Worsted": 200.0, "Bulky": 110.0}
            yardage = skeins * yd_map[cat]
            
            data.append({
                "date": month_start,
                "category": cat,
                "yards": yardage,
                "meters": yardage * YARDS_TO_METERS,
                "skeins": float(skeins),
                "grams": skeins * 100.0
            })
            
        # Consumption (Poisson lambda = 0.1)
        events_cons = np.random.poisson(0.1)
        for _ in range(events_cons):
            cat = np.random.choice(categories, p=probs)
            skeins = float(np.random.lognormal(mean=0.5, sigma=0.4))
            skeins = max(1.0, round(skeins))
            yd_map = {"Lace": 600.0, "Fingering": 400.0, "DK": 220.0, "Worsted": 200.0, "Bulky": 110.0}
            yardage = skeins * yd_map[cat]
            
            data.append({
                "date": month_start,
                "category": cat,
                "yards": -yardage,
                "meters": -yardage * YARDS_TO_METERS,
                "skeins": -float(skeins),
                "grams": -skeins * 100.0
            })

    if not data:
        return pd.DataFrame(columns=["date", "category", "yards", "meters", "skeins", "grams",
                                     "cumulative_yards", "cumulative_meters",
                                     "cumulative_skeins", "cumulative_grams", "size_skeins", "frame_date"])

    df = pd.DataFrame(data)
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
