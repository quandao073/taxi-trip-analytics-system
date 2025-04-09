from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
import pandas as pd
import numpy as np
import pyarrow.parquet as pq
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

@app.get("/api/taxi_trip")
def get_trip_data(
    type: str,
    year: int,
    month: int,
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=10000)
):
    filename = f"{type}_tripdata_{year:04d}-{month:02d}.parquet"
    filepath = os.path.join(DATA_DIR, filename)

    if not os.path.exists(filepath):
        logger.warning(f"File not found: {filepath}")
        raise HTTPException(status_code=404, detail="File not found")

    try:
        total_rows = pq.ParquetFile(filepath).metadata.num_rows

        if offset >= total_rows:
            return JSONResponse(content={
                "status": "done",
                "data": [],
                "total": total_rows,
                "offset": offset,
                "limit": limit
            })

        df = pd.read_parquet(filepath)
        df = df.sort_values("tpep_pickup_datetime")

        df_paginated = df.iloc[offset:offset + limit].copy()

        # Xử lý các cột datetime
        datetime_cols = df_paginated.select_dtypes(include=["datetime64[ns]"]).columns
        df_paginated[datetime_cols] = df_paginated[datetime_cols].astype(str)

        # Kiểm tra và log các giá trị float không hợp lệ
        float_cols = df_paginated.select_dtypes(include=['float64', 'float32']).columns
        for col in float_cols:
            invalid_values = df_paginated[df_paginated[col].apply(
                lambda x: np.isnan(x) or np.isinf(x) if isinstance(x, float) else False
            )]
            
            if not invalid_values.empty:
                logger.info(f"Column {col} has invalid values: {invalid_values[col].unique()}")
                
        # Chuyển đổi tất cả các giá trị float không hợp lệ thành None
        for col in float_cols:
            df_paginated[col] = df_paginated[col].apply(
                lambda x: None if isinstance(x, float) and (np.isnan(x) or np.isinf(x)) else x
            )
        
        for col in float_cols:
            df_paginated[col] = df_paginated[col].apply(
                lambda x: None if isinstance(x, float) and (pd.isna(x) or np.isinf(x)) else x
            )
            
        # Chuyển đổi thành records
        records = []
        for _, row in df_paginated.iterrows():
            record = {}
            for col in df_paginated.columns:
                val = row[col]
                if isinstance(val, float) and (np.isnan(val) or np.isinf(val)):
                    record[col] = None
                else:
                    record[col] = val
            records.append(record)

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