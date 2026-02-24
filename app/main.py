from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.core.config import settings
from app.core.exceptions import validation_exception_handler, global_exception_handler
from app.api.v1 import auth, rooms, chat, users

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="ChatApp API",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(rooms.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(chat.router)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def landing():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ChatApp</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', sans-serif;
            background: #07070f;
            color: #fff;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            overflow-x: hidden;
        }
        .glow-1 {
            position: fixed;
            width: 700px; height: 700px;
            background: radial-gradient(circle, rgba(124,58,237,0.12) 0%, transparent 70%);
            top: -200px; left: -200px;
            pointer-events: none;
            animation: g1 10s ease-in-out infinite;
        }
        .glow-2 {
            position: fixed;
            width: 600px; height: 600px;
            background: radial-gradient(circle, rgba(236,72,153,0.08) 0%, transparent 70%);
            bottom: -150px; right: -150px;
            pointer-events: none;
            animation: g2 12s ease-in-out infinite;
        }
        @keyframes g1 {
            0%,100% { transform: translate(0,0); }
            50% { transform: translate(40px,40px); }
        }
        @keyframes g2 {
            0%,100% { transform: translate(0,0); }
            50% { transform: translate(-30px,-30px); }
        }
        body::before {
            content: '';
            position: fixed;
            inset: 0;
            background-image:
                linear-gradient(rgba(255,255,255,0.015) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255,255,255,0.015) 1px, transparent 1px);
            background-size: 64px 64px;
            pointer-events: none;
            z-index: 0;
        }
        nav {
            position: relative;
            z-index: 10;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 20px 48px;
            border-bottom: 1px solid rgba(255,255,255,0.04);
        }
        .logo {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 17px;
            font-weight: 700;
            color: #fff;
            text-decoration: none;
        }
        .nav-right { display: flex; align-items: center; gap: 6px; }
        .nav-btn {
            padding: 8px 18px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 500;
            text-decoration: none;
            transition: all 0.15s;
        }
        .nav-ghost { color: #6b7280; }
        .nav-ghost:hover { color: #fff; background: rgba(255,255,255,0.05); }
        .nav-solid { background: #7c3aed; color: #fff; }
        .nav-solid:hover { background: #6d28d9; }
        .hero {
            position: relative;
            z-index: 10;
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            padding: 100px 24px 60px;
        }
        .pill {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(124,58,237,0.12);
            border: 1px solid rgba(124,58,237,0.25);
            color: #a78bfa;
            padding: 5px 14px;
            border-radius: 100px;
            font-size: 12px;
            font-weight: 500;
            margin-bottom: 28px;
        }
        .pill-dot {
            width: 5px; height: 5px;
            background: #a78bfa;
            border-radius: 50%;
            animation: blink 2s infinite;
        }
        @keyframes blink {
            0%,100% { opacity: 1; }
            50% { opacity: 0.3; }
        }
        h1 {
            font-size: clamp(40px, 5.5vw, 76px);
            font-weight: 800;
            letter-spacing: -2.5px;
            line-height: 1.05;
            margin-bottom: 20px;
            max-width: 720px;
        }
        .grad {
            background: linear-gradient(135deg, #7c3aed, #a855f7 45%, #ec4899);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .sub {
            font-size: 16px;
            color: #4b5563;
            line-height: 1.7;
            max-width: 400px;
            margin-bottom: 40px;
        }
        .cta { display: flex; gap: 10px; margin-bottom: 72px; }
        .cta-primary {
            padding: 13px 28px;
            background: #7c3aed;
            color: #fff;
            border-radius: 10px;
            font-size: 14px;
            font-weight: 600;
            text-decoration: none;
            transition: all 0.15s;
            box-shadow: 0 0 24px rgba(124,58,237,0.35);
        }
        .cta-primary:hover {
            background: #6d28d9;
            transform: translateY(-1px);
            box-shadow: 0 0 36px rgba(124,58,237,0.5);
        }
        .cta-secondary {
            padding: 13px 28px;
            background: rgba(255,255,255,0.04);
            color: #9ca3af;
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 10px;
            font-size: 14px;
            font-weight: 500;
            text-decoration: none;
            transition: all 0.15s;
        }
        .cta-secondary:hover {
            background: rgba(255,255,255,0.07);
            color: #fff;
            transform: translateY(-1px);
        }
        .preview {
            width: 100%;
            max-width: 660px;
            border-radius: 18px;
            overflow: hidden;
            border: 1px solid rgba(255,255,255,0.07);
            background: rgba(255,255,255,0.02);
            backdrop-filter: blur(20px);
            box-shadow: 0 32px 80px rgba(0,0,0,0.5), 0 0 0 1px rgba(124,58,237,0.08);
        }
        .preview-bar {
            display: flex;
            align-items: center;
            gap: 6px;
            padding: 12px 18px;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            background: rgba(255,255,255,0.01);
        }
        .dot { width: 9px; height: 9px; border-radius: 50%; }
        .preview-inner { display: flex; height: 260px; }
        .p-sidebar {
            width: 150px;
            border-right: 1px solid rgba(255,255,255,0.05);
            padding: 14px 10px;
            flex-shrink: 0;
        }
        .p-label {
            font-size: 9px;
            color: #374151;
            font-weight: 600;
            letter-spacing: 1.2px;
            text-transform: uppercase;
            padding: 0 8px;
            margin-bottom: 6px;
        }
        .p-ch {
            padding: 5px 8px;
            border-radius: 5px;
            font-size: 11px;
            color: #4b5563;
            display: flex;
            align-items: center;
            gap: 5px;
            margin-bottom: 1px;
        }
        .p-ch.on { background: rgba(124,58,237,0.18); color: #a78bfa; }
        .p-online {
            display: flex;
            align-items: center;
            gap: 5px;
            padding: 4px 8px;
            font-size: 11px;
            color: #374151;
        }
        .online-dot { width: 5px; height: 5px; background: #10b981; border-radius: 50%; }
        .p-chat {
            flex: 1;
            padding: 14px;
            display: flex;
            flex-direction: column;
            gap: 10px;
            overflow: hidden;
        }
        .p-msg {
            display: flex;
            gap: 7px;
            opacity: 0;
            animation: rise 0.4s ease forwards;
        }
        .p-msg.r { flex-direction: row-reverse; }
        .p-msg:nth-child(1) { animation-delay: 0.4s; }
        .p-msg:nth-child(2) { animation-delay: 1.0s; }
        .p-msg:nth-child(3) { animation-delay: 1.6s; }
        .p-msg:nth-child(4) { animation-delay: 2.2s; }
        @keyframes rise {
            from { opacity: 0; transform: translateY(8px); }
            to   { opacity: 1; transform: translateY(0); }
        }
        .p-av {
            width: 24px; height: 24px;
            border-radius: 50%;
            font-size: 10px;
            font-weight: 700;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }
        .p-bub {
            padding: 7px 11px;
            border-radius: 10px;
            font-size: 11px;
            line-height: 1.5;
            max-width: 170px;
        }
        .p-bub.other {
            background: rgba(255,255,255,0.05);
            color: #9ca3af;
            border-radius: 2px 10px 10px 10px;
        }
        .p-bub.me {
            background: rgba(124,58,237,0.35);
            color: #ddd6fe;
            border-radius: 10px 2px 10px 10px;
        }
        footer {
            position: relative;
            z-index: 10;
            padding: 20px 48px;
            border-top: 1px solid rgba(255,255,255,0.04);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .f-left { font-size: 12px; color: #1f2937; }
        .f-right { display: flex; gap: 20px; }
        .f-link {
            font-size: 12px;
            color: #374151;
            text-decoration: none;
            transition: color 0.15s;
        }
        .f-link:hover { color: #a78bfa; }
        @media (max-width: 600px) {
            nav { padding: 16px 20px; }
            h1 { letter-spacing: -1.5px; }
            .p-sidebar { display: none; }
            footer { padding: 16px 20px; flex-direction: column; gap: 12px; }
        }
    </style>
</head>
<body>
    <div class="glow-1"></div>
    <div class="glow-2"></div>

    <nav>
        <a href="/" class="logo">💬 ChatApp</a>
        <div class="nav-right">
            <a href="https://github.com/tishuu03/chat_app" target="_blank" class="nav-btn nav-ghost">GitHub</a>
            <a href="http://localhost:5173" class="nav-btn nav-solid">Open App →</a>
        </div>
    </nav>

    <div class="hero">
        <div class="pill">
            <div class="pill-dot"></div>
            Live · Real-time
        </div>

        <h1>The chat app<br>built <span class="grad">differently</span></h1>

        <p class="sub">
            Real-time messaging with WebSockets, Redis presence tracking, and JWT auth. Fast by design.
        </p>

        <div class="cta">
            <a href="http://localhost:5173" class="cta-primary">Start chatting →</a>
            <a href="https://github.com/tishuu03/chat_app" target="_blank" class="cta-secondary">⭐ GitHub</a>
        </div>

        <div class="preview">
            <div class="preview-bar">
                <div class="dot" style="background:#ef4444"></div>
                <div class="dot" style="background:#f59e0b"></div>
                <div class="dot" style="background:#10b981"></div>
            </div>
            <div class="preview-inner">
                <div class="p-sidebar">
                    <div class="p-label">Channels</div>
                    <div class="p-ch on"># general</div>
                    <div class="p-ch"># random</div>
                    <div class="p-ch"># dev</div>
                    <div class="p-label" style="margin-top:14px">Online</div>
                    <div class="p-online"><div class="online-dot"></div>tisha</div>
                    <div class="p-online"><div class="online-dot"></div>john</div>
                </div>
                <div class="p-chat">
                    <div class="p-msg">
                        <div class="p-av" style="background:rgba(124,58,237,0.25);color:#a78bfa">J</div>
                        <div class="p-bub other">Is the new feature live? 🚀</div>
                    </div>
                    <div class="p-msg r">
                        <div class="p-av" style="background:rgba(236,72,153,0.25);color:#f9a8d4">T</div>
                        <div class="p-bub me">Deployed 5 mins ago ✅</div>
                    </div>
                    <div class="p-msg">
                        <div class="p-av" style="background:rgba(124,58,237,0.25);color:#a78bfa">J</div>
                        <div class="p-bub other">Real-time sync is insane 🔥</div>
                    </div>
                    <div class="p-msg r">
                        <div class="p-av" style="background:rgba(236,72,153,0.25);color:#f9a8d4">T</div>
                        <div class="p-bub me">WebSockets + Redis 😄</div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <footer>
        <div class="f-left">Built by Tisha · FastAPI + WebSockets + Redis</div>
        <div class="f-right">
            <a href="https://github.com/tishuu03/chat_app" target="_blank" class="f-link">GitHub</a>
        </div>
    </footer>
</body>
</html>
    """


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": "1.0.0"
    }