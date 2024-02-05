'use client';
import { useEffect, useState } from 'react';
import QrcodeReader from './QrcodeReader';

export default function QrcodeReaderComponent() {
    const [scannedTime, setScannedTime] = useState(new Date());
    const [scannedResult, setScannedResult] = useState('');
    const [dealDetails, setDealDetails] = useState([]);

    useEffect(() => {}, [scannedTime, scannedResult]);

    // QRコードを読み取った時の実行する関数
    const onNewScanResult = (result: any) => {
        console.log('QRコードスキャン結果');
        console.log(result);
        setScannedTime(new Date());
        setScannedResult(result);
    };

    const [product, setProduct] = useState([]); // 初期値を空の配列に変更

    async function fetchProduct(scannedResult) {
        const encodedQrcode = encodeURIComponent(scannedResult);
        const res = await fetch(`http://127.0.0.1:5000/qrcode?qrcode=${encodedQrcode}`, { cache: "no-cache" });
        if (!res.ok) {
            throw new Error('Failed to fetch user');
        }
        return res.json();
    }

    useEffect(() => {
        const fetchAndSetProduct = async () => {
        const product = await fetchProduct(scannedResult);
        setProduct(product);
        console.log(product);
        }
        
        fetchAndSetProduct();

    }, [scannedTime, scannedResult]);

    const handleSubmit = async (event: any) => {
        event.preventDefault(); // フォームのデフォルトの送信を防ぎます
        const response = await fetch('http://127.0.0.1:5000/add_product', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                product_id: product.product_id,
                product_name: product.product_name,
                price: product.price,
                quantity: product.quantity,
                }),
            });
            if (!response.ok) {
                throw new Error('Product could not be added');
            }
            const data = await response.json();
            setDealDetails(data); // レスポンスデータで状態を更新
            console.log(dealDetails);
        };

        return (
            <>
                {/* フェッチしたデータのリスト表示 */}
                {dealDetails.map((deal, index) => (
                    <div key={index}>
                        <h2>商品No.：{deal.product_id} 商品名：{deal.product_name} 値段：{deal.price}円 個数：{deal.quantity}個</h2>
                    </div>
                ))}
                <div>
                    <h2>スキャン日時：{scannedTime.toLocaleDateString()}</h2>
                    <h2>スキャン結果：{scannedResult}</h2>
                    <h2>商品名：{product.product_name}</h2>
                    <h2>値段：{product.price}円</h2>
                    <h2>個数：{product.quantity}個</h2>
                </div>
                <form onSubmit={handleSubmit}>
                    <button type="submit">追加</button>
                </form>
                <QrcodeReader
                    onScanSuccess={onNewScanResult}
                    onScanFailure={(error: any) => {}}
                />
            </>
        );
}
