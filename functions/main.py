from firebase_functions import https_fn, options
import firebase_admin
from firebase_admin import initialize_app
from fastapi import FastAPI
import asyncio
import json

# Firebase Admin 초기화 (중복 방지)
if not firebase_admin._apps:
    initialize_app()

# 전역 지역 설정 (서울)
options.set_global_options(region="asia-northeast3")

# FastAPI 앱 생성
app = FastAPI()

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

@https_fn.on_request()
def fastapi_handler(req: https_fn.Request) -> https_fn.Response:
    """
    수동 ASGI 어댑터 구현
    Firebase Functions v2에서 FastAPI를 실행하기 위해 ASGI 프로토콜을 직접 구현
    """
    try:
        # ASGI scope 구성
        asgi_request = {
            "type": "http",
            "method": req.method,
            "path": req.path,
            "headers": [(k.lower().encode(), v.encode()) for k, v in req.headers.items()],
            "query_string": req.query_string or b"",
        }

        # ASGI receive 함수
        async def receive():
            return {"type": "http.request", "body": req.get_data() or b"", "more_body": False}

        # 응답 데이터 수집
        response_body, response_headers, response_status = [], [], 200

        # ASGI send 함수
        async def send(message):
            nonlocal response_body, response_headers, response_status
            if message["type"] == "http.response.start":
                response_status = message.get("status", 200)
                response_headers = message.get("headers", [])
            elif message["type"] == "http.response.body":
                response_body.append(message.get("body", b""))

        # FastAPI를 asyncio로 실행
        async def run_asgi():
            await app(asgi_request, receive, send)

        asyncio.run(run_asgi())

        # 응답 조합
        full_body = b"".join(response_body)
        headers_dict = {
            k.decode() if isinstance(k, bytes) else k: v.decode() if isinstance(v, bytes) else v
            for k, v in response_headers
        }

        return https_fn.Response(response=full_body, status=response_status, headers=headers_dict)

    except Exception as e:
        return https_fn.Response(
            response=json.dumps({"error": f"Internal Server Error: {str(e)}"}),
            status=500,
            headers={"Content-Type": "application/json"},
        )