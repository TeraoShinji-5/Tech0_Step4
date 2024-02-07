from fastapi import FastAPI, HTTPException, Body, Depends
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pymysql
import os
from datetime import datetime
from dotenv import load_dotenv
from typing import List

app = FastAPI()

# CORSを回避するために追加
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,   # 追記により追加
    allow_methods=["*"],      # 追記により追加
    allow_headers=["*"]       # 追記により追加
)

# .envファイルを読み込む
load_dotenv()


class ProductQuery(BaseModel):
    code: str


@app.get("/")
def read_root():
    return {"Hello": "World"}



drink = {
    "PRD_ID":"001",
    "PRD_CD": "4902220772414",
    "PRD_NAME": "クリアアサヒ",
    "PRD_PRICE": "178"
    }

# test用
@app.post("/search_product/")
def search_product(product_query: ProductQuery = Body(...)):
    print(f"Received code: {product_query.code}")
    if product_query.code == drink["PRD_CD"]:
        return {
            "status": "success",
            "message": drink
            }
    else:
        return{
            "status": "failed"
        }
 