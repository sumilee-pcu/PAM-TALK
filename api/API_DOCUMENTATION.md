# PAM-TALK REST API Documentation

## Overview

The PAM-TALK REST API provides comprehensive endpoints for managing agricultural farms, transactions, AI predictions, and analytics. The API is built with Flask and includes CORS support, comprehensive error handling, and JSON responses.

**Base URL**: `http://localhost:5000`

## Authentication

Currently, the API does not require authentication. In production, implement proper authentication mechanisms.

## Response Format

All API responses follow a consistent format:

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "message": "Optional success message",
  "timestamp": "2025-09-25T12:34:56.789Z"
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "message": "Error description",
    "status_code": 400,
    "timestamp": "2025-09-25T12:34:56.789Z",
    "details": { ... }
  }
}
```

## Endpoints

### Health Check

#### GET `/`
Returns basic API information.

**Response**:
```json
{
  "name": "PAM-TALK API Server",
  "version": "1.0.0",
  "status": "running",
  "timestamp": "2025-09-25T12:34:56.789Z",
  "endpoints": ["..."]
}
```

**cURL Example**:
```bash
curl -X GET http://localhost:5000/
```

#### GET `/api/health`
Returns detailed health status of all system components.

**Response**:
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "components": {
      "data_processor": "ok",
      "ai_models": "ok",
      "blockchain": "ok"
    },
    "blockchain_stats": { ... }
  }
}
```

**cURL Example**:
```bash
curl -X GET http://localhost:5000/api/health
```

---

### Farm Management

#### POST `/api/farms`
Register a new farm.

**Request Body**:
```json
{
  "farm_id": "FARM_001",
  "farm_name": "Green Valley Farm",
  "owner_name": "John Doe",
  "location": "Seoul, South Korea",
  "size_hectares": 25.5,
  "established_date": "2020-01-15",
  "contact_info": {
    "phone": "+82-10-1234-5678",
    "email": "contact@greenvalley.kr"
  },
  "certifications": ["organic", "fair_trade"],
  "products": ["tomatoes", "lettuce", "carrots"],
  "esg_data": {
    "organic_certified": true,
    "water_usage_per_hectare": 5000,
    "carbon_emissions": 2.5,
    "renewable_energy_percentage": 60.0
  },
  "status": "active"
}
```

**cURL Example**:
```bash
curl -X POST http://localhost:5000/api/farms \
  -H "Content-Type: application/json" \
  -d '{
    "farm_id": "FARM_001",
    "farm_name": "Green Valley Farm",
    "owner_name": "John Doe",
    "location": "Seoul, South Korea",
    "size_hectares": 25.5,
    "products": ["tomatoes", "lettuce"],
    "status": "active"
  }'
```

#### GET `/api/farms/{id}`
Get detailed information about a specific farm.

**Path Parameters**:
- `id` (string): Farm ID

**cURL Example**:
```bash
curl -X GET http://localhost:5000/api/farms/FARM_001
```

#### GET `/api/farms`
List all farms with optional filtering.

**Query Parameters**:
- `status` (string, optional): Filter by farm status
- `product` (string, optional): Filter by product type

**cURL Examples**:
```bash
# List all farms
curl -X GET http://localhost:5000/api/farms

# Filter by status
curl -X GET "http://localhost:5000/api/farms?status=active"

# Filter by product
curl -X GET "http://localhost:5000/api/farms?product=tomatoes"
```

#### GET `/api/farms/{id}/predict`
Get demand predictions for farm products.

**Path Parameters**:
- `id` (string): Farm ID

**Query Parameters**:
- `days` (integer, optional): Prediction period in days (default: 7)

**cURL Example**:
```bash
curl -X GET "http://localhost:5000/api/farms/FARM_001/predict?days=7"
```

---

### Transaction Management

#### POST `/api/transactions`
Create a new agricultural transaction.

**Request Body**:
```json
{
  "producer_id": "FARM_001",
  "consumer_id": "CONSUMER_001",
  "product_type": "tomatoes",
  "quantity": 500,
  "price_per_unit": 5000,
  "quality_score": 85,
  "esg_score": 80,
  "location": "Seoul",
  "payment_method": "PAMT_TRANSFER",
  "delivery_time_hours": 24,
  "metadata": {
    "note": "Organic produce delivery"
  }
}
```

**cURL Example**:
```bash
curl -X POST http://localhost:5000/api/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "producer_id": "FARM_001",
    "consumer_id": "CONSUMER_001",
    "product_type": "tomatoes",
    "quantity": 500,
    "price_per_unit": 5000,
    "quality_score": 85,
    "esg_score": 80
  }'
```

#### GET `/api/transactions`
List transactions with optional filtering.

**Query Parameters**:
- `limit` (integer, optional): Maximum number of results (default: 50)
- `farm_id` (string, optional): Filter by farm ID
- `product_type` (string, optional): Filter by product type
- `start_date` (string, optional): Filter by start date (ISO format)
- `end_date` (string, optional): Filter by end date (ISO format)

**cURL Examples**:
```bash
# List recent transactions
curl -X GET "http://localhost:5000/api/transactions?limit=10"

# Filter by farm
curl -X GET "http://localhost:5000/api/transactions?farm_id=FARM_001"

# Filter by date range
curl -X GET "http://localhost:5000/api/transactions?start_date=2025-09-01&end_date=2025-09-25"
```

#### GET `/api/transactions/{id}/esg`
Get ESG score for a transaction participant.

**Path Parameters**:
- `id` (string): Transaction ID

**Query Parameters**:
- `participant` (string): Either "producer" or "consumer" (default: "producer")

**cURL Example**:
```bash
curl -X GET "http://localhost:5000/api/transactions/TXN_123456/esg?participant=producer"
```

#### POST `/api/transactions/check`
Check a transaction for anomalies.

**Request Body**:
```json
{
  "producer_id": "FARM_001",
  "consumer_id": "CONSUMER_001",
  "product_type": "tomatoes",
  "quantity": 500,
  "price_per_unit": 5000,
  "quality_score": 85,
  "esg_score": 80,
  "location": "Seoul",
  "payment_method": "PAMT_TRANSFER",
  "delivery_time_hours": 24
}
```

**Response Example**:
```json
{
  "success": true,
  "data": {
    "transaction_id": "CHECK_1234567890",
    "is_anomaly": false,
    "anomaly_score": 0.234,
    "confidence": 0.876,
    "risk_level": "LOW",
    "anomaly_types": [],
    "recommendations": [],
    "detection_methods": {
      "z_score_analysis": 0.123,
      "isolation_forest": 0.234,
      "pattern_analysis": 0.100
    }
  }
}
```

**cURL Example**:
```bash
curl -X POST http://localhost:5000/api/transactions/check \
  -H "Content-Type: application/json" \
  -d '{
    "producer_id": "FARM_001",
    "consumer_id": "CONSUMER_001",
    "product_type": "tomatoes",
    "quantity": 100,
    "price_per_unit": 25000
  }'
```

---

### Dashboard and Analytics

#### GET `/api/dashboard`
Get comprehensive dashboard data including statistics, metrics, and AI insights.

**Response Structure**:
```json
{
  "success": true,
  "data": {
    "overview": {
      "total_farms": 10,
      "total_transactions": 150,
      "recent_transactions": 25,
      "active_farms": 8
    },
    "farms": {
      "by_status": {"active": 8, "inactive": 2},
      "by_size": {"small": 3, "medium": 5, "large": 2},
      "by_products": {"tomatoes": 6, "rice": 4, "lettuce": 3},
      "total_area": 456.7
    },
    "transactions": {
      "total_value": 45000000,
      "by_product": {"tomatoes": 20000000, "rice": 15000000},
      "recent_activity": [...]
    },
    "ai_insights": {
      "predictions": {"tomatoes": {"total_demand": 15000, "confidence": 0.85}},
      "anomalies_detected": 2,
      "esg_average": 76.5
    },
    "processing_stats": {
      "success_rate": 0.95,
      "total_predictions": 25,
      "total_anomalies": 3
    }
  }
}
```

**cURL Example**:
```bash
curl -X GET http://localhost:5000/api/dashboard
```

---

## Error Codes

- **200** - OK: Request successful
- **201** - Created: Resource created successfully
- **400** - Bad Request: Invalid request data
- **404** - Not Found: Resource not found
- **500** - Internal Server Error: Server error
- **503** - Service Unavailable: Service temporarily unavailable

## Rate Limiting

Currently, no rate limiting is implemented. In production, implement appropriate rate limiting based on your requirements.

## CORS

The API supports Cross-Origin Resource Sharing (CORS) and accepts requests from any origin. Configure this appropriately for production use.

## Testing

### Automated Testing
Run the comprehensive test suite:
```bash
python api/test_api.py
```

### Manual Testing Examples

1. **Health Check**:
```bash
curl -X GET http://localhost:5000/api/health
```

2. **Register a Farm**:
```bash
curl -X POST http://localhost:5000/api/farms \
  -H "Content-Type: application/json" \
  -d '{"farm_id":"TEST_001","farm_name":"Test Farm","owner_name":"Test Owner","location":"Seoul","size_hectares":10.0}'
```

3. **Create a Transaction**:
```bash
curl -X POST http://localhost:5000/api/transactions \
  -H "Content-Type: application/json" \
  -d '{"producer_id":"TEST_001","consumer_id":"CONSUMER_001","product_type":"tomatoes","quantity":100,"price_per_unit":3000}'
```

4. **Check for Anomalies**:
```bash
curl -X POST http://localhost:5000/api/transactions/check \
  -H "Content-Type: application/json" \
  -d '{"producer_id":"TEST_001","consumer_id":"CONSUMER_001","product_type":"tomatoes","quantity":10,"price_per_unit":50000}'
```

5. **Get Dashboard Data**:
```bash
curl -X GET http://localhost:5000/api/dashboard
```

## Deployment

### Development
```bash
python api/app.py
```

### Production
For production deployment, consider using:
- **Gunicorn**: `gunicorn -w 4 -b 0.0.0.0:5000 api.app:app`
- **uWSGI**: Configure with appropriate settings
- **Docker**: Create a Dockerfile for containerized deployment

### Environment Variables
Set these environment variables for production:
- `FLASK_ENV=production`
- `FLASK_DEBUG=False`
- Configure database connections
- Set API keys and secrets

## Security Considerations

1. **Authentication**: Implement proper authentication (JWT, OAuth2, etc.)
2. **Input Validation**: All inputs are validated, but add additional layers
3. **Rate Limiting**: Implement rate limiting for production
4. **HTTPS**: Always use HTTPS in production
5. **CORS**: Configure CORS properly for your domain
6. **Logging**: Monitor and log all API requests
7. **Error Handling**: Never expose sensitive information in error messages

## Support

For issues or questions about the API, check:
1. Server logs for detailed error information
2. Health check endpoint for system status
3. Test suite for examples of proper usage

## Changelog

### Version 1.0.0 (2025-09-25)
- Initial release
- Farm management endpoints
- Transaction processing
- AI integration (demand prediction, ESG scoring, anomaly detection)
- Dashboard analytics
- Comprehensive error handling and CORS support