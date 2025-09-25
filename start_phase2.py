#!/usr/bin/env python3
"""
PAM-TALK Phase 2 고성능 서버 실행기
Waitress + 고급 캐싱 + 백그라운드 태스크
"""

import os
import sys
import time
from waitress import serve
from phase2_server import app

def start_phase2_server():
    """Phase 2 최적화 서버 시작"""
    print("=" * 60)
    print("PAM-TALK Phase 2 고성능 서버 시작")
    print("=" * 60)

    print("Phase 2 최적화 기능:")
    print("  ✓ Waitress 프로덕션 WSGI 서버")
    print("  ✓ 고급 캐싱 시스템 (LRU, TTL)")
    print("  ✓ 백그라운드 태스크 처리")
    print("  ✓ 스레드 풀 최적화")
    print("  ✓ 연결 풀링")
    print("  ✓ 성능 모니터링")

    print(f"\n서버 설정:")
    print(f"  주소: http://127.0.0.1:5002")
    print(f"  스레드: 8개")
    print(f"  연결 제한: 1000개")
    print(f"  백그라운드 워커: 4개")

    print(f"\n주요 엔드포인트:")
    print(f"  /api/health       - 헬스 체크")
    print(f"  /api/farms        - 농장 관리")
    print(f"  /api/transactions - 거래 관리")
    print(f"  /api/dashboard    - 대시보드")
    print(f"  /api/cache/stats  - 캐시 통계")
    print(f"  /api/stress-test  - 성능 테스트")

    print("\n중지하려면 Ctrl+C를 누르세요")
    print("-" * 60)

    try:
        # Waitress 서버 시작
        serve(
            app,
            host='127.0.0.1',
            port=5002,
            threads=8,              # 8개 스레드
            connection_limit=1000,  # 최대 1000 연결
            cleanup_interval=30,    # 30초마다 정리
            channel_timeout=120,    # 2분 타임아웃
            log_socket_errors=True,
            url_scheme='http'
        )
    except KeyboardInterrupt:
        print("\n✓ Phase 2 서버가 정상적으로 종료되었습니다")
    except Exception as e:
        print(f"\n✗ 서버 시작 중 오류: {e}")

if __name__ == '__main__':
    start_phase2_server()