# SEC Income Statement API

A FastAPI-based REST API for retrieving and analyzing income statement data from SEC EDGAR filings using XBRL data.

## 🚀 Features

- **Comprehensive Financial Data**: Access 23+ income statement line items including revenue, expenses, profits, EPS, and more
- **Flexible Date Filtering**: Query data by date range or get all available periods
- **Multiple Output Formats**: Get quarterly, annual, or trailing-twelve-month (TTM) data
- **Smart Period Detection**: Automatically handles quarterly (2023Q1) and annual (2023) period formats
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
├── helper.py               # Core data processing logic
├── models/
│   ├── income_statement_request.py
│   └── income_statement_response.py
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
| `required_fields` | array | ❌ No | List of income statement line items (defaults to all available fields) |
| `output_type` | string | ❌ No | "quarterly", "annual", or "ttm" (default: "quarterly") |

**Response:**
```json
{
  "cik": "320193",
  "company_name": "Apple Inc.",
  "output_type": "quarterly",
  "data": {
    "Total Revenues": [94836000000, 81797000000, 89498000000, 117154000000],
    "Cost Of Revenues": [52860000000, 45364000000, 48916000000, 64309000000],
    "Gross Profit": [41976000000, 36433000000, 40582000000, 52845000000],
    "Operating Income": [30744000000, 26574000000, 29594000000, 40323000000],
    "Net Income": [23615000000, 19881000000, 22956000000, 33916000000]
  },
  "periods": ["2023Q1", "2023Q2", "2023Q3", "2023Q4"]
}
```

### Output Type Options

#### 1. Quarterly (`"output_type": "quarterly"`)
Returns data for individual fiscal quarters (Q1, Q2, Q3, Q4).
- Period format: `2023Q1`, `2023Q2`, etc.
- Use case: Quarterly trend analysis, seasonal patterns

#### 2. Annual (`"output_type": "annual"`)
Returns data for full fiscal years from 10-K filings.
- Period format: `2023`, `2024`, etc.
- Use case: Year-over-year comparisons, long-term trends

#### 3. TTM - Trailing Twelve Months (`"output_type": "ttm"`)
Returns rolling 12-month sum calculated from quarterly data.
- Period format: `2023Q4`, `2024Q1`, etc. (period ending)
- Use case: Smoothed trends, removing seasonality
- Note: Requires at least 4 consecutive quarters of data

## 📊 Available Fields

### Revenue & Costs
- Total Revenues
- Cost Of Revenues / Cost of Revenue
- Gross Profit

### Operating Expenses
- R&D / R&D Expenses
- SG&A / Selling General & Admin Expenses
- Other Operating Expenses / Other Operating Expenses, Total
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
- Income Tax / Income Tax Expense
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

### Example 1: Get Quarterly Data for All Fields
```bash
curl -X POST "http://localhost:8000/income-statement" \
  -H "Content-Type: application/json" \
  -d '{
    "cik": "320193",
    "user_agent": "yourname@domain.com MyApp/1.0",
    "output_type": "quarterly"
  }'
```

### Example 2: Get Annual Data with Date Range
```bash
curl -X POST "http://localhost:8000/income-statement" \
  -H "Content-Type: application/json" \
  -d '{
    "cik": "1318605",
    "user_agent": "yourname@domain.com MyApp/1.0",
    "start_date": "2020-01-01",
    "end_date": "2023-12-31",
    "required_fields": [
      "Total Revenues",
      "Gross Profit",
      "Operating Income",
      "Net Income",
      "Basic EPS - Continuing Operations"
    ],
    "output_type": "annual"
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
    "output_type": "annual"
}

response = requests.post(url, json=payload)
data = response.json()

print(f"Company: {data['company_name']}")
print(f"Periods: {data['periods']}")

# Access data by field name and period index
revenues = data['data']['Total Revenues']
periods = data['periods']

for i, period in enumerate(periods):
    revenue = revenues[i]
    if revenue is not None:
        print(f"{period}: ${revenue:,.0f}")
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

// Create a table of results
console.log(`Company: ${data.company_name}`);
console.table(
  data.periods.map((period, i) => ({
    Period: period,
    Revenue: data.data['Total Revenues'][i],
    'Net Income': data.data['Net Income'][i],
    EPS: data.data['Basic EPS - Continuing Operations'][i]
  }))
);
```

### Example 6: Comparing Quarterly vs Annual vs TTM
```python
import requests
import pandas as pd

url = "http://localhost:8000/income-statement"
base_payload = {
    "cik": "320193",
    "user_agent": "yourname@domain.com MyApp/1.0",
    "start_date": "2023-01-01",
    "end_date": "2023-12-31",
    "required_fields": ["Total Revenues", "Net Income"]
}

# Get all three formats
formats = ["quarterly", "annual", "ttm"]
results = {}

for fmt in formats:
    payload = {**base_payload, "output_type": fmt}
    response = requests.post(url, json=payload)
    results[fmt] = response.json()

# Display comparison
for fmt in formats:
    print(f"\n{fmt.upper()} Data:")
    data = results[fmt]
    df = pd.DataFrame({
        'Period': data['periods'],
        'Revenue': data['data']['Total Revenues'],
        'Net Income': data['data']['Net Income']
    })
    print(df)
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
- Meta Platforms Inc.: `1326801`
- NVIDIA Corp: `1045810`

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

## 📅 Date Filtering Behavior

Date filtering works intelligently with different output types:

### Quarterly Output
- Filters quarters based on quarter end date
- `start_date: "2023-01-01"` includes quarters ending on or after Jan 1, 2023
- `end_date: "2023-12-31"` includes quarters starting on or before Dec 31, 2023

### Annual Output
- Filters fiscal years based on fiscal year end date
- `start_date: "2022-01-01"` includes fiscal years ending on or after Jan 1, 2022
- `end_date: "2024-12-31"` includes fiscal years starting on or before Dec 31, 2024

### TTM Output
- Filters TTM periods based on the ending quarter
- Same logic as quarterly, but values represent rolling 12-month sums

## 📊 Output Format

### Response Structure
The API now returns a simplified, array-based format:

```json
{
  "cik": "320193",
  "company_name": "Apple Inc.",
  "output_type": "quarterly",
  "data": {
    "Total Revenues": [value1, value2, value3, ...],
    "Net Income": [value1, value2, value3, ...]
  },
  "periods": ["2023Q1", "2023Q2", "2023Q3", ...]
}
```

### Key Points:
- **Aligned Arrays**: All data fields have the same number of elements, aligned with the `periods` array
- **Null Values**: Missing data is represented as `null` in the arrays
- **Raw Numbers**: Values are in USD (no formatting applied)
- **Period Format**: 
  - Quarterly: `2023Q1`, `2023Q2`, etc.
  - Annual: `2023`, `2024`, etc.
  - TTM: `2023Q4`, `2024Q1`, etc. (ending period)

### Accessing Data
```python
# By index
revenue_q1 = data['data']['Total Revenues'][0]  # First period
period_name = data['periods'][0]  # "2023Q1"

# Iterate through periods
for i, period in enumerate(data['periods']):
    revenue = data['data']['Total Revenues'][i]
    print(f"{period}: {revenue}")

# Create DataFrame (recommended for analysis)
import pandas as pd
df = pd.DataFrame(data['data'], index=data['periods'])
```

## ⚠️ Error Handling

Common errors and solutions:

| Error | Cause | Solution |
|-------|-------|----------|
| `404` | Invalid CIK | Verify the CIK number is correct |
| `500` | SEC API timeout | Retry after a few seconds |
| `422` | Invalid request format | Check date format (YYYY-MM-DD) and output_type value |
| `Rate limit` | Too many requests | Wait and retry with backoff |
| Empty arrays | No data for period | Check date range and data availability |

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

### Quick Test Script
```python
import requests

def test_api(cik, output_type):
    url = "http://localhost:8000/income-statement"
    payload = {
        "cik": cik,
        "user_agent": "test@example.com TestApp/1.0",
        "output_type": output_type,
        "required_fields": ["Total Revenues", "Net Income"]
    }
    
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        data = response.json()
        print(f"✓ {output_type.upper()}: {len(data['periods'])} periods")
        return True
    else:
        print(f"✗ {output_type.upper()}: {response.status_code}")
        return False

# Test all output types
print("Testing Apple Inc. (CIK: 320193)")
for output_type in ["quarterly", "annual", "ttm"]:
    test_api("320193", output_type)
```

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
4. **Choose appropriate output type**: 
   - Use `annual` for year-over-year analysis (fewer data points)
   - Use `quarterly` for detailed trend analysis
   - Use `ttm` for smoothed, comparable metrics

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

**Empty data arrays:**
- Check if the company has filed the required forms (10-Q for quarterly, 10-K for annual)
- Verify date range includes actual filing periods
- Some fields may not be reported by all companies

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

## 📄 Updating the Application

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

---

## 📈 Example Use Cases

### 1. Financial Dashboard
```python
# Create a simple financial dashboard
import requests
import pandas as pd
import matplotlib.pyplot as plt

def fetch_data(cik, output_type="quarterly"):
    response = requests.post(
        "http://localhost:8000/income-statement",
        json={
            "cik": cik,
            "user_agent": "dashboard@example.com Dashboard/1.0",
            "output_type": output_type,
            "required_fields": ["Total Revenues", "Net Income", "Operating Income"]
        }
    )
    return response.json()

# Fetch data
data = fetch_data("320193")
df = pd.DataFrame(data['data'], index=data['periods'])

# Plot
df.plot(figsize=(12, 6))
plt.title(f"{data['company_name']} - Financial Performance")
plt.ylabel("USD")
plt.xlabel("Period")
plt.legend()
plt.grid(True)
plt.show()
```

### 2. Multi-Company Comparison
```python
# Compare multiple companies
companies = {
    "Apple": "320193",
    "Microsoft": "789019",
    "Tesla": "1318605"
}

results = {}
for name, cik in companies.items():
    data = fetch_data(cik, "annual")
    results[name] = pd.DataFrame(data['data'], index=data['periods'])

# Compare revenues
for name, df in results.items():
    plt.plot(df.index, df['Total Revenues'], marker='o', label=name)

plt.title("Revenue Comparison")
plt.ylabel("Revenue (USD)")
plt.xlabel("Year")
plt.legend()
plt.grid(True)
plt.show()
```

### 3. Margin Analysis
```python
# Calculate and analyze profit margins
data = fetch_data("320193", "ttm")
df = pd.DataFrame(data['data'], index=data['periods'])

# Calculate margins
df['Gross Margin %'] = (df['Gross Profit'] / df['Total Revenues']) * 100
df['Operating Margin %'] = (df['Operating Income'] / df['Total Revenues']) * 100
df['Net Margin %'] = (df['Net Income'] / df['Total Revenues']) * 100

# Plot margins
margins = df[['Gross Margin %', 'Operating Margin %', 'Net Margin %']]
margins.plot(figsize=(12, 6))
plt.title("Profit Margins Over Time (TTM)")
plt.ylabel("Margin (%)")
plt.xlabel("Period")
plt.legend()
plt.grid(True)
plt.show()
```