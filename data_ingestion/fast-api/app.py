from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
import pandas as pd
import numpy as np
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/api/taxi_trip")
def get_trip_data(
    type: str,
    year: int,
    month: int = Query(None, ge=1, le=12),
    day: int = Query(None, ge=1, le=31),
    hour: int = Query(None, ge=0, le=23),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100000)
):
    DATA_DIR = os.path.join(os.path.dirname(__file__), f"data/{year}")
    filename = f"{type}_tripdata_{year:04d}-{month:02d}.parquet"
    filepath = os.path.join(DATA_DIR, filename)

    pickup_field = "tpep_pickup_datetime" if type == "yellow" else "lpep_pickup_datetime"

    if not os.path.exists(filepath):
        logger.warning(f"File not found: {filepath}")
        raise HTTPException(status_code=404, detail="File not found")

    try:
        df = pd.read_parquet(filepath)
        df.rename(columns={"Airport_fee": "airport_fee"}, inplace=True)

        df[pickup_field] = pd.to_datetime(df[pickup_field], errors="coerce")
        df = df.dropna(subset=[pickup_field])

        # Lọc theo ngày/giờ nếu có
        if day is not None:
            df = df[df[pickup_field].dt.day == day]
        if hour is not None:
            df = df[df[pickup_field].dt.hour == hour]

        total_rows = len(df)
        if offset >= total_rows:
            return JSONResponse(content={
                "status": "done",
                "data": [],
                "total": total_rows,
                "offset": offset,
                "limit": limit
            })

        df = df.sort_values(pickup_field)
        df_paginated = df.iloc[offset:offset + limit].copy()

        # Chuyển datetime thành string
        datetime_cols = df_paginated.select_dtypes(include=["datetime64[ns]"]).columns
        df_paginated[datetime_cols] = df_paginated[datetime_cols].astype(str)

        # Xử lý giá trị float không hợp lệ (NaN, inf)
        float_cols = df_paginated.select_dtypes(include=['float64', 'float32']).columns
        for col in float_cols:
            df_paginated[col] = df_paginated[col].apply(
                lambda x: None if isinstance(x, float) and (np.isnan(x) or np.isinf(x)) else x
            )

        # Ép kiểu float → int cho các trường định nghĩa
        float_to_int_cols = ["passenger_count", "payment_type"]
        for col in float_to_int_cols:
            if col in df_paginated.columns:
                df_paginated[col] = df_paginated[col].apply(
                    lambda x: int(x) if pd.notnull(x) and isinstance(x, (float, np.float64)) and x == int(x) else x
                )

        # records = []
        # for _, row in df_paginated.iterrows():
        #     record = {}
        #     for col in df_paginated.columns:
        #         val = row[col]
        #         if isinstance(val, float) and (np.isnan(val) or np.isinf(val)):
        #             record[col] = None
        #         else:
        #             record[col] = val
        #     records.append(record)
        records = df_paginated.replace([np.nan, np.inf], None).to_dict('records')


        return JSONResponse(content={
            "status": "ok",
            "data": records,
            "total": total_rows,
            "offset": offset,
            "limit": limit
        })
       
    except Exception as e:
        logger.exception(f"Error processing data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing data: {str(e)}")