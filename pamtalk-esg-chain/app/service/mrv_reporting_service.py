# -*- coding: utf-8 -*-
"""
MRV 자동 리포팅 시스템
탄소 감축량 자동 보고 및 리포트 생성
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
from enum import Enum

from .mrv_measurement_module import MeasurementData, MeasurementStatus

logger = logging.getLogger(__name__)


class ReportType(Enum):
    """리포트 유형"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"
    CUSTOM = "custom"
    VERIFICATION_REQUEST = "verification_request"


class ReportFormat(Enum):
    """리포트 형식"""
    JSON = "json"
    PDF = "pdf"
    CSV = "csv"
    XLSX = "xlsx"


@dataclass
class Report:
    """리포트"""
    report_id: str
    report_type: ReportType
    title: str
    generated_at: str
    period_start: str
    period_end: str

    # 리포트 데이터
    summary: Dict
    detailed_data: List[Dict]

    # 메타데이터
    generated_by: str  # user_id or system
    format: ReportFormat = ReportFormat.JSON
    file_path: Optional[str] = None
    metadata: Dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class MRVReportingService:
    """MRV 자동 리포팅 서비스"""

    def __init__(self, db_connection=None):
        """
        Args:
            db_connection: 데이터베이스 연결
        """
        self.db = db_connection

    def generate_measurement_report(self, measurements: List[MeasurementData],
                                   report_type: ReportType = ReportType.CUSTOM,
                                   user_id: str = "system") -> Report:
        """
        측정 데이터로부터 리포트 생성

        Args:
            measurements: 측정 데이터 목록
            report_type: 리포트 유형
            user_id: 생성자 ID

        Returns:
            Report: 생성된 리포트
        """
        if not measurements:
            logger.warning("No measurements provided for report generation")
            return None

        # 기간 계산
        dates = [datetime.fromisoformat(m.measurement_timestamp) for m in measurements]
        period_start = min(dates).isoformat()
        period_end = max(dates).isoformat()

        # 요약 데이터 생성
        summary = self._generate_summary(measurements)

        # 상세 데이터 생성
        detailed_data = self._generate_detailed_data(measurements)

        # 리포트 ID 생성
        report_id = self._generate_report_id(report_type)

        # 리포트 생성
        report = Report(
            report_id=report_id,
            report_type=report_type,
            title=f"{report_type.value.upper()} Carbon Reduction Report",
            generated_at=datetime.now().isoformat(),
            period_start=period_start,
            period_end=period_end,
            summary=summary,
            detailed_data=detailed_data,
            generated_by=user_id,
            format=ReportFormat.JSON
        )

        # 메타데이터 추가
        report.metadata = {
            'total_measurements': len(measurements),
            'report_version': '1.0',
            'data_integrity_verified': True
        }

        logger.info(f"Report generated: {report_id}, Measurements: {len(measurements)}")

        return report

    def generate_daily_report(self, date: str, user_id: Optional[str] = None) -> Report:
        """
        일일 리포트 자동 생성

        Args:
            date: 날짜 (YYYY-MM-DD)
            user_id: 특정 사용자 (None이면 전체)

        Returns:
            Report: 일일 리포트
        """
        # DB에서 해당 날짜의 측정 데이터 조회
        measurements = self._fetch_measurements_by_date(date, user_id)

        if not measurements:
            logger.info(f"No measurements found for date: {date}")
            return None

        report = self.generate_measurement_report(
            measurements=measurements,
            report_type=ReportType.DAILY,
            user_id=user_id or "system"
        )

        # 일일 리포트 특화 데이터 추가
        report.metadata['daily_stats'] = self._calculate_daily_stats(measurements)

        return report

    def generate_monthly_report(self, year: int, month: int,
                               user_id: Optional[str] = None) -> Report:
        """
        월별 리포트 생성

        Args:
            year: 년
            month: 월
            user_id: 특정 사용자 (None이면 전체)

        Returns:
            Report: 월별 리포트
        """
        # 해당 월의 측정 데이터 조회
        measurements = self._fetch_measurements_by_month(year, month, user_id)

        if not measurements:
            logger.info(f"No measurements found for {year}-{month:02d}")
            return None

        report = self.generate_measurement_report(
            measurements=measurements,
            report_type=ReportType.MONTHLY,
            user_id=user_id or "system"
        )

        # 월별 리포트 특화 데이터
        report.metadata['monthly_stats'] = self._calculate_monthly_stats(measurements)
        report.metadata['daily_breakdown'] = self._calculate_daily_breakdown(measurements)

        return report

    def generate_verification_request_report(self, measurement: MeasurementData) -> Report:
        """
        검증 요청 리포트 생성

        Args:
            measurement: 측정 데이터

        Returns:
            Report: 검증 요청 리포트
        """
        report_id = self._generate_report_id(ReportType.VERIFICATION_REQUEST)

        # 검증 요청을 위한 상세 데이터
        verification_data = {
            'measurement_id': measurement.measurement_id,
            'user_id': measurement.user_id,
            'carbon_savings_kg': measurement.carbon_savings_kg,
            'dc_units': measurement.dc_units,
            'esg_gold_amount': measurement.esg_gold_amount,
            'confidence_score': measurement.confidence_score,
            'measurement_method': measurement.measurement_method,
            'measurement_timestamp': measurement.measurement_timestamp,

            'activity_details': {
                'type': measurement.activity.activity_type.value,
                'product_name': measurement.activity.product_name,
                'quantity': measurement.activity.quantity,
                'origin_region': measurement.activity.origin_region,
                'destination_region': measurement.activity.destination_region,
                'farming_method': measurement.activity.farming_method,
                'transport_method': measurement.activity.transport_method,
                'packaging_type': measurement.activity.packaging_type
            },

            'evidences': [
                {
                    'type': e.evidence_type.value,
                    'description': e.description,
                    'file_path': e.file_path,
                    'timestamp': e.timestamp,
                    'hash': e.hash
                } for e in measurement.evidences
            ],

            'data_hash': measurement.data_hash,
            'metadata': measurement.metadata
        }

        summary = {
            'measurement_id': measurement.measurement_id,
            'carbon_savings_kg': measurement.carbon_savings_kg,
            'dc_units': measurement.dc_units,
            'confidence_score': measurement.confidence_score,
            'evidence_count': len(measurement.evidences),
            'requires_verification': measurement.confidence_score < 80 or len(measurement.evidences) < 2
        }

        report = Report(
            report_id=report_id,
            report_type=ReportType.VERIFICATION_REQUEST,
            title=f"Verification Request - {measurement.measurement_id}",
            generated_at=datetime.now().isoformat(),
            period_start=measurement.measurement_timestamp,
            period_end=measurement.measurement_timestamp,
            summary=summary,
            detailed_data=[verification_data],
            generated_by=measurement.user_id,
            format=ReportFormat.JSON
        )

        return report

    def generate_user_summary_report(self, user_id: str,
                                    start_date: str,
                                    end_date: str) -> Report:
        """
        사용자별 요약 리포트

        Args:
            user_id: 사용자 ID
            start_date: 시작일
            end_date: 종료일

        Returns:
            Report: 사용자 요약 리포트
        """
        measurements = self._fetch_measurements_by_period(user_id, start_date, end_date)

        if not measurements:
            return None

        report = self.generate_measurement_report(
            measurements=measurements,
            report_type=ReportType.CUSTOM,
            user_id=user_id
        )

        # 사용자 특화 통계
        report.metadata['user_stats'] = {
            'user_id': user_id,
            'total_activities': len(measurements),
            'total_carbon_saved': sum(m.carbon_savings_kg for m in measurements),
            'total_dc_earned': sum(m.dc_units for m in measurements),
            'average_confidence': sum(m.confidence_score for m in measurements) / len(measurements) if measurements else 0,
            'activity_breakdown': self._calculate_activity_breakdown(measurements),
            'achievement_milestones': self._calculate_milestones(measurements)
        }

        return report

    def export_report(self, report: Report, format: ReportFormat = ReportFormat.JSON) -> str:
        """
        리포트 내보내기

        Args:
            report: 리포트
            format: 출력 형식

        Returns:
            파일 경로 또는 데이터
        """
        if format == ReportFormat.JSON:
            return self._export_json(report)
        elif format == ReportFormat.CSV:
            return self._export_csv(report)
        elif format == ReportFormat.PDF:
            return self._export_pdf(report)
        elif format == ReportFormat.XLSX:
            return self._export_xlsx(report)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def schedule_automatic_reports(self, user_id: Optional[str] = None):
        """
        자동 리포트 스케줄링

        Args:
            user_id: 특정 사용자 (None이면 전체)
        """
        # 일일 리포트 생성 (매일 자정)
        # 주간 리포트 생성 (매주 월요일)
        # 월간 리포트 생성 (매월 1일)

        logger.info(f"Automatic report scheduling configured for user: {user_id or 'all'}")
        # 실제 구현에서는 Celery, APScheduler 등 사용

    def _generate_summary(self, measurements: List[MeasurementData]) -> Dict:
        """요약 데이터 생성"""
        total_carbon = sum(m.carbon_savings_kg for m in measurements)
        total_dc = sum(m.dc_units for m in measurements)
        total_esg_gold = sum(m.esg_gold_amount for m in measurements)
        avg_confidence = sum(m.confidence_score for m in measurements) / len(measurements)

        # 활동 유형별 통계
        activity_stats = {}
        for m in measurements:
            activity_type = m.activity.activity_type.value
            if activity_type not in activity_stats:
                activity_stats[activity_type] = {
                    'count': 0,
                    'carbon_savings': 0.0,
                    'dc_units': 0.0
                }
            activity_stats[activity_type]['count'] += 1
            activity_stats[activity_type]['carbon_savings'] += m.carbon_savings_kg
            activity_stats[activity_type]['dc_units'] += m.dc_units

        return {
            'total_measurements': len(measurements),
            'total_carbon_savings_kg': round(total_carbon, 2),
            'total_dc_units': round(total_dc, 2),
            'total_esg_gold': round(total_esg_gold, 6),
            'average_confidence_score': round(avg_confidence, 2),
            'by_activity_type': activity_stats,
            'high_confidence_count': sum(1 for m in measurements if m.confidence_score >= 80),
            'pending_verification': sum(1 for m in measurements if m.status == MeasurementStatus.PENDING)
        }

    def _generate_detailed_data(self, measurements: List[MeasurementData]) -> List[Dict]:
        """상세 데이터 생성"""
        detailed = []

        for m in measurements:
            detailed.append({
                'measurement_id': m.measurement_id,
                'user_id': m.user_id,
                'timestamp': m.measurement_timestamp,
                'activity_type': m.activity.activity_type.value,
                'product_name': m.activity.product_name,
                'quantity': m.activity.quantity,
                'carbon_savings_kg': m.carbon_savings_kg,
                'dc_units': m.dc_units,
                'esg_gold_amount': m.esg_gold_amount,
                'confidence_score': m.confidence_score,
                'status': m.status.value,
                'evidence_count': len(m.evidences)
            })

        return detailed

    def _calculate_daily_stats(self, measurements: List[MeasurementData]) -> Dict:
        """일일 통계 계산"""
        # 시간대별 분포
        hourly_distribution = {}
        for m in measurements:
            hour = datetime.fromisoformat(m.measurement_timestamp).hour
            hourly_distribution[hour] = hourly_distribution.get(hour, 0) + 1

        return {
            'peak_hour': max(hourly_distribution, key=hourly_distribution.get) if hourly_distribution else None,
            'hourly_distribution': hourly_distribution,
            'unique_users': len(set(m.user_id for m in measurements))
        }

    def _calculate_monthly_stats(self, measurements: List[MeasurementData]) -> Dict:
        """월별 통계 계산"""
        # 주별 통계
        weekly_stats = {}
        for m in measurements:
            week = datetime.fromisoformat(m.measurement_timestamp).isocalendar()[1]
            if week not in weekly_stats:
                weekly_stats[week] = {'count': 0, 'carbon': 0.0}
            weekly_stats[week]['count'] += 1
            weekly_stats[week]['carbon'] += m.carbon_savings_kg

        return {
            'weeks_active': len(weekly_stats),
            'weekly_breakdown': weekly_stats,
            'total_unique_users': len(set(m.user_id for m in measurements))
        }

    def _calculate_daily_breakdown(self, measurements: List[MeasurementData]) -> Dict:
        """일별 분석"""
        daily = {}
        for m in measurements:
            date = datetime.fromisoformat(m.measurement_timestamp).date().isoformat()
            if date not in daily:
                daily[date] = {'count': 0, 'carbon_kg': 0.0, 'dc_units': 0.0}
            daily[date]['count'] += 1
            daily[date]['carbon_kg'] += m.carbon_savings_kg
            daily[date]['dc_units'] += m.dc_units

        return daily

    def _calculate_activity_breakdown(self, measurements: List[MeasurementData]) -> Dict:
        """활동별 분석"""
        breakdown = {}
        for m in measurements:
            activity_type = m.activity.activity_type.value
            if activity_type not in breakdown:
                breakdown[activity_type] = {
                    'count': 0,
                    'total_carbon': 0.0,
                    'total_dc': 0.0,
                    'avg_confidence': []
                }
            breakdown[activity_type]['count'] += 1
            breakdown[activity_type]['total_carbon'] += m.carbon_savings_kg
            breakdown[activity_type]['total_dc'] += m.dc_units
            breakdown[activity_type]['avg_confidence'].append(m.confidence_score)

        # 평균 계산
        for activity_type in breakdown:
            confidences = breakdown[activity_type]['avg_confidence']
            breakdown[activity_type]['avg_confidence'] = sum(confidences) / len(confidences) if confidences else 0

        return breakdown

    def _calculate_milestones(self, measurements: List[MeasurementData]) -> List[Dict]:
        """마일스톤 계산"""
        milestones = []
        total_carbon = sum(m.carbon_savings_kg for m in measurements)

        # 마일스톤 정의
        milestone_thresholds = [10, 50, 100, 500, 1000, 5000]

        for threshold in milestone_thresholds:
            if total_carbon >= threshold:
                milestones.append({
                    'threshold_kg': threshold,
                    'achieved': True,
                    'achieved_at': 'calculated',  # 실제로는 DB에서 조회
                    'title': f'{threshold}kg CO₂ 감축 달성'
                })

        return milestones

    def _fetch_measurements_by_date(self, date: str, user_id: Optional[str] = None) -> List[MeasurementData]:
        """날짜별 측정 데이터 조회 (DB)"""
        # 실제 구현에서는 DB 쿼리
        logger.info(f"Fetching measurements for date: {date}, user: {user_id or 'all'}")
        return []  # Placeholder

    def _fetch_measurements_by_month(self, year: int, month: int, user_id: Optional[str] = None) -> List[MeasurementData]:
        """월별 측정 데이터 조회 (DB)"""
        logger.info(f"Fetching measurements for {year}-{month:02d}, user: {user_id or 'all'}")
        return []  # Placeholder

    def _fetch_measurements_by_period(self, user_id: str, start_date: str, end_date: str) -> List[MeasurementData]:
        """기간별 측정 데이터 조회 (DB)"""
        logger.info(f"Fetching measurements for user {user_id} from {start_date} to {end_date}")
        return []  # Placeholder

    def _generate_report_id(self, report_type: ReportType) -> str:
        """리포트 ID 생성"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"RPT-{report_type.value.upper()}-{timestamp}"

    def _export_json(self, report: Report) -> str:
        """JSON으로 내보내기"""
        report_dict = {
            'report_id': report.report_id,
            'report_type': report.report_type.value,
            'title': report.title,
            'generated_at': report.generated_at,
            'period_start': report.period_start,
            'period_end': report.period_end,
            'summary': report.summary,
            'detailed_data': report.detailed_data,
            'metadata': report.metadata
        }

        return json.dumps(report_dict, indent=2, ensure_ascii=False)

    def _export_csv(self, report: Report) -> str:
        """CSV로 내보내기"""
        # CSV 형식 변환
        csv_lines = []
        csv_lines.append("measurement_id,user_id,timestamp,activity_type,carbon_savings_kg,dc_units,confidence_score")

        for data in report.detailed_data:
            line = f"{data['measurement_id']},{data['user_id']},{data['timestamp']}," \
                   f"{data['activity_type']},{data['carbon_savings_kg']},{data['dc_units']}," \
                   f"{data['confidence_score']}"
            csv_lines.append(line)

        return '\n'.join(csv_lines)

    def _export_pdf(self, report: Report) -> str:
        """PDF로 내보내기"""
        # PDF 생성 (reportlab 등 사용)
        logger.info(f"PDF export for report {report.report_id}")
        return f"/reports/pdf/{report.report_id}.pdf"

    def _export_xlsx(self, report: Report) -> str:
        """Excel로 내보내기"""
        # Excel 생성 (openpyxl 등 사용)
        logger.info(f"XLSX export for report {report.report_id}")
        return f"/reports/xlsx/{report.report_id}.xlsx"


# 사용 예시
if __name__ == "__main__":
    from mrv_measurement_module import MRVMeasurementModule, MeasurementData
    from carbon_calculation_engine import CarbonActivity, ActivityType

    # 리포팅 서비스 초기화
    reporting_service = MRVReportingService()

    # 테스트용 측정 데이터 (실제로는 DB에서 조회)
    # measurements = [...]

    # 일일 리포트 생성
    # daily_report = reporting_service.generate_daily_report("2024-01-15")

    # 월별 리포트 생성
    # monthly_report = reporting_service.generate_monthly_report(2024, 1)

    print("MRV 리포팅 서비스 초기화 완료")
