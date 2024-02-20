from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse
from fastapi import Query
import os
from typing import Optional
from sqlalchemy import func
from jose import jwt
from pytz import timezone
from fastapi.middleware.cors import CORSMiddleware
import pytz


# 環境変数の読み込み
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

# トークンを生成するためのシークレットキー
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = "HS256"

app = FastAPI()

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ここに許可するオリジンを指定します。*はすべてのオリジンを許可します。
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # 許可するメソッドを指定します。
    allow_headers=["*"],  # すべてのヘッダーを許可します。必要に応じて指定します。
)

# データベース接続設定
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ProductDB(Base):
    __tablename__ = 'products'
    product_id = Column(Integer, primary_key=True, nullable=False)
    product_name = Column(String(255), nullable=False)
    price = Column(Integer, nullable=False)
    product_qrcode = Column(Integer, unique=True, nullable=False)
    quantity = Column(Integer, nullable=False)
    last_update = Column(DateTime, default=datetime.utcnow)

class UserDB(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True, nullable=False)
    user_name = Column(String(255), nullable=False)
    birthplace = Column(String(255), nullable=False)
    password = Column(String(255), nullable=True)
    token = Column(String(500), nullable=True)
    last_update = Column(DateTime, default=datetime.utcnow)

# ユーザー情報を格納するためのモデル
class User(BaseModel):
    user_name: str
    password: str

class Deal_DetailsDB(Base):
    __tablename__ = 'deal_details'  # テーブル名を指定
    deal_id = Column(Integer, primary_key=True, nullable=False)
    event_id = Column(Integer, nullable=True)  # MySQL定義に合わせてデフォルトNULL
    quantity = Column(Integer, nullable=False)
    product_qrcode = Column(Integer, nullable=False)
    product_name = Column(String(255), nullable=False)  # 長さを255に合わせる
    price = Column(Integer, nullable=False)
    tax_percent = Column(Numeric(precision=5, scale=2), nullable=False)
    buy_time = Column(DateTime, nullable=False)  # nullable=TrueからFalseに変更

# リクエストボディのモデル定義
class Product(BaseModel):
    product_qrcode: int
    product_name: str
    price: int
    quantity: int
    tax_percent: float
    buy_time: datetime

class ProductList(BaseModel):
    products: list[Product]


class TaxDB(Base):
    __tablename__ = 'tax'  # テーブル名を指定
    tax_id = Column(Integer, primary_key=True, nullable=False)
    tax_code = Column(Integer, unique=True, nullable=False)
    tax_name = Column(String(255), nullable=False)  # 長さを255に合わせる
    tax_percent = Column(Numeric(precision=5, scale=2), nullable=False) # MySQLのdecimal型に対応するためにNumeric型を使用

# SQLAlchemyのテーブルモデル
class TradesDB(Base):
    __tablename__ = 'trades'
    trade_id = Column(Integer, primary_key=True, autoincrement=True)
    buy_time = Column(DateTime, default=func.now(), nullable=False)
    staff_id = Column(Integer, nullable=False)
    machine_id = Column(Integer, nullable=False)
    store_id = Column(Integer, nullable=False)
    total_charge = Column(Integer, nullable=False)
    total_charge_wo_tax = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=True)

# Pydanticモデルの定義
class Trades(BaseModel):
    token: str
    store_id: int
    staff_id: int
    machine_id: int
    total_charge: int
    total_charge_wo_tax: int
    buy_time: Optional[datetime]  # buy_time フィールドをオプションに変更


# データベースのセットアップ
Base.metadata.create_all(bind=engine)


# UTCで取得した日時をJSTに変換する関数
def to_jst(datetime_obj):
    utc_zone = pytz.utc
    jst_zone = pytz.timezone('Asia/Tokyo')
    return datetime_obj.replace(tzinfo=utc_zone).astimezone(jst_zone)


@app.post('/login')
async def login(user: User):
    db = SessionLocal()
    # ユーザーの認証
    user_info = db.query(UserDB).filter_by(user_name=user.user_name, password=user.password).first()
    if not user_info:
        raise HTTPException(status_code=401, detail="Bad username or password")

    now = datetime.now()

    # トークンが有効期限内であるかどうかをチェックし、トークンを発行または更新する
    if user_info.last_update is None or (now - user_info.last_update) > timedelta(days=7):
        # トークンのペイロード
        payload = {
            "sub": user_info.user_name,
            "exp": now + timedelta(days=7)  # トークンの有効期限を7日に設定
        }

        # トークンを生成
        access_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

        # ユーザー情報の更新
        user_info.token = access_token
        user_info.last_update = now
        db.commit()
    else:
        access_token = user_info.token

    # トークンをクライアントに返す
    return {"access_token": access_token, "user_name": user_info.user_name}


@app.get('/shopping')
async def read_login(token: str = Query(..., description="Token information")):
    db = SessionLocal()
    # ユーザーの認証
    user_info = db.query(UserDB).filter_by(token=token).first()
    if not user_info:
        raise HTTPException(status_code=401, detail="Bad token")

    user_name = user_info.user_name

    # ユーザー名をクライアントに返す
    return {"user_name": user_name}


@app.get("/qrcode")
async def read_products_info(qrcode: int = Query(..., description="Product QR code")):
    db = SessionLocal()
    product = db.query(ProductDB).filter_by(product_qrcode=qrcode).first()
    if product:
        # Productの情報を取得
        product_info = {
            "product_id": product.product_id,
            "product_name": product.product_name,
            "price": product.price,
            "product_qrcode": product.product_qrcode,
            "quantity": product.quantity,
        }

        # Taxの情報を取得
        tax = db.query(TaxDB).first()
        if tax:
            product_info["tax_percent"] = tax.tax_percent
        else:
            product_info["tax_percent"] = 0.1  # デフォルト値などを設定する必要がある場合

        db.close()
        return product_info
    else:
        db.close()
        return JSONResponse(content={"product_name": "商品がマスタ未登録です"}, status_code=404)


@app.post('/trade')
async def add_trade(trade: Trades):
    db = SessionLocal()
    # ユーザーの情報を取得
    user_info = db.query(UserDB).filter_by(token=trade.token).first()
    if not user_info:
        raise HTTPException(status_code=404, detail="User not found")

    # UTCで取得した日時をJSTに変換
    buy_time_utc = trade.buy_time
    jst = pytz.timezone('Asia/Tokyo')
    buy_time_jst = buy_time_utc.astimezone(jst)

    new_trade = TradesDB(
        user_id=user_info.user_id,
        store_id=trade.store_id,
        staff_id=trade.staff_id,
        machine_id=trade.machine_id,
        total_charge=trade.total_charge,
        total_charge_wo_tax=trade.total_charge_wo_tax,
        buy_time=buy_time_jst
    )

    # トレードをデータベースに追加してコミット
    db.add(new_trade)
    db.commit()

    # 成功した場合は挿入されたトレードのIDを含むレスポンスを返す
    return {"trade_id": new_trade.trade_id}


# FastAPIのエンドポイント
@app.post('/deal_detail')
def add_deal_detail(products: ProductList):
    db = SessionLocal()
    jst = pytz.timezone('Asia/Tokyo')  # 日本時間のタイムゾーンを設定

    for product in products.products:
        # UTCで取得した日時をJSTに変換
        buy_time_utc = product.buy_time
        buy_time_jst = buy_time_utc.astimezone(jst)

        new_detail = Deal_DetailsDB(
            product_qrcode=product.product_qrcode,
            product_name=product.product_name,
            price=product.price,
            quantity=product.quantity,
            tax_percent=product.tax_percent,
            event_id=1,  # 適切なevent_idの取り扱いを確認してください
            buy_time=buy_time_jst  # JSTに変換した日時を使用
        )
        db.add(new_detail)
    db.commit()
    return {'message': 'Deal details added successfully'}
