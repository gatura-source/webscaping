from fastapi import Request, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from utils.config import appsettings
import time
import redis.asyncio as redis

api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=False)

# Redis client - initialize this in your app startup
_redis_client = None

async def init_redis():
    """Call this during FastAPI startup"""
    global _redis_client
    _redis_client = redis.Redis(
        host=appsettings.REDIS_HOST,
        port=appsettings.REDIS_PORT,
        password=appsettings.REDIS_PASSWORD if hasattr(appsettings, 'REDIS_PASSWORD') else None,
        db=appsettings.REDIS_DB if hasattr(appsettings, 'REDIS_DB') else 0,
        decode_responses=True
    )
    await _redis_client.ping()

async def close_redis():
    """Call this during FastAPI shutdown"""
    global _redis_client
    if _redis_client:
        await _redis_client.close()

async def check_api_key(request: Request):
    api_key = request.headers.get("X-API-KEY")
    if not api_key or api_key not in appsettings.API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid API Key"
        )
    
    # Rate limit using Redis
    limit = appsettings.RATE_LIMIT_PER_HOUR
    now = time.time()
    bucket_key = f"rate_limit:{api_key}"
    
    # Use Redis pipeline for atomic operations
    pipe = _redis_client.pipeline()
    
    try:
        # Get current bucket state
        bucket_data = await _redis_client.hgetall(bucket_key)
        
        if not bucket_data:
            # Initialize new bucket
            bucket = {"tokens": str(limit), "last": str(now)}
            await _redis_client.hset(bucket_key, mapping=bucket)
            await _redis_client.expire(bucket_key, 7200)  # Expire after 2 hours of inactivity
        else:
            tokens = float(bucket_data.get("tokens", limit))
            last = float(bucket_data.get("last", now))
            
            # Refill tokens proportional to time elapsed
            elapsed = now - last
            refill = (elapsed / 3600.0) * limit
            
            if refill > 0:
                tokens = min(limit, tokens + refill)
                last = now
            
            # Check if tokens available
            if tokens < 1:
                raise HTTPException(
                    status_code=429, 
                    detail="Rate limit exceeded"
                )
            
            # Consume one token
            tokens -= 1
            
            # Update bucket in Redis
            await _redis_client.hset(
                bucket_key,
                mapping={"tokens": str(tokens), "last": str(last)}
            )
            await _redis_client.expire(bucket_key, 7200)
    
    except HTTPException:
        raise
    except Exception as e:
        # Log error but don't fail the request if Redis is down
        print(f"Redis error in rate limiting: {e}")
        # Optionally: fail open or fail closed depending on your security requirements
        raise HTTPException(status_code=503, detail="Rate limiting service unavailable")
    
    return api_key