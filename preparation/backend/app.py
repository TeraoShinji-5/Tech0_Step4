from flask import Flask, request, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token
import os
from dotenv import load_dotenv
from flask import jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy import desc
import json
import re


load_dotenv()  # .env ファイルから環境変数を読み込む

app = Flask(__name__)
CORS(app, origins=["*"]) # 許可するオリジンを指定

# DBの設定
app.config['SQLALCHEMY_DATABASE_URI'] = r'sqlite:///C:\Users\zip-b\Tech0 step4\preparation\POS_System.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# JWTの設定
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
jwt = JWTManager(app) 


class Products(db.Model):
    __tablename__ = 'products'  # ここでテーブル名を指定
    product_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    product_name = db.Column(db.String(120), nullable=False)
    product_qrcode = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    last_update = db.Column(db.DateTime, nullable=True)

class Users(db.Model):
    __tablename__ = 'users'  # ここでテーブル名を指定
    user_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    user_name = db.Column(db.String(120), nullable=False)
    birthplace = db.Column(db.String(80), nullable=True)
    password = db.Column(db.String(80), nullable=False)
    token = db.Column(db.String(80), nullable=True)
    last_update = db.Column(db.DateTime, nullable=True)

class Deal_Details(db.Model):
    __tablename__ = 'deal_details'  # ここでテーブル名を指定
    deal_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    event_id = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    product_name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    buy_time = db.Column(db.DateTime, nullable=True)

class Tax(db.Model):
    __tablename__ = 'tax'  # ここでテーブル名を指定
    tax_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    tax_code = db.Column(db.Integer, nullable=False)
    tax_name = db.Column(db.String(80), nullable=False)
    tax_percent = db.Column(db.Integer, nullable=False)


@app.route('/login', methods=['POST'])
def login():
    user_name = request.json.get('user_name', None)
    password = request.json.get('password', None)
    user = Users.query.filter_by(user_name=user_name, password=password).first()

    if not user:
        return jsonify({"msg": "Bad username or password"}), 401

    now = datetime.now()

    # ユーザーの last_update 属性を確認
    if user.last_update:
        if (now - user.last_update) < timedelta(days=7) and user.token:
            # 7日以内でトークンが存在する場合、現在のトークンを使用
            access_token = user.token
        else:
            # トークンが無いか7日以上経過している場合、新しいトークンを生成
            access_token = create_access_token(identity=user_name)
            user.token = access_token
            user.last_update = now
    else:
        # last_update が設定されていない場合も新しいトークンを生成
        access_token = create_access_token(identity=user_name)
        user.token = access_token
        user.last_update = now

    db.session.commit()

    # トークンをクライアントに返す
    return jsonify(access_token=access_token)


@app.route("/user", methods=['GET'])
def read_user_info():
    user_id = request.args.get('user_id')
    user = Users.query.filter_by(user_id = user_id).first()

    if user:
        # イベントが存在する場合、詳細情報を返す
        user_info = {
            "user_name" : user.user_name,
            "birthplace" : user.birthplace,
            }
        return jsonify(user_info)
    else:
        # ユーザーが存在しない場合
        return jsonify({"message": "イベントが存在しません"})


@app.route("/qrcode", methods=['GET'])
def read_products_info():
    product_qrcode = request.args.get('qrcode')
    product = Products.query.filter_by(product_qrcode = product_qrcode).first()

    if product:
        # イベントが存在する場合、詳細情報を返す
        product_info = {
            "product_id" : product.product_id,
            "product_name" : product.product_name,
            "price" : product.price,
            "quantity" : product.quantity,
            }
        return jsonify(product_info)
    else:
        # ユーザーが存在しない場合
        return jsonify({"message": "イベントが存在しません"})


@app.route('/add_product', methods=['POST'])
def add_product():
    # POSTされたデータを取得
    product_id = request.json.get('product_id', None)
    product_name = request.json.get('product_name', None)
    price = request.json.get('price', None)
    quantity = request.json.get('quantity', None)

    # 1行前のbuy_timeとevent_idをチェック
    last_deal = Deal_Details.query.order_by(Deal_Details.deal_id.desc()).first()
    if last_deal:
        if last_deal.buy_time is None:
            # buy_timeがnullならば、1行前と同じevent_idを使用
            event_id = last_deal.event_id
        else:
            # buy_timeがnullでなければ、event_idに+1した値を使用
            event_id = last_deal.event_id + 1
    else:
        # データベースにデータがまったくない場合
        event_id = 1

    # 新しい取引詳細をデータベースに追加
    new_deal = Deal_Details(event_id=event_id, product_name=product_name, product_id=product_id, price=price, quantity=quantity)
    db.session.add(new_deal)
    db.session.commit()

    # 同じevent_idのすべての行を検索して返す
    deals = Deal_Details.query.filter_by(event_id=event_id).all()
    result = [
        {"quantity": deal.quantity, "product_id": deal.product_id, "product_name": deal.product_name, "price": deal.price}
        for deal in deals
    ]

    return jsonify(result)


@app.route('/purchase', methods=['POST'])
def purchase():
    # 税率を tax テーブルから取得
    # tax_name が "10%" の税レコードを取得
    tax_info = Tax.query.filter_by(tax_name="10%").first()

    # 取得したレコードから tax_percent を取得
    tax_rate = tax_info.tax_percent

    # deal_details テーブルから buy_time が NULL の行を取得し、buy_time を更新
    deals = Deal_Details.query.filter(Deal_Details.buy_time.is_(None)).all()
    total_price = sum(deal.price * deal.quantity for deal in deals)
    for deal in deals:
        deal.buy_time = datetime.now()
    db.session.commit()

    # 税込価格を計算（小数点以下を四捨五入して整数に）
    total_price_tax_included = round(total_price * (1 + tax_rate))

    # 税込価格と税抜価格をクライアントに返送
    response = {
        "total_price": total_price,
        "total_price_tax_included": total_price_tax_included
    }
    return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True)
