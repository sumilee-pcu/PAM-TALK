#!/usr/bin/env python3
"""
PAM-TALK Windows용 최적화 서버 실행기
Gunicorn 대신 ThreadingWSGIServer와 캐싱으로 성능 최적화
"""

import threading
import time
from werkzeug.serving import ThreadingWSGIServer
from optimized_server import app

def run_optimized_server():
    """최적화된 서버 실행"""
    print("=" * 50)
    print("PAM-TALK 최적화 서버 시작")
    print("=" * 50)

    print("최적화 기능:")
    print("  - 멀티스레딩 서버")
    print("  - 메모리 캐싱 시스템")
    print("  - 응답시간 측정")
    print("  - 연결 풀링")

    # 스레딩 WSGI 서버 시작
    server = ThreadingWSGIServer(
        host='127.0.0.1',
        port=5001,  # 기존 서버와 다른 포트 사용
        app=app,
        threaded=True,
        processes=1,
        request_handler=None,
        passthrough_errors=False,
        ssl_context=None
    )

    print(f"\n서버 주소: http://127.0.0.1:5001")
    print("종료하려면 Ctrl+C를 누르세요")
    print("-" * 50)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n서버를 종료합니다...")
        server.shutdown()

if __name__ == '__main__':
    run_optimized_server()