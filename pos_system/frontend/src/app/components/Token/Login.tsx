'use client';
import { useRef } from 'react';
import { useCookies } from 'react-cookie';

export default function Login() {
    const formRef = useRef();
    const [cookies, setCookie] = useCookies(['access_token', 'user_name']);

    const handleSend = async (event: any) => {
        event.preventDefault();
        const formData = new FormData(formRef.current);
        const body_msg = JSON.stringify({
            user_name: formData.get('user_name'),
            password: formData.get('password'),
        });

    const response = await fetch('http://127.0.0.1:5000/login', {
        method: 'POST',
        body: body_msg,
        headers: {
            'Content-Type': 'application/json',
        },
    });

    if (response.ok) {
        const jsonData = await response.json();
        setCookie('access_token', jsonData.access_token, { path: '/' });
        setCookie('user_name', jsonData.user_name, { path: '/' });
        window.location.href =`http://127.0.0.1:3000/shopping`;
    } else {
        console.error('Login request failed:', response.statusText);
        // ユーザーフレンドリーなエラーメッセージを表示したり、他の処理を行う
    }
    };

    return (
    <>
        <div>
        <form ref={formRef} onSubmit={handleSend} style={{ width: '100%' }}>
            <h1>Welcome back to dagashiya!</h1>
            <div>
            <label>
                ユーザー名:
                <input name="user_name" type="text" />
            </label>
            </div>
            <div>
            <label>
                パスワード：
                <input name="password" type="password" />
            </label>
            </div>
            <button type="submit">SIGN IN</button>
        </form>
        </div>
    </>
    );
}