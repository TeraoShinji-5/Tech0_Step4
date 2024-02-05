"use client";// import先は適宜置き換えてください。
import React from 'react';
import QrcodeReaderComponent from './components/Qrcode/QrcodeReaderComponent';

export default function Home() {
  return (
      <main>
        <div>
          <QrcodeReaderComponent />
        </div>
      </main>
  );
}