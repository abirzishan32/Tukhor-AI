from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from utils.supabase import supabase

security = HTTPBearer(auto_error=False)

async def verify_session(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = None
    # Try Authorization header first
    if credentials and credentials.scheme == "Bearer":
        token = credentials.credentials
    else:
        # Fallback to cookie
        cookie = request.cookies.get("access_token")
        if cookie and cookie.startswith("Bearer "):
            token = cookie.split(" ", 1)[1]

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    data = supabase.auth.get_user(token)
    # logger.info(f"Session data: {data}")
    user = data.user if hasattr(data, "user") else data  # supabase-py returns differently by version
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    return user
