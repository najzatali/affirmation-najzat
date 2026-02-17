from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/magic-link")
def send_magic_link():
    return {"status": "ok", "message": "Magic link sent (stub)."}

@router.post("/oauth/callback")
def oauth_callback():
    return {"status": "ok", "message": "OAuth callback (stub)."}
