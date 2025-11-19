# -*- coding: utf-8 -*-
"""
배치 작업 API 라우트
대량 토큰 발행 및 배치 전송 API 엔드포인트
"""

from flask import Blueprint, request, jsonify
import os
from dotenv import load_dotenv

from app.service.batch_service import batch_service

# 환경변수 로드
load_dotenv()
ASA_ID = int(os.getenv("ASA_ID"))
ASSET_NAME = os.getenv("ASA_NAME", "Pamtalk ESG Asset")

# Flask Blueprint 설정
batch_routes = Blueprint("batch_routes", __name__)


@batch_routes.route("/mass-mint", methods=["POST"])
def mass_mint_tokens():
    """대량 토큰 발행 API"""
    try:
        body = request.get_json()

        # 필수 파라미터 검증
        amount = int(body.get("amount", 0))
        description = body.get("description", "").strip()
        unit_name = body.get("unit_name", "").strip().upper()
        priority = int(body.get("priority", 5))

        if amount <= 0:
            return jsonify({
                "success": False,
                "message": "발행 수량은 1 이상이어야 합니다."
            }), 400

        if amount > 1000000:  # 100만개 제한
            return jsonify({
                "success": False,
                "message": "한 번에 최대 1,000,000개까지 발행 가능합니다."
            }), 400

        # 발행자 정보
        issued_by = body.get("issued_by", "admin@pamtalk.com")

        # 배치 작업 생성
        job_id = batch_service.create_mass_mint_job(
            amount=amount,
            description=description or f"{unit_name} 대량 발행",
            issued_by=issued_by,
            asset_id=ASA_ID,
            asset_name=ASSET_NAME,
            unit_name=unit_name,
            priority=priority
        )

        return jsonify({
            "success": True,
            "message": f"{amount:,}개 토큰 대량 발행 작업이 시작되었습니다.",
            "job_id": job_id,
            "amount": amount,
            "unit_name": unit_name,
            "asset_id": ASA_ID,
            "priority": priority
        }), 202  # Accepted

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"대량 발행 작업 생성 실패: {str(e)}"
        }), 500


@batch_routes.route("/batch-transfer", methods=["POST"])
def batch_transfer_tokens():
    """배치 토큰 전송 API"""
    try:
        body = request.get_json()

        transfers = body.get("transfers", [])
        priority = int(body.get("priority", 5))

        if not transfers:
            return jsonify({
                "success": False,
                "message": "전송할 대상이 없습니다."
            }), 400

        if len(transfers) > 10000:  # 1만 건 제한
            return jsonify({
                "success": False,
                "message": "한 번에 최대 10,000건까지 전송 가능합니다."
            }), 400

        # 전송 데이터 검증
        for i, transfer in enumerate(transfers):
            if not transfer.get("recipient") or not transfer.get("amount"):
                return jsonify({
                    "success": False,
                    "message": f"{i+1}번째 전송 데이터가 유효하지 않습니다."
                }), 400

        # 배치 작업 생성
        job_id = batch_service.create_batch_transfer_job(
            transfers=transfers,
            priority=priority
        )

        return jsonify({
            "success": True,
            "message": f"{len(transfers):,}건의 배치 전송 작업이 시작되었습니다.",
            "job_id": job_id,
            "transfer_count": len(transfers),
            "priority": priority
        }), 202  # Accepted

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"배치 전송 작업 생성 실패: {str(e)}"
        }), 500


@batch_routes.route("/job/<job_id>/status", methods=["GET"])
def get_job_status(job_id):
    """배치 작업 상태 조회 API"""
    try:
        status = batch_service.get_job_status(job_id)

        if not status:
            return jsonify({
                "success": False,
                "message": "존재하지 않는 작업 ID입니다."
            }), 404

        return jsonify({
            "success": True,
            "job_status": status
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"작업 상태 조회 실패: {str(e)}"
        }), 500


@batch_routes.route("/queue/info", methods=["GET"])
def get_queue_info():
    """배치 큐 정보 조회 API"""
    try:
        info = batch_service.get_queue_info()

        return jsonify({
            "success": True,
            "queue_info": info
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"큐 정보 조회 실패: {str(e)}"
        }), 500


@batch_routes.route("/jobs", methods=["GET"])
def list_recent_jobs():
    """최근 배치 작업 목록 조회"""
    try:
        # 최근 50개 작업 조회 (실제로는 DB나 Redis에서)
        jobs = []
        for job_id, job in batch_service.processor.jobs_storage.items():
            jobs.append({
                "job_id": job.job_id,
                "job_type": job.job_type,
                "status": job.status,
                "created_at": job.created_at.isoformat(),
                "priority": job.priority
            })

        # 최신순 정렬
        jobs.sort(key=lambda x: x['created_at'], reverse=True)
        jobs = jobs[:50]  # 최근 50개만

        return jsonify({
            "success": True,
            "jobs": jobs,
            "total_count": len(jobs)
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"작업 목록 조회 실패: {str(e)}"
        }), 500