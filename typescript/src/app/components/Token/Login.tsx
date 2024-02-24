'use client';
import { useRef, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';


export default function Login() {
    const formRef = useRef<HTMLFormElement>(null);
    const [userName, setUserName] = useState(''); // ユーザー名の状態を管理
    const [token, setToken] = useState(''); // ユーザー名の状態を管理
    const router = useRouter();

    const handleSend = async (event: any) => {
        event.preventDefault();

        // formRef.currentがnullでないことを確認
        if (formRef.current) {
            const formData = new FormData(formRef.current);
            const body_msg = JSON.stringify({
                user_name: formData.get('user_name'),
                password: formData.get('password'),
            });

            const response = await fetch('https://tech0-gen-5-step4-studentwebapp-7.azurewebsites.net/login', {
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
        }
    };

    useEffect(() => {
        console.log(userName);

        // userNameが空でない場合のみ実行
        if (userName) {
            window.alert(`ようこそ ${userName}さま！`);
            router.push(`/shopping?token=${token}`);
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