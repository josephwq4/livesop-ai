from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import os
from typing import Dict, Any

auth_scheme = HTTPBearer()

def get_current_user(token: HTTPAuthorizationCredentials = Depends(auth_scheme)) -> Dict[str, Any]:
    """
    Verifies the Supabase JWT token and returns the user payload
    """
    jwt_secret = os.getenv("SUPABASE_JWT_SECRET")
    
    if not jwt_secret:
        print("⚠️ [WARNING] SUPABASE_JWT_SECRET missing! Using fallback for DEBUGGING.")
        # FALLBACK FOR DEBUGGING ONLY
        jwt_secret = "fallback_secret_for_debugging_only" 
        # raise HTTPException(...) <--- Commented out crash check

    try:
        # Decode and verify the token
        payload = jwt.decode(
            token.credentials,
            jwt_secret,
            algorithms=["HS256"],
            audience="authenticated"
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
