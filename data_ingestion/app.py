from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import ORJSONResponse
import pandas as pd
import numpy as np
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(default_response_class=ORJSONResponse)

STANDARD_SCHEMA = {
    "VendorID": "Int64",
    "tpep_pickup_datetime": "datetime64[ns]",
    "tpep_dropoff_datetime": "datetime64[ns]",
    "passenger_count": "Int64",
    "trip_distance": "float64",
    "RatecodeID": "float64",
    "store_and_fwd_flag": "string",
    "PULocationID": "Int64",
    "DOLocationID": "Int64",
    "payment_type": "Int64",
    "fare_amount": "float64",
    "extra": "float64",
    "mta_tax": "float64",
    "tip_amount": "float64",
    "tolls_amount": "float64",
    "improvement_surcharge": "float64",
    "total_amount": "float64",
    "congestion_surcharge": "float64",
    "airport_fee": "float64"
}


@app.get("/api/taxi_trip")
def get_trip_data(
    type: str,
    year: int,
    month: int = Query(..., ge=1, le=12),
    day: int = Query(None, ge=1, le=31),
    hour: int = Query(None, ge=0, le=23),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100000)
):
    DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
    filename = f"{type}_tripdata_{year:04d}-{month:02d}.parquet"
    filepath = os.path.join(DATA_DIR, filename)

    pickup_field = "tpep_pickup_datetime" if type == "yellow" else "lpep_pickup_datetime"

    if not os.path.exists(filepath):
        logger.warning(f"File not found: {filepath}")
        raise HTTPException(status_code=404, detail="File not found")

    try:
        df = pd.read_parquet(filepath)
        df.rename(columns={"Airport_fee": "airport_fee"}, inplace=True)

        # Chuẩn hóa schema: thêm cột thiếu, ép kiểu
        for col, dtype in STANDARD_SCHEMA.items():
            if col not in df.columns:
                df[col] = pd.NA
            try:
                df[col] = df[col].astype(dtype)
            except Exception as e:
                logger.warning(f"Failed to cast column '{col}' to '{dtype}': {e}")
                df[col] = pd.NA

        # Chuẩn hóa datetime
        if pickup_field in df.columns:
            df[pickup_field] = pd.to_datetime(df[pickup_field], errors="coerce")
            df = df.dropna(subset=[pickup_field])
            df = df[df[pickup_field].dt.year == year]
            df = df[df[pickup_field].dt.month == month]
            if day is not None:
                df = df[df[pickup_field].dt.day == day]
            if hour is not None:
                df = df[df[pickup_field].dt.hour == hour]
        else:
            return {"status": "done", "data": [], "total": 0, "offset": offset, "limit": limit}

        total_rows = len(df)
        if offset >= total_rows:
            return {
                "status": "done",
                "data": [],
                "total": total_rows,
                "offset": offset,
                "limit": limit
            }

        df = df.sort_values(pickup_field)
        df_paginated = df.iloc[offset:offset + limit].copy()

        # Format datetime về ISO
        datetime_cols = df_paginated.select_dtypes(include=["datetime64[ns]"]).columns
        for col in datetime_cols:
            df_paginated[col] = df_paginated[col].dt.strftime('%Y-%m-%dT%H:%M:%S')

        # Thay NaN, Inf thành None
        df_paginated = df_paginated.replace([np.nan, np.inf, -np.inf], None)

        records = df_paginated.to_dict(orient="records")

        return {
            "status": "ok",
            "data": records,
            "total": total_rows,
            "offset": offset,
            "limit": limit
        }

    except Exception as e:
        logger.exception(f"Error processing data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing data: {str(e)}")