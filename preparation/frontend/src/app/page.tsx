"use client";// import先は適宜置き換えてください。
import React from 'react';
import QrcodeCashRegister3 from './components/Qrcode/QrcodeCashRegister3';

export default function Home() {
  return (
      <main>
        <div>
          <QrcodeCashRegister3 />
        </div>
      </main>
  );
}