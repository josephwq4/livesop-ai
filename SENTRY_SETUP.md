# Phase D: Sentry Integration Setup Guide

## Option 1: Using Sentry (Recommended for Production)

### 1. Install Sentry SDK
```bash
pip install sentry-sdk[fastapi]
```

### 2. Add to requirements.txt
```
sentry-sdk[fastapi]==1.39.2
```

### 3. Initialize in main.py

Add at the top of `backend/app/main.py`:

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration

# Initialize Sentry (only if DSN is configured)
if os.getenv("SENTRY_DSN"):
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        integrations=[
            StarletteIntegration(transaction_style="endpoint"),
            FastApiIntegration(transaction_style="endpoint"),
        ],
        # Set traces_sample_rate to 1.0 to capture 100% of transactions for performance monitoring
        traces_sample_rate=0.1,  # 10% sampling for performance
        # Set profiles_sample_rate to 1.0 to profile 100% of sampled transactions
        profiles_sample_rate=0.1,
        environment=os.getenv("ENVIRONMENT", "production"),
        release=f"livesop-backend@1.0.0",
    )
    print("✅ Sentry initialized")
else:
    print("⚠️ SENTRY_DSN not configured. Error tracking disabled.")
```

### 4. Add Environment Variable in Render

Go to Render Dashboard → Your Service → Environment:
```
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
ENVIRONMENT=production
```

### 5. Get Your Sentry DSN

1. Go to https://sentry.io
2. Create account (free tier available)
3. Create new project → Select "FastAPI"
4. Copy the DSN from project settings

---

## Option 2: Simple Logging (No External Service)

If you don't want to use Sentry, enhance Python logging:

### Add to main.py:

```python
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Console output (Render logs)
        RotatingFileHandler(
            'logs/app.log',
            maxBytes=10485760,  # 10MB
            backupCount=5
        )
    ]
)

logger = logging.getLogger("livesop")
```

### Use in your code:

```python
from logging import getLogger
logger = getLogger("livesop")

# Instead of print statements:
logger.info("Signal processed successfully")
logger.warning("Low confidence signal detected")
logger.error("Failed to create Jira ticket", exc_info=True)
```

---

## Recommendation

**For MVP/Beta**: Use Option 2 (Simple Logging)
- No external dependencies
- Free
- Works immediately
- Render captures all console output

**For Production**: Use Option 1 (Sentry)
- Automatic error grouping
- Stack traces with context
- Performance monitoring
- Alerts when errors spike
- Free tier: 5,000 errors/month

---

## Current Status

✅ Health checks implemented
✅ Webhook reliability hardened
✅ Timeout protection added
✅ Graceful failure handling

⏸️ Sentry integration (optional - add when ready)

The system will work perfectly without Sentry. Add it when you're ready to scale.
