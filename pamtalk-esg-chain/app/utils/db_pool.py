# -*- coding: utf-8 -*-
"""
데이터베이스 연결 풀링 및 성능 최적화
PostgreSQL 연결 풀을 사용한 효율적인 DB 관리
"""

import os
import threading
import time
from contextlib import contextmanager
from typing import Optional, Dict, Any

import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()


class DatabaseConnectionPool:
    """데이터베이스 연결 풀 관리자"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """싱글톤 패턴 구현"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """연결 풀 초기화"""
        if self._initialized:
            return

        self.db_config = {
            'host': os.getenv('DB_HOST'),
            'database': os.getenv('DB_NAME'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'port': '5432'
        }

        # 연결 풀 설정
        self.pool_config = {
            'minconn': int(os.getenv('DB_POOL_MIN', '2')),
            'maxconn': int(os.getenv('DB_POOL_MAX', '20')),
        }

        self._pool = None
        self._stats = {
            'total_connections': 0,
            'active_connections': 0,
            'pool_hits': 0,
            'pool_misses': 0,
            'connection_errors': 0
        }

        self._initialize_pool()
        self._initialized = True

    def _initialize_pool(self):
        """연결 풀 초기화"""
        try:
            self._pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=self.pool_config['minconn'],
                maxconn=self.pool_config['maxconn'],
                cursor_factory=RealDictCursor,
                **self.db_config
            )

            print(f"[DB 연결 풀 초기화 완료] "
                  f"최소: {self.pool_config['minconn']}, "
                  f"최대: {self.pool_config['maxconn']}")

        except Exception as e:
            print(f"[DB 연결 풀 초기화 실패] {str(e)}")
            raise

    @contextmanager
    def get_connection(self, timeout: int = 30):
        """연결 풀에서 연결 획득 (컨텍스트 매니저)"""
        connection = None
        start_time = time.time()

        try:
            # 연결 풀에서 연결 획득
            connection = self._pool.getconn()

            if connection is None:
                self._stats['pool_misses'] += 1
                raise Exception("연결 풀에서 연결을 획득할 수 없습니다")

            self._stats['pool_hits'] += 1
            self._stats['active_connections'] += 1

            # 연결 상태 확인
            if connection.closed:
                self._pool.putconn(connection)
                connection = self._pool.getconn()

            yield connection

        except Exception as e:
            self._stats['connection_errors'] += 1

            if connection:
                # 오류 발생 시 롤백
                try:
                    connection.rollback()
                except:
                    pass

            raise e

        finally:
            # 연결 반환
            if connection:
                try:
                    # 커밋되지 않은 트랜잭션 정리
                    if not connection.autocommit and connection.status == psycopg2.extensions.STATUS_IN_TRANSACTION:
                        connection.rollback()

                    self._pool.putconn(connection)
                    self._stats['active_connections'] -= 1

                except Exception as e:
                    print(f"[연결 반환 중 오류] {str(e)}")

    def execute_query(self, query: str, params: tuple = None, fetch: str = 'all') -> Any:
        """쿼리 실행 (연결 풀 사용)"""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)

                if fetch == 'all':
                    return cursor.fetchall()
                elif fetch == 'one':
                    return cursor.fetchone()
                elif fetch == 'many':
                    return cursor.fetchmany()
                else:
                    return cursor.rowcount

    def execute_transaction(self, queries: list) -> bool:
        """트랜잭션 실행 (여러 쿼리를 하나의 트랜잭션으로)"""
        with self.get_connection() as conn:
            try:
                with conn.cursor() as cursor:
                    for query_info in queries:
                        query = query_info['query']
                        params = query_info.get('params', None)
                        cursor.execute(query, params)

                conn.commit()
                return True

            except Exception as e:
                conn.rollback()
                print(f"[트랜잭션 실패] {str(e)}")
                raise

    def get_pool_stats(self) -> Dict[str, Any]:
        """연결 풀 통계"""
        if self._pool:
            return {
                **self._stats,
                'pool_size': len(self._pool._pool),
                'available_connections': len([conn for conn in self._pool._pool if not conn.closed])
            }
        return self._stats

    def health_check(self) -> Dict[str, Any]:
        """DB 연결 상태 확인"""
        try:
            with self.get_connection(timeout=5) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()

                    return {
                        'healthy': True,
                        'message': 'DB 연결 정상',
                        'response_time': time.time()
                    }

        except Exception as e:
            return {
                'healthy': False,
                'message': f'DB 연결 실패: {str(e)}',
                'response_time': None
            }

    def close_all_connections(self):
        """모든 연결 종료"""
        if self._pool:
            self._pool.closeall()
            print("[DB 연결 풀 종료 완료]")


class DatabaseService:
    """데이터베이스 서비스 클래스"""

    def __init__(self):
        self.pool = DatabaseConnectionPool()

    def get_committees(self, limit: int = 100) -> list:
        """위원회 목록 조회"""
        query = """
            SELECT id, name, wallet_address, created_at
            FROM committees
            ORDER BY created_at DESC
            LIMIT %s
        """
        return self.pool.execute_query(query, (limit,))

    def get_committee_by_id(self, committee_id: int) -> Optional[dict]:
        """위원회 정보 조회"""
        query = "SELECT * FROM committees WHERE id = %s"
        return self.pool.execute_query(query, (committee_id,), fetch='one')

    def get_token_statistics(self) -> dict:
        """토큰 통계 조회"""
        queries = [
            {
                'name': 'total_issued',
                'query': 'SELECT COUNT(*) as count FROM esg_coupons WHERE status != %s',
                'params': ('ISSUED',)
            },
            {
                'name': 'committee_tokens',
                'query': 'SELECT COUNT(*) as count FROM esg_coupons WHERE status = %s',
                'params': ('COMMITTEE',)
            },
            {
                'name': 'provider_tokens',
                'query': 'SELECT COUNT(*) as count FROM esg_coupons WHERE status = %s',
                'params': ('PROVIDER',)
            },
            {
                'name': 'consumer_tokens',
                'query': 'SELECT COUNT(*) as count FROM esg_coupons WHERE status = %s',
                'params': ('CONSUMER',)
            }
        ]

        stats = {}
        for query_info in queries:
            result = self.pool.execute_query(query_info['query'], query_info['params'], fetch='one')
            stats[query_info['name']] = result['count'] if result else 0

        return stats

    def bulk_insert_coupons(self, coupons_data: list) -> int:
        """대량 쿠폰 삽입 (배치 처리)"""
        if not coupons_data:
            return 0

        with self.pool.get_connection() as conn:
            try:
                with conn.cursor() as cursor:
                    # 배치 삽입 쿼리
                    insert_query = """
                        INSERT INTO esg_coupons
                        (coupon_code, asset_id, asset_name, mint_history_id,
                         status, created_at, updated_at)
                        VALUES %s
                    """

                    # psycopg2의 execute_values를 사용한 효율적인 배치 삽입
                    from psycopg2.extras import execute_values

                    execute_values(
                        cursor, insert_query, coupons_data,
                        template=None, page_size=1000
                    )

                    inserted_count = cursor.rowcount
                    conn.commit()

                    print(f"[배치 삽입 완료] {inserted_count}개 쿠폰")
                    return inserted_count

            except Exception as e:
                conn.rollback()
                print(f"[배치 삽입 실패] {str(e)}")
                raise


# 글로벌 DB 서비스 인스턴스
db_service = DatabaseService()


# 사용 예시
if __name__ == "__main__":
    # 연결 풀 상태 확인
    pool_stats = db_service.pool.get_pool_stats()
    print(f"연결 풀 통계: {pool_stats}")

    # 건강성 검사
    health = db_service.pool.health_check()
    print(f"DB 건강성: {health}")

    # 토큰 통계 조회
    try:
        stats = db_service.get_token_statistics()
        print(f"토큰 통계: {stats}")
    except Exception as e:
        print(f"통계 조회 실패: {e}")

    # 풀 종료
    # db_service.pool.close_all_connections()