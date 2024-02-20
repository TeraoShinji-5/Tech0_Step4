'use client';
import { useRef } from 'react';
// import { useRouter } from 'next/router';
import { useCookies } from 'react-cookie';
import { useEffect, useState } from 'react';
import nookies from 'nookies';

export default function Login() {
    const formRef = useRef();
    // const [pastcookies, setPastCookie] = useCookies(['dummy']);
    // setPastCookie('dummy', 1);
    const [cookies, setCookie] = useCookies(['access_token', 'user_name']);
    const [userName, setUserName] = useState(''); // ユーザー名の状態を管理
    // const router = useRouter();

    const handleSend = async (event: any) => {
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
            setCookie('access_token', jsonData.access_token, { path: '/' });
            setCookie('user_name', jsonData.user_name, { path: '/' });
            setUserName(cookies.user_name);


        } else {
            console.error('Login request failed:', response.statusText);
            window.alert(`Login request failed`);
        }

    };

    useEffect(() => {
        console.log(userName);
        console.log(cookies);
    
        // cookies.user_nameが空でない場合のみ実行
        if (cookies.user_name) {
            window.alert(`ようこそ ${cookies.user_name}さま！`);
            // router.push("http://127.0.0.1:3000/shopping");
            window.location.href =`http://127.0.0.1:3000/shopping`;
        }
    
    }, [userName]);


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

export const getServerSideProps = async (context) => {
    const cookies = nookies.get(context);
    const accessToken = cookies['access_token'];

    // アクセストークンが存在する場合、ユーザーをショッピングページにリダイレクト
    if (accessToken) {
        return {
            redirect: {
                destination: '/shopping',
                permanent: false,
            },
        };
    }

    // アクセストークンが存在しない場合、ログインページをそのまま表示
    return { props: {} };
};