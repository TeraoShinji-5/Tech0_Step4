'use client';
import { useEffect, useState } from 'react';
import QrcodeReader from './QrcodeReader';
import { useSearchParams } from 'next/navigation';


export default function QrcodeReaderComponent() {
    const [scannedTime, setScannedTime] = useState(new Date());
    const [scannedResult, setScannedResult] = useState('');
    const [products, setProducts] = useState([]); // 商品を格納するための配列
    const [newProduct, setNewProduct] = useState({}); // 商品を格納するための配列
    const [quantity, setQuantity] = useState(''); // newProduct.quantityを管理するためのローカルステートを追加
    const [productTax, setProductTax] = useState(0.1); // 税率を格納するための配列
    const [total, setTotal] = useState(0); // 税抜き合計金額を保持するステート
    const [totalWithTax, setTotalWithTax] = useState(0); // 税込み合計金額を保持するステート
    const [userName, setUserName] = useState(''); // ユーザー名の状態を管理
    const [token, setToken] = useState(''); // ユーザー名の状態を管理
    const user_token = useSearchParams().get("token");


    async function fetchUser(token: string) {
        const res = await fetch(`http://127.0.0.1:8000/shopping?token=${user_token}`, { cache: "no-cache" });
        if (!res.ok) {
            throw new Error('Failed to fetch user');
        }
        return res.json();
    }

    useEffect(() => {
        const fetchAndSetUser = async () => {
        const userData = await fetchUser(token);
        setUserName(userData.user_name);
        setToken(user_token);
        console.log(userData);
        };
        fetchAndSetUser();
    }, []);


    // QRコードを読み取った時の関数
    const onNewScanResult = (result: any) => {
        console.log('QRコードスキャン結果');
        console.log(result);
        setScannedTime(new Date());
        setScannedResult(result);
    };

    // QRコードから商品情報を渡す関数
    async function fetchProduct(scannedResult) {
        const encodedQrcode = encodeURIComponent(scannedResult);
        const res = await fetch(`http://127.0.0.1:8000/qrcode?qrcode=${encodedQrcode}`, { cache: "no-cache" });
        if (!res.ok) {
            throw new Error('Failed to fetch product');
        }
        return res.json();
    }

    // 商品情報を購入リストに入れる関数
    useEffect(() => {
        const fetchAndSetProduct = async () => {
            try {
                const newProduct = await fetchProduct(scannedResult);
                setNewProduct(newProduct);
                console.log(newProduct);
                setProducts(prevProducts => {
                    // 既存のproducts配列でproduct_idが一致する商品を探す
                    const existingProductIndex = prevProducts.findIndex(p => p.product_id === newProduct.product_id);
                    if (existingProductIndex !== -1) {
                        // 一致する商品があれば、quantityを更新する
                        const updatedProducts = [...prevProducts];
                        updatedProducts[existingProductIndex] = {
                            ...updatedProducts[existingProductIndex],
                            quantity: updatedProducts[existingProductIndex].quantity + 1,
                        };
                        return updatedProducts;
                    } else {
                        // 新しい商品を追加する（初期個数を設定）
                        return [...prevProducts, { ...newProduct, quantity: 1 }];
                    }
                });
                setScannedResult('');
            } catch (error) {
                console.error("Failed to fetch and set product:", error);
            }
        };

        if(scannedResult) {
            fetchAndSetProduct();
        }
    }, [scannedTime, scannedResult]);

    // 合計金額の表示
    useEffect(() => {
        // 税抜き合計金額を計算
        const newTotal = products.reduce((sum, product) => sum + product.price * product.quantity, 0);

        // 税込み合計金額を計算し、小数点第一位で四捨五入
        let newTotalWithTax = newTotal; // 初期値を税抜き合計金額として設定

        if (newProduct.tax !== undefined) { // newProduct.taxがundefinedでない場合にのみ再計算
            newTotalWithTax = products.reduce((sum, product) =>
                sum + Math.round((product.price * product.quantity * (1 + productTax)) * 10) / 10, 0);
        }

        setTotal(Math.round(newTotal)); // 税抜き合計金額をステートにセット
        setTotalWithTax(Math.round(newTotalWithTax)); // 税込み合計金額をステートにセット
    }, [products, newProduct.tax]); // products配列かnewProduct.taxが変わるたびに再計算


    // 商品情報をnewProductにセットする関数
    const handleSetNewProduct = (product: any) => {
        setProductTax(product.tax);
        setNewProduct(product);
        console.log(newProduct);
        // newProductが更新されたらquantityも更新する
        setQuantity(product.quantity.toString());
    };

    // 選択されている商品を削除する関数
    const handleRemoveProduct = () => {
        setProducts(prevProducts => prevProducts.filter(product => product.product_id !== newProduct.product_id));
        setNewProduct({}); // newProductを空にリセット
        console.log(newProduct);
    }

    // 選択されている商品の数量を更新する関数
    const handleQuantityChange = (event: any) => {
        setQuantity(event.target.value);
    };

    // 数量の入力が完了したときに呼ばれる関数
    const handleQuantityBlur = () => {
        const updatedQuantity = parseInt(quantity, 10);

        // 数量が有効な数値でない場合は、処理を終了
        if (isNaN(updatedQuantity) || updatedQuantity < 0) {
            console.error("Invalid quantity input");
            return;
        }

        setProducts(prevProducts =>
            prevProducts.map(product =>
                product.product_id === newProduct.product_id
                    ? { ...product, quantity: updatedQuantity }
                    : product
            )
        );

        // newProductの数量も更新
        setNewProduct(prevNewProduct => ({ ...prevNewProduct, quantity: updatedQuantity }));
        console.log(newProduct);
    };

    // newProduct.quantityをquantityステートにセットする関数
    const handleEditQuantity = () => {
        setQuantity(newProduct.quantity.toString());
    };

    // newProductが更新されたときにquantityステートも更新する
    useEffect(() => {
        if (newProduct && newProduct.quantity !== undefined) {
            setQuantity(newProduct.quantity.toString());
        }
    }, [newProduct]);

    // 日本時間に変換するための関数
    function getJSTDate() {
        const now = new Date();
        const utc = now.getTime() + (now.getTimezoneOffset() * 60000);
        const jstOffset = 9
         * 60 * 60000; // JSTはUTC+9時間
        return new Date(utc + jstOffset);
    }

    const handlePurchase = async () => {
        // 日本時間の現在時刻を取得
        const currentTime = getJSTDate();

        // ポップアップで合計金額を表示
        window.alert(`合計(税込): ${totalWithTax}円 (税抜: ${total}円)`);

        // TradeDBにデータを保存する
        try {
            // トレード情報を保存
            await fetchAndSetTrade(currentTime);

            // ディール詳細を保存
            await fetchAndDealDetail(currentTime);
        } catch (error) {
            console.error("An error occurred during the purchase process:", error);
        }

        // すべての状態をクリア
        setProducts([]);
        setNewProduct({});
        setQuantity('');
        setProductTax(0.1);
        setTotal(0);
        setTotalWithTax(0);
        setUserName('ゲスト');
        setToken('');
    };

    // トレード情報を保存する関数
    const fetchAndSetTrade = async (buyTime: Date) => {
        // buyTimeをISO文字列に変換
        const buyTimeString = buyTime.toISOString();

        const response = await fetch('http://127.0.0.1:8000/trade', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                token: token,
                store_id: 1,
                staff_id: 1,
                machine_id: 1,
                total_charge: totalWithTax,
                total_charge_wo_tax: total,
                buy_time: buyTimeString,
            }),
        });
        if (!response.ok) {
            throw new Error('Trade could not be added');
        }
        const data = await response.json();
        console.log(data);
    };

    // ディール詳細を保存する関数
    const fetchAndDealDetail = async (buyTime: Date) => {
        // buyTimeをISO文字列に変換
        const buyTimeString = buyTime.toISOString();

        const response = await fetch('http://127.0.0.1:8000/deal_detail', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                products: products.map(product => ({
                    product_qrcode: product.product_qrcode,
                    product_name: product.product_name,
                    price: product.price,
                    quantity: product.quantity,
                    tax_percent: productTax,
                    buy_time: buyTimeString,
                }))
            }),
        });
        if (!response.ok) {
            throw new Error('Deal Detail could not be added');
        }
        const data = await response.json();
        console.log(data);
    };

    return (
        <>
        <div>ようこそ {userName}さん！</div>
            <div>
                <h2>スキャン日時：{scannedTime.toLocaleDateString()}</h2>
                <h2>スキャン結果：{newProduct.product_id}</h2>
                <h2>商品名：{newProduct.product_name}</h2>
                <h2>値段：{newProduct.price}円</h2>
                <h2>
                    個数：
                    {newProduct.quantity !== undefined ? (
                        <>
                            <input
                                type="number"
                                value={quantity}
                                onChange={handleQuantityChange}
                                onBlur={handleQuantityBlur}
                                min="1"
                                max="99"
                                style={{ width: '3em' }}
                            />
                            <button onClick={handleEditQuantity}>数量変更</button> {/* 数量変更ボタン */}
                        </>
                    ) : (
                        '商品を選択してください。'
                    )}
                </h2>
                <button onClick={handleRemoveProduct}>リストから削除</button> {/* 削除ボタン */}

                {/* 商品と値段を表示 */}
                {products.map((product, index) => (
                    <div key={index}>
                        <h2>
                            {product.product_name}    {product.price}円    x{product.quantity}個    {product.price * product.quantity}円
                            <span style={{ marginLeft: '20px' }}> {/* ここで間隔を調整します */}
                                <button onClick={() => handleSetNewProduct(product)}>選択</button>
                            </span>
                        </h2>
                    </div>
                ))}
            </div>
            {/* 合計金額を表示 */}
            <h2>合計:{totalWithTax} 円 （税抜: {total} 円）</h2>
            <button onClick={handlePurchase}>購入</button>
            <QrcodeReader
                onScanSuccess={onNewScanResult}
                onScanFailure={(error: any) => {
                    // console.log('Qr scan error');
                }}
            />
        </>
    );
}




