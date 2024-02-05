'use client';
import { useEffect, useState } from 'react';
import QrcodeReader from './QrcodeReader';

export default function QrcodeReaderComponent() {
    const [scannedTime, setScannedTime] = useState(new Date());
    const [scannedResult, setScannedResult] = useState('');

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

    return (
        <>
        <div>
            <h2>スキャン日時：{scannedTime.toLocaleDateString()}</h2>
            <h2>スキャン結果：{scannedResult}</h2>
            <h2>商品：{product.product_name}</h2>
            <h2>値段：{product.price}円</h2>
        </div>
        <QrcodeReader
            onScanSuccess={onNewScanResult}
            onScanFailure={(error: any) => {
            // console.log('Qr scan error');
            }}
        />
        </>
    );
}
