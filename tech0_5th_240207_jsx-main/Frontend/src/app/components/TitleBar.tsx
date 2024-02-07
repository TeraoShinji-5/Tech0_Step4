import React from 'react';
import Image from 'next/image'
import tech0Icon from '../../../public/images/tech0.png'; // 正しいパスにしてください
import Link from 'next/link'; // Next.jsのLinkコンポーネントをインポート

const TitleBar = () => {
  return (
    <div className="mx-10 my-4 flex items-center justify-between"  style={{ borderBottom: '3px solid #007bff' }}>
    {/* 左のアイコン */}
        <div className="flex-1" style={{ flex: 1, display: 'flex', justifyContent: 'flex-end' }}> {/* 25% width */}
        <Image src={tech0Icon} alt="Tech Icon" width={130} height={130} />
        </div>
        
        {/* 中央のタイトル */}
        <div className="flex-1" style={{ flex: 2, display: 'flex', justifyContent: 'center' }}> {/* 50% width */}
        <h1 className="text-black text-3xl font-bold">
            Tech0 STEP4 POSアプリ
        </h1>
        </div>
    
        {/* 右のテキスト */}
        <Link href="/contact" className="flex-1 text-black-600 font-bold hover:underline" style={{ flex: 1 }}> {/* 25% width */}
        {/* <a className="text-sky-600 hover:underline">Contact</a> */}
        Contact
        </Link>
    </div>
  );
};

export default TitleBar;
