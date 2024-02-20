'use client';
import { useRef, useEffect, useState } from 'react';

export default function Login() {
    const formRef = useRef();
    const [userName, setUserName] = useState(''); // ユーザー名の状態を管理
    const [token, setToken] = useState(''); // ユーザー名の状態を管理

    const handleSend = async (event) => {
        event.preventDefault();
        const formData = new FormData(formRef.current);
        const body_msg = JSON.stringify({
            user_name: formData.get('user_name'),
            password: formData.get('password'),
        });

        const response = await fetch('http://127.0.0.1:8000/login', {
            method: 'POST',
            body: body_msg,
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (response.ok) {
            const jsonData = await response.json();
            setToken(jsonData.access_token);
            setUserName(jsonData.user_name);
            console.log(jsonData);
        } else {
            console.error('Login request failed:', response.statusText);
            window.alert(`Login request failed`);
        }
    };

    useEffect(() => {
        console.log(userName);

        // userNameが空でない場合のみ実行
        if (userName) {
            window.alert(`ようこそ ${userName}さま！`);
            window.location.href = `http://127.0.0.1:3000/shopping?token=${token}`;
        }
    }, [userName, token]); // userNameとtokenが変更されたときにのみ実行

    return (
        <>
            <div>
                <form ref={formRef} onSubmit={handleSend} style={{ width: '100%' }}>
                    <h1>Welcome back to Dagashiya!</h1>
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