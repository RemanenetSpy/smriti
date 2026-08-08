"""
Smriti — Billing Route
============================
Stripe Checkout integration for premium tier subscriptions.
POST /billing/checkout — Create a Stripe checkout session
GET  /billing/usage    — Current usage statistics
POST /billing/keys     — Generate a new API key
"""

from __future__ import annotations

import logging
import os

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from smriti_core.models import (
    BillingCheckoutRequest,
    BillingCheckoutResponse,
    TierName,
    TIER_LIMITS,
    UsageStats,
)
from api.auth import verify_api_key, generate_api_key, hash_api_key
from api.deps import get_memory_store

logger = logging.getLogger("smriti.routes.billing")

router = APIRouter(prefix="/billing", tags=["Billing"])


class KeyRequest(BaseModel):
    """Body for POST /billing/keys."""
    email:    str | None = None
    cf_token: str | None = None
    use_case: str | None = None

# Razorpay plan IDs (set these in your Razorpay dashboard)
RAZORPAY_PLAN_IDS = {
    TierName.BUILDER: os.getenv("RAZORPAY_PLAN_BUILDER", "plan_builder_placeholder"),
    TierName.SCALE: os.getenv("RAZORPAY_PLAN_SCALE", "plan_scale_placeholder"),
}


@router.post("/checkout", response_model=BillingCheckoutResponse)
async def create_checkout(
    request: BillingCheckoutRequest,
    key_info: dict = Depends(verify_api_key),
):
    """
    Create a Stripe Checkout session for upgrading to Builder ($49/mo)
    or Scale ($249/mo).
    """
    if request.tier == TierName.EXPLORER:
        raise HTTPException(
            status_code=400,
            detail="Explorer tier is free. No checkout needed.",
        )

    key_id = os.getenv("RAZORPAY_KEY_ID")
    key_secret = os.getenv("RAZORPAY_KEY_SECRET")
    if not key_id or not key_secret:
        raise HTTPException(
            status_code=503,
            detail="Razorpay not configured (missing key_id/key_secret). Contact support.",
        )

    try:
        import razorpay
        client = razorpay.Client(auth=(key_id, key_secret))

        plan_id = RAZORPAY_PLAN_IDS.get(request.tier)
        if not plan_id:
            raise HTTPException(status_code=400, detail="Invalid tier.")

        # Create a Razorpay subscription link
        subscription_data = {
            "plan_id": plan_id,
            "total_count": 12,  # e.g., 12 months billing cycle
            "quantity": 1,
            "notes": {
                "source_id": key_info["source_id"],
                "tier": request.tier.value,
            }
        }
        
        sub = client.subscription.create(subscription_data)

        logger.info(
            f"Razorpay subscription created for source={key_info['source_id']} "
            f"tier={request.tier.value}"
        )

        return BillingCheckoutResponse(
            checkout_url=sub.get("short_url", ""),
            session_id=sub.get("id", ""),
        )

    except ImportError:
        raise HTTPException(
            status_code=503,
            detail="Razorpay SDK not installed. Run: pip install razorpay",
        )
    except Exception as e:
        logger.error(f"Razorpay checkout failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/usage")
async def get_usage(
    key_info: dict = Depends(verify_api_key),
):
    """
    Get current usage statistics and tier limits.
    """
    source_id = key_info["source_id"]
    memory = get_memory_store()
    usage = await memory.get_usage(source_id)

    if not usage:
        usage = UsageStats(source_id=source_id)

    tier = usage.tier
    limits = TIER_LIMITS[tier]

    return {
        "source_id": source_id,
        "tier": tier.value,
        "usage": {
            "events": {
                "used": usage.events_used,
                "limit": limits.events_per_month,
                "remaining": max(0, limits.events_per_month - usage.events_used),
            },
            "orchestration": {
                "used": usage.orchestration_used,
                "limit": limits.orchestration_per_month,
                "remaining": (
                    "unlimited" if limits.orchestration_per_month == -1
                    else max(0, limits.orchestration_per_month - usage.orchestration_used)
                ),
            },
            "connectors": {
                "used": usage.connectors_used,
                "limit": limits.connected_tools,
            },
        },
        "limits": {
            "retention_days": limits.retention_days,
            "agent_threads": limits.agent_threads,
            "event_overage_per_1k": limits.event_overage_per_1k,
            "orchestration_overage": limits.orchestration_overage,
        },
        "period_start": usage.period_start.isoformat(),
    }


@router.post("/keys")
async def generate_new_key(
    request: Request,
    body: KeyRequest,
    tier: TierName = TierName.EXPLORER,
):
    """
    Generate a new API key.
    Protected by: Cloudflare Turnstile captcha + IP rate limit (3/day) + email deduplication.
    Returns the key ONCE — store it securely.
    """
    import hashlib
    import uuid
    from datetime import datetime, timezone

    email    = body.email
    cf_token = body.cf_token

    ip = (request.client.host if request.client else None) or "unknown"

    # ── 1. Cloudflare Turnstile verification ─────────────────────────────────
    # Strip control chars from env vars (guards against newline-in-secret bug)
    import re as _re
    def _clean_env(key: str) -> str:
        return _re.sub(r"[\x00-\x1f\x7f]", "", os.getenv(key, ""))

    turnstile_secret = _clean_env("TURNSTILE_SECRET") or "1x0000000000000000000000000000000AA"
    is_test_secret   = turnstile_secret == "1x0000000000000000000000000000000AA"

    # Emergency escape hatch: set SKIP_CAPTCHA=true in HF Spaces to bypass
    # Turnstile entirely while debugging. Remove once widget is confirmed working.
    skip_captcha = os.getenv("SKIP_CAPTCHA", "").strip().lower() in ("1", "true", "yes")

    if not is_test_secret and not skip_captcha:
        if not cf_token:
            raise HTTPException(status_code=400, detail="Captcha token required.")

        cf_verified = False
        try:
            import httpx
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.post(
                    "https://challenges.cloudflare.com/turnstile/v0/siteverify",
                    data={
                        "secret":   turnstile_secret,
                        "response": cf_token,
                        "remoteip": ip,
                    },
                )
            raw_body = resp.text
            logger.info(f"Turnstile siteverify HTTP {resp.status_code}: {raw_body[:300]}")
            try:
                result = resp.json()
                cf_verified = bool(result.get("success"))
                if not cf_verified:
                    codes = result.get("error-codes", [])
                    logger.warning(
                        f"Turnstile rejected: ip={ip} codes={codes} response={result}"
                    )
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            f"Captcha verification failed "
                            f"({', '.join(codes) if codes else 'check site/secret key pair'}). "
                            "Please refresh and try again."
                        ),
                    )
            except HTTPException:
                raise
            except Exception as json_err:
                logger.error(
                    f"Turnstile siteverify returned non-JSON "
                    f"(HTTP {resp.status_code}): {raw_body[:300]} — {json_err}"
                )
                raise HTTPException(
                    status_code=503,
                    detail="Captcha service returned an unexpected response. Try again.",
                )
        except HTTPException:
            raise
        except Exception as net_err:
            logger.warning(
                f"Turnstile network error ({type(net_err).__name__}): {net_err} "
                f"— allowing request through (fail-open)"
            )
            # Fail-open: if Cloudflare's servers are unreachable, don't block users.
            # IP rate-limiting below still provides abuse protection.

    # ── 2. IP rate limiting — 3 keys per IP per calendar day ────────────────
    # Module-level store (resets on restart; good enough for HF Spaces)
    if not hasattr(generate_new_key, "_ip_log"):
        generate_new_key._ip_log: dict = {}  # type: ignore[attr-defined]

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    log = generate_new_key._ip_log
    key = f"{ip}:{today}"
    count = log.get(key, 0)
    if count >= 3:
        raise HTTPException(
            status_code=429,
            detail="Maximum 3 API keys per IP per day. Try again tomorrow.",
        )

    # ── 3. Email deduplication — 1 key per email address ────────────────────
    if not hasattr(generate_new_key, "_email_hashes"):
        generate_new_key._email_hashes: set = set()  # type: ignore[attr-defined]

    if email:
        email_hash = hashlib.sha256(email.strip().lower().encode()).hexdigest()
        if email_hash in generate_new_key._email_hashes:
            raise HTTPException(
                status_code=409,
                detail="An API key already exists for this email. Check your inbox or contact support.",
            )
    else:
        email_hash = None

    # ── 4. Generate ──────────────────────────────────────────────────────────
    memory = get_memory_store()
    raw_key = generate_api_key()
    key_hash = hash_api_key(raw_key)
    source_id = f"src_{uuid.uuid4().hex[:16]}"

    await memory.register_api_key(key_hash, source_id, tier)

    # Commit rate-limit & email records only after successful DB write
    log[key] = count + 1
    if email_hash:
        generate_new_key._email_hashes.add(email_hash)

    logger.info(
        f"API key generated source={source_id} tier={tier.value} "
        f"ip={ip} email={'set' if email else 'none'}"
    )

    return {
        "api_key": raw_key,
        "source_id": source_id,
        "tier": tier.value,
        "message": (
            "⚠️ Save this API key now — it cannot be retrieved later. "
            "Include it as the X-API-Key header on all requests."
        ),
    }
