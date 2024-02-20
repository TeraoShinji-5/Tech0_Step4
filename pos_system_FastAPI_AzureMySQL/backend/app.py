from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token
import os
from dotenv import load_dotenv
from flask import jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
from dateutil import parser
import pytz


load_dotenv()  # .env ファイルから環境変数を読み込む
password = os.getenv('password')

app = Flask(__name__)
CORS(app, origins=["*"]) # 許可するオリジンを指定

# DBの設定
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://root:Tech0415BTO@localhost/mydb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# JWTの設定
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
jwt = JWTManager(app)


class Products(db.Model):
    __tablename__ = 'products'  # テーブル名を指定
    product_id = db.Column(db.Integer, primary_key=True, nullable=False)
    product_name = db.Column(db.String(255), nullable=False)  # 長さを255に合わせる
    price = db.Column(db.Integer, nullable=False)
    product_qrcode = db.Column(db.Integer, unique=True, nullable=False)  # 文字列から整数型に変更
    quantity = db.Column(db.Integer, nullable=False)
    last_update = db.Column(db.DateTime, default=datetime.utcnow)  # defaultを指定

class Users(db.Model):
    __tablename__ = 'users'  # テーブル名を指定
    user_id = db.Column(db.Integer, primary_key=True, nullable=False)  # unique=Trueは不要です（primary_keyは自動的にユニークです）
    user_name = db.Column(db.String(255), nullable=False)  # 長さを255に合わせる
    birthplace = db.Column(db.String(255), nullable=False)  # nullable=Falseに変更し、長さを255に合わせる
    password = db.Column(db.String(255), nullable=True)  # nullable=Trueに変更し、長さを255に合わせる
    token = db.Column(db.String(500), nullable=True)  # 長さを500に合わせる
    last_update = db.Column(db.DateTime, default=datetime.utcnow)  # default=datetime.utcnowを追加

# ユーザー情報を格納するためのモデル
class User(BaseModel):
    user_name: str
    password: str

class Deal_Details(db.Model):
    __tablename__ = 'deal_details'  # テーブル名を指定
    deal_id = db.Column(db.Integer, primary_key=True, nullable=False)
    event_id = db.Column(db.Integer, nullable=True)  # MySQL定義に合わせてデフォルトNULL
    quantity = db.Column(db.Integer, nullable=False)
    product_qrcode = db.Column(db.Integer, nullable=False)
    product_name = db.Column(db.String(255), nullable=False)  # 長さを255に合わせる
    price = db.Column(db.Integer, nullable=False)
    tax_percent = db.Column(db.Numeric(5, 2), nullable=False)  # MySQLのdecimal型に対応するためにNumeric型を使用
    buy_time = db.Column(db.DateTime, nullable=False)  # nullable=TrueからFalseに変更

class Tax(db.Model):
    __tablename__ = 'tax'  # テーブル名を指定
    tax_id = db.Column(db.Integer, primary_key=True, nullable=False)
    tax_code = db.Column(db.Integer, unique=True, nullable=False)
    tax_name = db.Column(db.String(255), nullable=False)  # 長さを255に合わせる
    tax_percent = db.Column(db.Numeric(5, 2), nullable=False)  # MySQLのdecimal型に対応するためにNumeric型を使用

class Trades(db.Model):
    __tablename__ = 'trades'  # テーブル名を指定
    trade_id = db.Column(db.Integer, primary_key=True, nullable=False)
    buy_time = db.Column(db.DateTime, nullable=True)  # datetime型に変更、デフォルトをNULLに設定
    staff_id = db.Column(db.Integer, nullable=False)
    machine_id = db.Column(db.Integer, nullable=False)
    store_id = db.Column(db.String(255), nullable=False)  # varchar(255)に合わせてString型に変更
    total_charge = db.Column(db.Integer, nullable=False)
    total_charge_wo_tax = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=True)  # DEFAULT NULLに合わせてnullable=Trueに設定

# UTCで取得した日時をJSTに変換する関数
def to_jst(datetime_obj):
    utc_zone = pytz.utc
    jst_zone = pytz.timezone('Asia/Tokyo')
    return datetime_obj.replace(tzinfo=utc_zone).astimezone(jst_zone)



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
    return jsonify({"access_token": access_token, "user_name": user_name})


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
    tax = Tax.query.first()

    if product:
        # イベントが存在する場合、詳細情報を返す
        product_info = {
            "product_id" : product.product_id,
            "product_name" : product.product_name,
            "price" : product.price,
            "product_qrcode" : product.product_qrcode,
            "quantity" : product.quantity,
            "tax" :tax.tax_percent,
            }
        return jsonify(product_info)
    else:
        # ユーザーが存在しない場合
        return jsonify({"product_name":"商品がマスタ未登録です"})


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


@app.route('/trade', methods=['POST'])
def add_trade():
    # POSTされたデータを取得
    token  = request.json.get('token', None)
    user_info = Users.query.filter_by(token=token).first()
    user_id = user_info.user_id
    store_id = request.json.get('store_id', None)
    staff_id = request.json.get('staff_id', None)
    machine_id = request.json.get('machine_id', None)
    total_charge = request.json.get('total_charge', None)
    total_charge_wo_tax = request.json.get('total_charge_wo_tax', None)
    buy_time_str = request.json.get('buy_time', None)
    buy_time_utc = parser.isoparse(buy_time_str)  # タイムゾーン情報を含むUTC日時
    buy_time = to_jst(buy_time_utc)  # JSTに変換

    new_trade = Trades(user_id=user_id, store_id=store_id, staff_id=staff_id, machine_id=machine_id,
                    total_charge=total_charge, total_charge_wo_tax=total_charge_wo_tax, buy_time=buy_time,)

    # セッションに追加してコミット
    db.session.add(new_trade)
    db.session.commit()

    # 成功した場合は挿入されたトレードのIDを含むレスポンスを返す
    return jsonify({'trade_id': new_trade.trade_id}), 201


@app.route('/deal_detail', methods=['POST'])
def add_deal_detail():
    data = request.json
    for product in data['products']:
        # ISO形式の文字列からdatetimeオブジェクトに変換
        buy_time_str = product['buy_time']
        buy_time_utc = parser.isoparse(buy_time_str)
        buy_time_jst = to_jst(buy_time_utc)  # UTCからJSTに変換

        new_detail = Deal_Details(
            product_qrcode=product['product_qrcode'],
            product_name=product['product_name'],
            price=product['price'],
            quantity=product['quantity'],
            tax_percent=product['tax_percent'],
            event_id=1,  # 適切なevent_idの取り扱いを確認してください
            buy_time=buy_time_jst  # JSTに変換したdatetimeオブジェクトを使用
        )
        db.session.add(new_detail)
    db.session.commit()

    return jsonify({'message': 'Deal details added successfully'}), 201


if __name__ == "__main__":
    app.run(debug=True)