'use client';
import React, { useState, useEffect } from 'react';
import { BarcodeDetector } from '@zxing/library/esm/browser';

const App = () => {
  const [barcodeText, setBarcodeText] = useState('');
  const [videoRef, setVideoRef] = useState(null);

  useEffect(() => {
    const detector = new BarcodeDetector();

    const startCamera = async () => {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      videoRef.current.srcObject = stream;

      detector.decodeFromVideoStream(videoRef.current, (results) => {
        if (results.length > 0) {
          setBarcodeText(results[0].text);
        }
      });
    };

    startCamera();

    return () => {
      stream.getTracks().forEach((track) => track.stop());
    };
  }, []); // 依存関係配列を空の配列に修正

  return (
    <div>
      <video ref={setVideoRef} width="640" height="480" />
      <p>{barcodeText}</p>
    </div>
  );
};

export default App;

