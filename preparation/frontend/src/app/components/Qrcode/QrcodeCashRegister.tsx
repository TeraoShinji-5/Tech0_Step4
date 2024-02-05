'use client';
import { useEffect, useState } from 'react';
import QrcodeReader from './QrcodeReader';



export default function QrcodeReaderComponent3() {
    const [scannedTime, setScannedTime] = useState(new Date());
    const [scannedResult, setScannedResult] = useState('');
    const [product, setProduct] = useState([]); // 初期値を空の配列に変更

    // QRコードを読み取った時の実行する関数
    const onNewScanResult = (result: any) => {
        console.log('QRコードスキャン結果');
        console.log(result);
        setScannedTime(new Date());
        setScannedResult(result);
    };


    async function fetchProduct(scannedResult) {
        const encodedQrcode = encodeURIComponent(scannedResult);
        const res = await fetch(`http://127.0.0.1:5000/product?product_qrcode=${encodedQrcode}`, { cache: "no-cache" });
        if (!res.ok) {
            throw new Error('Failed to fetch product');
        }
        return res.json();
    };

    useEffect(() => {
        const fetchAndSetProduct = async () => {
        const productData = await fetchProduct(scannedResult);
        setProduct(productData);
        console.log(product);
        }
        fetchAndSetProduct();

    }, [scannedTime, scannedResult]);

    return (
        <>
        <div>
            <h2>スキャン日時：{scannedTime.toLocaleDateString()}</h2>
            <h2>スキャン結果：{scannedResult}</h2>
            {/* <h2>ようこそ{user.user_name}さん！</h2> */}
        </div>
        </>
    );
};
