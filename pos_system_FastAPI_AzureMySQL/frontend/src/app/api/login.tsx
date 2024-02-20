// /pages/api/login.js
import fetch from 'node-fetch';
import { serialize } from 'cookie';

export default async (req, res) => {
  if (req.method === 'POST') {
    // フロントエンドからのリクエストボディをそのままFlaskサーバーへ転送
    const flaskResponse = await fetch('http://127.0.0.1:5000/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(req.body)
    });

    if (flaskResponse.ok) {
      const { access_token, user_name } = await flaskResponse.json();

      // FlaskからのレスポンスをもとにHttpOnlyクッキーをセット
      res.setHeader('Set-Cookie', [
        serialize('access_token', access_token, { path: '/', httpOnly: true, secure: process.env.NODE_ENV === 'production', sameSite: 'lax' }),
        serialize('user_name', user_name, { path: '/', httpOnly: true, secure: process.env.NODE_ENV === 'production', sameSite: 'lax' })
      ]);

      return res.status(200).json({ success: true });
    } else {
      // Flaskサーバーからエラーレスポンスが返された場合
      return res.status(flaskResponse.status).json({ message: 'Authentication failed' });
    }
  } else {
    // POSTメソッド以外のリクエストに対するレスポンス
    res.setHeader('Allow', ['POST']);
    return res.status(405).end('Method Not Allowed');
  }
};