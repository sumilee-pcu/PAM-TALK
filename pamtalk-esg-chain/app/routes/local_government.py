"""
Local Government API Routes
RESTful API endpoints for local government portal features
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from datetime import date

from ..service.local_government_service import LocalGovernmentService
from ..service.producer_registration_service import ProducerRegistrationService
from ..service.charging_station_service import ChargingStationService
from ..service.incentive_policy_service import IncentivePolicyService


# Initialize services
local_gov_service = LocalGovernmentService()
producer_service = ProducerRegistrationService()
charging_service = ChargingStationService()
incentive_service = IncentivePolicyService()

router = APIRouter(prefix="/api/local-government", tags=["Local Government"])


# ============================================================================
# Request/Response Models
# ============================================================================

class GovernmentDashboardResponse(BaseModel):
    government_id: str
    government_name: str
    total_carbon_reduction: float
    active_residents: int
    active_programs: int
    total_producers: int
    operational_stations: int


class ProducerRegistrationRequest(BaseModel):
    government_id: str
    producer_name: str
    producer_type: str
    contact_person: str
    contact_phone: str
    contact_email: Optional[str] = None
    farm_address: str
    farm_latitude: Optional[float] = None
    farm_longitude: Optional[float] = None
    farm_area_sqm: Optional[float] = None
    organic_certified: bool = False
    gap_certified: bool = False
    haccp_certified: bool = False
    algorand_address: Optional[str] = None


class ProductRegistrationRequest(BaseModel):
    producer_id: str
    product_name: str
    product_category: str
    product_type: Optional[str] = None
    description: Optional[str] = None
    unit_type: str
    unit_price: Optional[float] = None
    production_method: Optional[str] = None


class ChargingStationRequest(BaseModel):
    government_id: str
    station_name: str
    station_type: str
    operator_name: str
    address: str
    latitude: float
    longitude: float
    total_chargers: int
    max_power_kw: float
    price_per_kwh: Optional[float] = None
    accepts_esg_gold: bool = False
    esg_gold_discount_percentage: float = 0


class IncentivePolicyRequest(BaseModel):
    government_id: str
    policy_name: str
    policy_type: str
    description: str
    target_group: str
    eligibility_criteria: str
    benefit_amount: Optional[float] = None
    total_budget: Optional[float] = None
    application_start_date: str
    effective_date: str


class IncentiveApplicationRequest(BaseModel):
    policy_id: str
    government_id: str
    applicant_type: str
    applicant_id: str
    applicant_name: str
    applicant_email: str
    applicant_phone: str
    requested_amount: Optional[float] = None
    carbon_reduction_achieved: Optional[float] = None
    activities_completed: Optional[str] = None
    recipient_algorand_address: Optional[str] = None


# ============================================================================
# Local Government Endpoints
# ============================================================================

@router.get("/governments")
async def get_all_governments(
    government_type: Optional[str] = Query(None, description="Filter by government type")
):
    """Get all local governments"""
    try:
        governments = local_gov_service.get_all_governments(government_type)
        return {"success": True, "data": governments}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/{government_id}")
async def get_government_dashboard(government_id: str):
    """Get comprehensive dashboard data for a local government"""
    try:
        dashboard = local_gov_service.get_government_dashboard(government_id)
        if not dashboard:
            raise HTTPException(status_code=404, detail="Government not found")
        return {"success": True, "data": dashboard}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/carbon-stats/{government_id}")
async def get_carbon_stats(
    government_id: str,
    period: str = Query("monthly", description="daily, weekly, monthly, quarterly, yearly"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Get carbon reduction statistics"""
    try:
        stats = local_gov_service.get_carbon_stats(government_id, period, start_date, end_date)
        return {"success": True, "data": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/carbon-stats/{government_id}/update")
async def update_carbon_stats(government_id: str):
    """Update daily carbon statistics"""
    try:
        result = local_gov_service.update_daily_carbon_stats(government_id)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rankings")
async def get_regional_rankings(
    region_type: str = Query("all", description="all, city, county, district, province")
):
    """Get carbon reduction rankings of local governments"""
    try:
        rankings = local_gov_service.get_regional_rankings(region_type)
        return {"success": True, "data": rankings}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ESG Program Endpoints
# ============================================================================

@router.get("/programs")
async def get_esg_programs(
    government_id: Optional[str] = None,
    program_type: Optional[str] = None,
    status: Optional[str] = None
):
    """Get ESG programs with filters"""
    try:
        programs = local_gov_service.get_esg_programs(government_id, program_type, status)
        return {"success": True, "data": programs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/programs")
async def create_esg_program(program_data: dict):
    """Create a new ESG program"""
    try:
        program_id = local_gov_service.create_esg_program(program_data)
        return {"success": True, "program_id": program_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/programs/{program_id}")
async def update_esg_program(program_id: str, update_data: dict):
    """Update an ESG program"""
    try:
        success = local_gov_service.update_esg_program(program_id, update_data)
        if not success:
            raise HTTPException(status_code=404, detail="Program not found")
        return {"success": True, "message": "Program updated"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Producer Registration Endpoints
# ============================================================================

@router.post("/producers/register")
async def register_producer(producer_data: ProducerRegistrationRequest):
    """Register a new producer"""
    try:
        producer_id = producer_service.register_producer(producer_data.dict())
        return {"success": True, "producer_id": producer_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/producers")
async def get_producers(
    government_id: Optional[str] = None,
    producer_type: Optional[str] = None,
    verification_status: Optional[str] = None,
    organic_only: bool = False
):
    """Get producers with filters"""
    try:
        producers = producer_service.get_producers(
            government_id, producer_type, verification_status, organic_only
        )
        return {"success": True, "data": producers}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/producers/{producer_id}")
async def get_producer_detail(producer_id: str):
    """Get detailed producer information"""
    try:
        producer = producer_service.get_producer_detail(producer_id)
        if not producer:
            raise HTTPException(status_code=404, detail="Producer not found")
        return {"success": True, "data": producer}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/producers/{producer_id}/verify")
async def verify_producer(
    producer_id: str,
    verifier_id: str,
    status: str,
    notes: Optional[str] = None
):
    """Verify or reject a producer registration"""
    try:
        success = producer_service.verify_producer(producer_id, verifier_id, status, notes)
        if not success:
            raise HTTPException(status_code=404, detail="Producer not found")
        return {"success": True, "message": "Producer verification updated"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/producers/products")
async def add_product(product_data: ProductRegistrationRequest):
    """Add a product for a producer"""
    try:
        product_id = producer_service.add_product(product_data.dict())
        return {"success": True, "product_id": product_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/products/search")
async def search_products(
    government_id: Optional[str] = None,
    product_category: Optional[str] = None,
    product_type: Optional[str] = None,
    organic_only: bool = False
):
    """Search for products"""
    try:
        products = producer_service.search_products(
            government_id, product_category, product_type, organic_only
        )
        return {"success": True, "data": products}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/producers/stats/{government_id}")
async def get_producer_statistics(government_id: str):
    """Get producer statistics for a government"""
    try:
        stats = producer_service.get_producer_statistics(government_id)
        return {"success": True, "data": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Charging Station Endpoints
# ============================================================================

@router.get("/charging-stations")
async def get_all_charging_stations(
    government_id: Optional[str] = None,
    station_type: Optional[str] = None,
    accepts_esg_gold: Optional[bool] = None
):
    """Get all charging stations with filters"""
    try:
        stations = charging_service.get_all_stations(government_id, station_type, accepts_esg_gold)
        return {"success": True, "data": stations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/charging-stations/nearby")
async def get_nearby_stations(
    latitude: float = Query(..., description="Latitude"),
    longitude: float = Query(..., description="Longitude"),
    radius_km: float = Query(10.0, description="Search radius in kilometers"),
    limit: int = Query(20, description="Maximum number of results")
):
    """Find charging stations near a location"""
    try:
        stations = charging_service.get_nearby_stations(latitude, longitude, radius_km, limit)
        return {"success": True, "data": stations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/charging-stations/{station_id}")
async def get_station_detail(station_id: str):
    """Get detailed information about a charging station"""
    try:
        station = charging_service.get_station_detail(station_id)
        if not station:
            raise HTTPException(status_code=404, detail="Station not found")
        return {"success": True, "data": station}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/charging-stations")
async def create_charging_station(station_data: ChargingStationRequest):
    """Create a new charging station"""
    try:
        station_id = charging_service.create_station(station_data.dict())
        return {"success": True, "station_id": station_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/charging-stations/{station_id}/start-session")
async def start_charging_session(station_id: str, session_data: dict):
    """Start a new charging session"""
    try:
        session_data['station_id'] = station_id
        usage_id = charging_service.start_charging_session(session_data)
        return {"success": True, "usage_id": usage_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/charging-stations/sessions/{usage_id}/complete")
async def complete_charging_session(
    usage_id: str,
    energy_delivered_kwh: float,
    payment_details: Optional[dict] = None
):
    """Complete a charging session"""
    try:
        result = charging_service.complete_charging_session(usage_id, energy_delivered_kwh, payment_details)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/charging-stations/user-history/{user_address}")
async def get_user_charging_history(user_address: str, limit: int = 50):
    """Get charging history for a user"""
    try:
        history = charging_service.get_user_charging_history(user_address, limit)
        return {"success": True, "data": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/charging-stations/{station_id}/reviews")
async def add_station_review(station_id: str, review_data: dict):
    """Add a review for a charging station"""
    try:
        review_data['station_id'] = station_id
        review_id = charging_service.add_review(review_data)
        return {"success": True, "review_id": review_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/charging-stations/stats/{government_id}")
async def get_station_statistics(government_id: str):
    """Get charging station statistics"""
    try:
        stats = charging_service.get_station_statistics(government_id)
        return {"success": True, "data": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/charging-stations/popular/{government_id}")
async def get_popular_stations(government_id: str, limit: int = 10):
    """Get most popular charging stations"""
    try:
        stations = charging_service.get_popular_stations(government_id, limit)
        return {"success": True, "data": stations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Incentive Policy Endpoints
# ============================================================================

@router.get("/policies")
async def get_incentive_policies(
    government_id: Optional[str] = None,
    policy_type: Optional[str] = None,
    status: str = "active",
    target_group: Optional[str] = None
):
    """Get incentive policies with filters"""
    try:
        policies = incentive_service.get_policies(government_id, policy_type, status, target_group)
        return {"success": True, "data": policies}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/policies/{policy_id}")
async def get_policy_detail(policy_id: str):
    """Get detailed policy information"""
    try:
        policy = incentive_service.get_policy_detail(policy_id)
        if not policy:
            raise HTTPException(status_code=404, detail="Policy not found")
        return {"success": True, "data": policy}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/policies")
async def create_incentive_policy(policy_data: IncentivePolicyRequest):
    """Create a new incentive policy"""
    try:
        policy_id = incentive_service.create_policy(policy_data.dict())
        return {"success": True, "policy_id": policy_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/policies/{policy_id}")
async def update_incentive_policy(policy_id: str, update_data: dict):
    """Update policy information"""
    try:
        success = incentive_service.update_policy(policy_id, update_data)
        if not success:
            raise HTTPException(status_code=404, detail="Policy not found")
        return {"success": True, "message": "Policy updated"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/policies/applications")
async def submit_incentive_application(application_data: IncentiveApplicationRequest):
    """Submit a new incentive application"""
    try:
        application_id = incentive_service.submit_application(application_data.dict())
        return {"success": True, "application_id": application_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/policies/applications")
async def get_incentive_applications(
    government_id: Optional[str] = None,
    policy_id: Optional[str] = None,
    applicant_id: Optional[str] = None,
    status: Optional[str] = None
):
    """Get applications with filters"""
    try:
        applications = incentive_service.get_applications(government_id, policy_id, applicant_id, status)
        return {"success": True, "data": applications}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/policies/applications/{application_id}")
async def get_application_detail(application_id: str):
    """Get detailed application information"""
    try:
        application = incentive_service.get_application_detail(application_id)
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        return {"success": True, "data": application}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/policies/applications/{application_id}/review")
async def review_application(
    application_id: str,
    reviewer_id: str,
    decision: str,
    approved_amount: Optional[float] = None,
    review_notes: Optional[str] = None
):
    """Review and approve/reject an application"""
    try:
        success = incentive_service.review_application(
            application_id, reviewer_id, decision, approved_amount, review_notes
        )
        if not success:
            raise HTTPException(status_code=404, detail="Application not found")
        return {"success": True, "message": "Application reviewed"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/policies/applications/{application_id}/mark-paid")
async def mark_application_paid(
    application_id: str,
    payment_reference: str,
    blockchain_tx_id: Optional[str] = None
):
    """Mark an application as paid"""
    try:
        success = incentive_service.mark_application_paid(application_id, payment_reference, blockchain_tx_id)
        if not success:
            raise HTTPException(status_code=404, detail="Application not found or not approved")
        return {"success": True, "message": "Application marked as paid"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/policies/stats/{government_id}")
async def get_policy_statistics(government_id: str):
    """Get policy statistics for a government"""
    try:
        stats = incentive_service.get_policy_statistics(government_id)
        return {"success": True, "data": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/policies/applicant-history/{applicant_id}")
async def get_applicant_history(applicant_id: str):
    """Get application history for an applicant"""
    try:
        history = incentive_service.get_applicant_history(applicant_id)
        return {"success": True, "data": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
