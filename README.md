# SEC Income Statement API

A FastAPI-based REST API for retrieving and analyzing income statement data from SEC EDGAR filings using XBRL data.

## 🚀 Features

- **Comprehensive Financial Data**: Access 23+ income statement line items including revenue, expenses, profits, EPS, and more
- **Flexible Date Filtering**: Query data by date range or get all available periods
- **Multiple Output Formats**: Get quarterly or trailing-twelve-month (TTM) data
- **Smart Data Derivation**: Automatically calculates missing fields when possible (e.g., Cost of Revenue = Revenue - Gross Profit)
- **Formatted Output**: Returns both raw numbers and human-readable formatted values ($1.5B, $234.5M)
- **SEC Compliant**: Includes proper User-Agent headers and rate limiting
- **Docker Ready**: Full containerization with Docker and Docker Compose
- **Production Ready**: Includes Nginx reverse proxy and Redis caching options

## 📋 Requirements

### Option 1: Docker (Recommended)
- Docker 20.10+
- Docker Compose 2.0+

### Option 2: Local Development
```bash
fastapi>=0.104.0
uvicorn>=0.24.0
pydantic>=2.0.0
requests>=2.31.0
pandas>=2.0.0
numpy>=1.24.0
```

## 🔧 Installation

### Quick Start with Docker

1. Clone the repository:
```bash
git clone <repository-url>
cd secinsight-api
```

2. Build and run with Docker Compose:
```bash
# Basic setup (API only)
make build
make up

# Or manually
docker-compose up -d
```

3. Access the API:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Advanced Docker Setup

#### With Nginx Reverse Proxy
```bash
make up-with-nginx
# API available at http://localhost (port 80)
```

#### With Redis Cache
```bash
make up-with-cache
```

#### Full Stack (API + Nginx + Redis)
```bash
make up-full
```

### Local Development Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
# Option 1: Direct Python
python app.py

# Option 2: Using Uvicorn
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

## 🐳 Docker Commands

The project includes a Makefile for easy container management:

```bash
make help           # Show all available commands
make build          # Build Docker images
make up             # Start services
make down           # Stop services
make restart        # Restart services
make logs           # View logs (follow mode)
make logs-api       # View API logs only
make shell          # Open shell in API container
make ps             # Show running containers
make health         # Check API health status
make clean          # Remove stopped containers
make rebuild        # Rebuild from scratch
```

## 📁 Project Structure

```
secinsight-api/
├── app.py                  # Main FastAPI application
├── Dockerfile              # Docker image configuration
├── docker-compose.yml      # Docker Compose services
├── requirements.txt        # Python dependencies
├── .dockerignore          # Docker build exclusions
├── Makefile               # Helper commands
├── README.md              # This file
├── nginx/
│   └── nginx.conf         # Nginx configuration
└── logs/                  # Application logs (created on run)
```

## 📖 API Documentation

### Endpoints

#### `GET /`
Root endpoint with API information.

#### `GET /health`
Health check endpoint.

#### `POST /income-statement`
Retrieve income statement data from SEC filings.

**Request Body:**
```json
{
  "cik": "320193",
  "user_agent": "yourname@domain.com MyApp/1.0",
  "start_date": "2022-01-01",
  "end_date": "2024-12-31",
  "required_fields": [
    "Total Revenues",
    "Cost Of Revenues",
    "Gross Profit",
    "Operating Income",
    "Net Income"
  ],
  "output_type": "quarterly"
}
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `cik` | string | ✅ Yes | Company CIK number (e.g., "320193" for Apple) |
| `user_agent` | string | ✅ Yes | Your email for SEC compliance (e.g., "yourname@domain.com MyApp/1.0") |
| `start_date` | string | ❌ No | Start date in YYYY-MM-DD format |
| `end_date` | string | ❌ No | End date in YYYY-MM-DD format |
| `required_fields` | array | ❌ No | List of income statement line items (defaults to 23 fields) |
| `output_type` | string | ❌ No | "quarterly" or "ttm" (default: "quarterly") |

**Response:**
```json
{
  "cik": "320193",
  "company_name": "Apple Inc.",
  "output_type": "quarterly",
  "data": {
    "Total Revenues": {
      "2023Q1": {
        "raw": 94836000000,
        "formatted": "$94.84B"
      },
      "2023Q2": {
        "raw": 81797000000,
        "formatted": "$81.80B"
      }
    },
    "Net Income": {
      "2023Q1": {
        "raw": 23615000000,
        "formatted": "$23.62B"
      }
    }
  },
  "periods": ["2023Q1", "2023Q2", "2023Q3", "2023Q4"],
  "message": "Success"
}
```

## 📊 Available Fields

### Revenue & Costs
- Total Revenues
- Cost Of Revenues
- Gross Profit

### Operating Expenses
- R&D Expenses
- Selling General & Admin Expenses
- Other Operating Expenses, Total
- Operating Expenses

### Income Metrics
- Operating Income
- EBIT
- EBITDA

### Interest & Non-Operating
- Interest Expense, Total
- Interest And Investment Income
- Net Interest Expenses
- Other Non Operating Expenses, Total

### Pre-Tax & Unusual Items
- EBT, Excl. Unusual Items
- EBT, Incl. Unusual Items
- Gain (Loss) On Sale Of Assets
- Other Unusual Items, Total

### Tax & Net Income
- Income Tax Expense
- Net Income
- Net Income to Company
- Minority Interest
- Net Income to Common Excl. Extra Items
- Preferred Dividend and Other Adjustments

### Per Share Metrics
- Basic EPS - Continuing Operations
- Diluted EPS - Continuing Operations
- Basic Weighted Average Shares Outstanding
- Diluted Weighted Average Shares Outstanding
- Dividend Per Share

## 💡 Usage Examples

### Example 1: Get All Available Data (Default)
```bash
curl -X POST "http://localhost:8000/income-statement" \
  -H "Content-Type: application/json" \
  -d '{
    "cik": "320193",
    "user_agent": "yourname@domain.com MyApp/1.0",
    "output_type": "quarterly"
  }'
```

### Example 2: Get Specific Fields for Date Range
```bash
curl -X POST "http://localhost:8000/income-statement" \
  -H "Content-Type: application/json" \
  -d '{
    "cik": "1318605",
    "user_agent": "yourname@domain.com MyApp/1.0",
    "start_date": "2023-01-01",
    "end_date": "2023-12-31",
    "required_fields": [
      "Total Revenues",
      "Gross Profit",
      "Operating Income",
      "Net Income",
      "Basic EPS - Continuing Operations"
    ],
    "output_type": "quarterly"
  }'
```

### Example 3: Get TTM (Trailing Twelve Months) Data
```bash
curl -X POST "http://localhost:8000/income-statement" \
  -H "Content-Type: application/json" \
  -d '{
    "cik": "789019",
    "user_agent": "yourname@domain.com MyApp/1.0",
    "required_fields": ["Total Revenues", "Net Income", "EBIT"],
    "output_type": "ttm"
  }'
```

### Example 4: Python Requests
```python
import requests

url = "http://localhost:8000/income-statement"
payload = {
    "cik": "320193",
    "user_agent": "yourname@domain.com MyApp/1.0",
    "start_date": "2022-01-01",
    "end_date": "2024-12-31",
    "required_fields": [
        "Total Revenues",
        "Cost Of Revenues",
        "Gross Profit",
        "Net Income"
    ],
    "output_type": "quarterly"
}

response = requests.post(url, json=payload)
data = response.json()

print(f"Company: {data['company_name']}")
print(f"Periods: {data['periods']}")
print(f"Revenue Q1 2023: {data['data']['Total Revenues']['2023Q1']['formatted']}")
```

### Example 5: JavaScript/Node.js Fetch
```javascript
const response = await fetch('http://localhost:8000/income-statement', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    cik: '320193',
    user_agent: 'yourname@domain.com MyApp/1.0',
    output_type: 'ttm',
    required_fields: ['Total Revenues', 'Net Income', 'Basic EPS - Continuing Operations']
  })
});

const data = await response.json();
console.log(data);
```

## 🔍 Finding Company CIK Numbers

You can find company CIK numbers on the SEC website:
1. Visit https://www.sec.gov/edgar/searchedgar/companysearch.html
2. Search for the company name
3. The CIK is displayed in the search results

**Common CIK Numbers:**
- Apple Inc.: `320193`
- Microsoft Corp: `789019`
- Tesla Inc.: `1318605`
- Amazon.com Inc.: `1018724`
- Alphabet Inc. (Google): `1652044`

## ⚙️ Configuration

### User Agent Requirement
The SEC requires a User-Agent header with your contact information. Format:
```
yourname@domain.com MyAppName/Version
```

**Important:** Replace with your actual email address to comply with SEC regulations.

### Rate Limiting
The API includes built-in retry logic for SEC requests with exponential backoff. However, be mindful of SEC rate limits:
- Maximum 10 requests per second
- Requests should include proper User-Agent

## 🔒 Data Derivation Logic

The API automatically derives missing fields when possible:

1. **Cost of Revenue** = Revenue - Gross Profit (if missing)
2. **Gross Profit** = Revenue - Cost of Revenue (if missing)
3. **Operating Expenses** = R&D + SG&A (if missing)
4. **Operating Income** = Gross Profit - Operating Expenses (if missing)

## 📝 Output Format

Each field returns both:
- **`raw`**: Numerical value in USD
- **`formatted`**: Human-readable string with units:
  - Billions: `$1.5B`
  - Millions: `$234.5M`
  - Thousands: `$5.2K`

## ⚠️ Error Handling

Common errors and solutions:

| Error | Cause | Solution |
|-------|-------|----------|
| `404` | Invalid CIK | Verify the CIK number is correct |
| `500` | SEC API timeout | Retry after a few seconds |
| `422` | Invalid request format | Check date format (YYYY-MM-DD) and output_type |
| `Rate limit` | Too many requests | Wait and retry with backoff |

## 🧪 Testing

### Test the Health Endpoint
```bash
curl http://localhost:8000/health
```

### Test with Interactive Docs
1. Open `http://localhost:8000/docs`
2. Click on `/income-statement` endpoint
3. Click "Try it out"
4. Fill in the parameters
5. Click "Execute"

## 📄 License

This project is provided as-is for educational and research purposes. Please comply with SEC usage policies when accessing their data.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 📧 Support

For questions or issues, please create an issue in the repository or contact the maintainer.

## ⚡ Performance Tips

1. **Cache responses**: Store frequently accessed data to reduce SEC API calls
2. **Batch requests**: Request multiple fields at once instead of separate calls
3. **Use date ranges**: Limit data to needed periods to improve response time
4. **TTM calculation**: Pre-calculate TTM data if accessing frequently

## 🔮 Future Enhancements

- [ ] Balance sheet data support
- [ ] Cash flow statement support
- [ ] Multiple company comparison
- [ ] Growth rate calculations
- [ ] Margin trend analysis
- [ ] Export to CSV/Excel
- [ ] Caching layer with Redis
- [ ] Authentication & API keys
- [ ] Rate limiting per user
- [ ] Webhook notifications

## 🐳 Docker Configuration Details

### Environment Variables

You can customize the API behavior using environment variables in `docker-compose.yml`:

```yaml
environment:
  - ENVIRONMENT=production
  - LOG_LEVEL=info
  - API_RATE_LIMIT=10  # requests per second
```

### Docker Profiles

The project uses Docker Compose profiles for optional services:

- **Default**: API only
- **`with-nginx`**: Adds Nginx reverse proxy with rate limiting
- **`with-cache`**: Adds Redis for caching (ready for future implementation)

### Volumes

- `./logs:/app/logs` - Application logs
- `redis-data` - Redis persistence (if using cache profile)

### Networks

All services run on the `secinsight-network` bridge network for internal communication.

### Health Checks

Both API and Redis containers include health checks:
- **API**: Checks `/health` endpoint every 30s
- **Redis**: Pings Redis server every 10s

## 🔒 Security Best Practices

1. **Non-root User**: API runs as `appuser` (UID 1000) inside container
2. **Security Headers**: Nginx adds security headers (X-Frame-Options, etc.)
3. **Rate Limiting**: Nginx limits requests to 10/second (burst 20)
4. **SSL Ready**: Nginx config includes commented SSL configuration
5. **No Secrets in Code**: Use environment variables for sensitive data

## 📊 Monitoring & Logs

### View Logs
```bash
# All services
make logs

# API only
make logs-api

# Specific number of lines
docker-compose logs --tail=100 api
```

### Health Check
```bash
# Using make command
make health

# Or manually
curl http://localhost:8000/health
```

### Container Stats
```bash
# Resource usage
docker stats secinsight-api

# Running containers
make ps
```

## 🧪 Testing

### Test API Endpoint
```bash
# Health check
curl http://localhost:8000/health

# Get income statement
curl -X POST "http://localhost:8000/income-statement" \
  -H "Content-Type: application/json" \
  -d '{
    "cik": "320193",
    "user_agent": "test@example.com TestApp/1.0",
    "output_type": "quarterly",
    "required_fields": ["Total Revenues", "Net Income"]
  }'
```

### Interactive API Testing
1. Open http://localhost:8000/docs
2. Click "Try it out" on any endpoint
3. Fill in parameters and execute

## 🚀 Deployment

### Production Deployment Checklist

- [ ] Update `user_agent` requirement validation
- [ ] Enable SSL/TLS in Nginx
- [ ] Set up proper logging
- [ ] Configure firewall rules
- [ ] Set up monitoring (Prometheus/Grafana)
- [ ] Configure backup strategy
- [ ] Set resource limits in docker-compose
- [ ] Use Docker secrets for sensitive data
- [ ] Set up CI/CD pipeline

### Resource Limits (Optional)

Add to `docker-compose.yml`:

```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### SSL/TLS Setup

1. Obtain SSL certificate (Let's Encrypt, etc.)
2. Place certificates in `nginx/ssl/`
3. Uncomment HTTPS section in `nginx/nginx.conf`
4. Update domain name
5. Restart Nginx:
```bash
docker-compose restart nginx
```

## 🛠️ Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Check what's using port 8000
lsof -i :8000

# Or change port in docker-compose.yml
ports:
  - "8001:8000"
```

**Permission denied:**
```bash
# Fix file permissions
sudo chown -R $USER:$USER .

# Or run with sudo (not recommended)
sudo docker-compose up
```

**Container won't start:**
```bash
# Check logs
make logs-api

# Rebuild from scratch
make rebuild
```

**SEC API rate limit:**
- Wait a few seconds between requests
- Implement caching (Redis profile)
- Use proper User-Agent header

### Debug Mode

Run with debug logs:
```bash
docker-compose up
# Or
uvicorn app:app --reload --log-level debug
```

## 💡 Performance Optimization

### 1. Enable Redis Caching
```bash
make up-with-cache
```

### 2. Use Docker BuildKit
```bash
export DOCKER_BUILDKIT=1
docker-compose build
```

### 3. Multi-stage Builds
The Dockerfile uses optimized layering for faster builds and smaller images.

### 4. Nginx Caching
Add to `nginx.conf`:
```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m;
proxy_cache api_cache;
proxy_cache_valid 200 10m;
```

## 🔄 Updating the Application

### Update Code
```bash
# Pull latest changes
git pull

# Rebuild and restart
make rebuild
```

### Update Dependencies
```bash
# Update requirements.txt
# Then rebuild
docker-compose build --no-cache api
docker-compose up -d
```

## 📦 Backup & Restore

### Backup Redis Data
```bash
docker-compose exec redis redis-cli SAVE
docker cp secinsight-redis:/data/dump.rdb ./backup/
```

### Backup Logs
```bash
tar -czf logs-backup-$(date +%Y%m%d).tar.gz logs/
```

---

**Built with ❤️ using FastAPI and SEC EDGAR data**

## 📞 Support & Community

- **Issues**: Report bugs via GitHub Issues
- **Discussions**: Join our community discussions
- **Documentation**: Full API docs at `/docs`
- **Email**: support@example.com (update with your contact)

## 📄 License

This project is provided as-is for educational and research purposes. Please comply with SEC usage policies when accessing their data.

---

### Quick Reference Card

```bash
# Start
make up

# Stop
make down

# Logs
make logs

# Restart
make restart

# Shell access
make shell

# Clean up
make clean

# Full stack
make up-full
```