#!/usr/bin/env python3
"""
PAM-TALK 최적화된 서버 시작 (Windows용)
"""

import subprocess
import sys
import time
import os

def start_optimized_server():
    """최적화된 서버 시작"""
    print("=" * 50)
    print("PAM-TALK 최적화 서버 시작")
    print("=" * 50)

    print("최적화 적용:")
    print("  ✓ 메모리 캐싱 시스템")
    print("  ✓ 응답시간 측정")
    print("  ✓ 데이터 크기 최적화")
    print("  ✓ 압축된 JSON 응답")

    # Flask 개발 서버의 스레딩 모드 활성화
    os.environ['FLASK_ENV'] = 'production'
    os.environ['FLASK_DEBUG'] = 'False'

    print("\n서버 주소: http://127.0.0.1:5001")
    print("중지하려면 Ctrl+C를 누르세요")
    print("-" * 50)

    # 최적화된 서버 실행
    try:
        from optimized_server import app
        app.run(
            host='127.0.0.1',
            port=5001,
            debug=False,
            threaded=True,
            use_reloader=False
        )
    except KeyboardInterrupt:
        print("\n✓ 서버가 정상적으로 종료되었습니다")

if __name__ == '__main__':
    start_optimized_server()