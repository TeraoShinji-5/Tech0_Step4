"use client";// import先は適宜置き換えてください。
import React from 'react';
import QrcodeCashRegister2 from './components/Qrcode/QrcodeCashRegister2';

export default function Home() {
  return (
      <main>
        <div>
          <QrcodeCashRegister2 />
        </div>
      </main>
  );
}