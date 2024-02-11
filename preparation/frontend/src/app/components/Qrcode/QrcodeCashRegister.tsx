'use client';
import { useEffect, useState } from 'react';
import QrcodeReader from './QrcodeReader';

export default function QrcodeReaderComponent() {
    const [scannedTime, setScannedTime] = useState(new Date());
    const [scannedResult, setScannedResult] = useState('');
    const [products, setProducts] = useState([]); // 商品を格納するための配列

    useEffect(() => {}, [scannedTime, scannedResult]);

    // QRコードを読み取った時の関数
    const onNewScanResult = (result: any) => {
        console.log('QRコードスキャン結果');
        console.log(result);
        setScannedTime(new Date());
        setScannedResult(result);
    };

    async function fetchProduct(scannedResult) {
        const encodedQrcode = encodeURIComponent(scannedResult);
        const res = await fetch(`http://127.0.0.1:5000/qrcode?qrcode=${encodedQrcode}`, { cache: "no-cache" });
        if (!res.ok) {
            throw new Error('Failed to fetch product');
        }
        return res.json();
    }

    useEffect(() => {
        const fetchAndSetProduct = async () => {
            const newProduct = await fetchProduct(scannedResult);
            // 既存のproducts配列に新しい商品を追加
            setProducts(prevProducts => [...prevProducts, newProduct]);
            setScannedResult('');
            console.log(newProduct);
            console.log(products);
        };
        
        if(scannedResult) {
            fetchAndSetProduct();
        }

    }, [scannedTime, scannedResult]);

    return (
        <>
            <div>
                <h2>スキャン日時：{scannedTime.toLocaleDateString()}</h2>
                <h2>スキャン結果：{scannedResult}</h2>
                {/* 商品と値段を表示 */}
                {products.map((product, index) => (
                    <div key={index}>
                        <h2>商品：{product.product_name} 値段：{product.price}円 個数：{product.quantity}個</h2>
                    </div>
                ))}
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