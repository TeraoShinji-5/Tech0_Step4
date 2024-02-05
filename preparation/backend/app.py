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
    qrcode = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    product_name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    last_update = db.Column(db.DateTime, nullable=True)

class Users(db.Model):
    __tablename__ = 'users'  # ここでテーブル名を指定
    user_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    user_name = db.Column(db.String(120), nullable=False)
    birthplace = db.Column(db.String(80), nullable=True)
    password = db.Column(db.String(80), nullable=False)
    token = db.Column(db.String(80), nullable=True)
    last_update = db.Column(db.DateTime, nullable=True)


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


@app.route("/qrcode", methods=['GET'])
def read_products_info():
    qrcode = request.args.get('qrcode')
    product = Products.query.filter_by(qrcode = qrcode).first()

    if product:
        # イベントが存在する場合、詳細情報を返す
        product_info = {
            "product_name" : product.product_name,
            "price" : product.price,
            }
        return jsonify(product_info)
    else:
        # ユーザーが存在しない場合
        return jsonify({"message": "イベントが存在しません"})


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

if __name__ == "__main__":
    app.run(debug=True)

