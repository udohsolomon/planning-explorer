# Redis Setup Guide for Enrichment Agent

## Overview
The enrichment agent requires Redis for caching applicant/agent data (24h TTL).

## Current Status
- ✅ Python redis package installed (v6.4.0)
- ⚠️ Redis server not running
- ⚠️ Docker not available in current environment

## Installation Options

### Option 1: Windows WSL Redis (Recommended for WSL)
```bash
# Update package list
sudo apt update

# Install Redis
sudo apt install redis-server

# Start Redis
sudo service redis-server start

# Verify
redis-cli ping
# Should return: PONG
```

### Option 2: Native Windows Redis
```powershell
# Download Redis for Windows from:
# https://github.com/microsoftarchive/redis/releases

# Extract and run:
redis-server.exe

# Test in another terminal:
redis-cli.exe ping
```

### Option 3: Docker (if available)
```bash
docker run -d -p 6379:6379 --name planning-redis redis:latest
docker ps  # Verify running
redis-cli ping
```

### Option 4: Cloud Redis (Production)
- Use managed Redis service (AWS ElastiCache, Azure Cache, etc.)
- Update `.env` with connection details:
```env
REDIS_HOST=your-redis-host.com
REDIS_PORT=6379
REDIS_PASSWORD=your-password  # if applicable
```

## Configuration

### Environment Variables
Add to `backend/.env`:
```env
# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=  # Leave empty for local dev
ENRICHMENT_CACHE_TTL=86400  # 24 hours in seconds
```

## Testing Redis Connection

```python
# Test script: test_redis_connection.py
import redis
import asyncio

async def test_redis():
    try:
        client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        response = client.ping()
        print(f"✅ Redis connected: {response}")

        # Test set/get
        client.set("test_key", "test_value", ex=60)
        value = client.get("test_key")
        print(f"✅ Set/Get test: {value}")

        client.close()
        return True
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_redis())
```

Run:
```bash
cd backend
source venv/bin/activate
python test_redis_connection.py
```

## Next Steps After Redis Installation

1. Verify Redis is running:
   ```bash
   redis-cli ping
   ```

2. Test Python connection:
   ```bash
   python test_redis_connection.py
   ```

3. Update `.env` with Redis configuration

4. Proceed to Phase 2 (Core Agent Implementation)

## Troubleshooting

### Error: "Connection refused"
- Redis server not running
- Solution: `sudo service redis-server start` (Linux/WSL)

### Error: "redis-cli: command not found"
- Redis not installed
- Solution: Install Redis using one of the options above

### Error: "NOAUTH Authentication required"
- Redis requires password
- Solution: Add password to `.env` REDIS_PASSWORD

## Alternative: Development Without Redis

The enrichment agent can run without Redis caching (degraded mode):
- Agent still extracts data
- No caching (slower, re-scrapes every time)
- Add fallback in cache_service.py:

```python
class CacheService:
    async def connect(self, host="localhost", port=6379):
        try:
            self.redis = await redis.from_url(...)
        except Exception as e:
            logger.warning(f"Redis unavailable, running without cache: {e}")
            self.redis = None  # Graceful degradation
```

---

**Current Requirement**: Redis installation needed before testing Phase 4 (caching)
**Impact if skipped**: Agent works but slower (no caching benefit)
**Recommended**: Install Redis before production deployment
