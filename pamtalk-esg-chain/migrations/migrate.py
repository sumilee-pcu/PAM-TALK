#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PAM-TALK ESG Chain Database Migration Tool
Usage: python migrate.py [up|down|status]
"""

import os
import sys
import psycopg2
from pathlib import Path
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'port': '5432'
}

MIGRATIONS_DIR = Path(__file__).parent

def get_db_connection():
    """데이터베이스 연결"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        return conn
    except psycopg2.Error as e:
        print(f"❌ 데이터베이스 연결 실패: {e}")
        sys.exit(1)

def create_migration_table(conn):
    """마이그레이션 추적 테이블 생성"""
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version VARCHAR(50) PRIMARY KEY,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                description TEXT
            )
        """)
    print("✅ 마이그레이션 추적 테이블 생성/확인 완료")

def get_applied_migrations(conn):
    """적용된 마이그레이션 목록 조회"""
    with conn.cursor() as cur:
        cur.execute("SELECT version FROM schema_migrations ORDER BY version")
        return [row[0] for row in cur.fetchall()]

def get_pending_migrations(applied_versions):
    """적용되지 않은 마이그레이션 목록"""
    migration_files = sorted([f for f in MIGRATIONS_DIR.glob("*.sql") if f.name.startswith(('001_', '002_', '003_'))])
    pending = []

    for migration_file in migration_files:
        version = migration_file.stem.split('_')[0]
        if version not in applied_versions:
            pending.append((version, migration_file))

    return pending

def apply_migration(conn, version, migration_file):
    """마이그레이션 적용"""
    print(f"📦 적용 중: {migration_file.name}")

    try:
        with conn.cursor() as cur:
            # SQL 파일 읽기 및 실행
            sql_content = migration_file.read_text(encoding='utf-8')
            cur.execute(sql_content)

            # 마이그레이션 기록
            description = f"Applied {migration_file.name}"
            cur.execute(
                "INSERT INTO schema_migrations (version, description) VALUES (%s, %s)",
                (version, description)
            )

        print(f"✅ 완료: {migration_file.name}")

    except psycopg2.Error as e:
        print(f"❌ 마이그레이션 실패 {migration_file.name}: {e}")
        conn.rollback()
        sys.exit(1)

def migrate_up():
    """마이그레이션 적용"""
    print("🚀 데이터베이스 마이그레이션 시작")

    conn = get_db_connection()
    create_migration_table(conn)

    applied_versions = get_applied_migrations(conn)
    pending_migrations = get_pending_migrations(applied_versions)

    if not pending_migrations:
        print("✅ 적용할 마이그레이션이 없습니다.")
        return

    print(f"📋 {len(pending_migrations)}개의 마이그레이션을 적용합니다.")

    for version, migration_file in pending_migrations:
        apply_migration(conn, version, migration_file)

    conn.close()
    print("🎉 모든 마이그레이션 완료!")

def migration_status():
    """마이그레이션 상태 확인"""
    print("📊 마이그레이션 상태")

    conn = get_db_connection()
    create_migration_table(conn)

    applied_versions = get_applied_migrations(conn)
    pending_migrations = get_pending_migrations(applied_versions)

    print(f"\n✅ 적용된 마이그레이션: {len(applied_versions)}개")
    for version in applied_versions:
        print(f"   - {version}")

    print(f"\n⏳ 대기 중인 마이그레이션: {len(pending_migrations)}개")
    for version, migration_file in pending_migrations:
        print(f"   - {version}: {migration_file.name}")

    conn.close()

def main():
    """메인 함수"""
    if len(sys.argv) != 2:
        print("사용법: python migrate.py [up|status]")
        print("  up     - 마이그레이션 적용")
        print("  status - 마이그레이션 상태 확인")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == 'up':
        migrate_up()
    elif command == 'status':
        migration_status()
    else:
        print(f"❌ 알 수 없는 명령어: {command}")
        sys.exit(1)

if __name__ == '__main__':
    main()