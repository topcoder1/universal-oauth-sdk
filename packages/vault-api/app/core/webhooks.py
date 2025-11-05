"""Webhook delivery system"""

import hmac
import hashlib
import httpx
import json
from datetime import datetime
from typing import Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
import logging

from app.models.webhook import Webhook

logger = logging.getLogger(__name__)


def create_signature(secret: str, timestamp: int, payload: Dict[Any, Any]) -> str:
    """
    Create HMAC-SHA256 signature for webhook.
    
    Args:
        secret: Webhook secret
        timestamp: Unix timestamp
        payload: Webhook payload
        
    Returns:
        str: HMAC signature
    """
    message = f"{timestamp}.{json.dumps(payload, sort_keys=True)}"
    return hmac.new(
        secret.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()


async def send_webhook_async(
    tenant_id: UUID,
    event_type: str,
    payload: Dict[Any, Any],
    db: Session
):
    """
    Send webhook to all registered endpoints for a tenant.
    
    Args:
        tenant_id: Tenant ID
        event_type: Event type (e.g., 'token.refreshed')
        payload: Event payload
        db: Database session
    """
    # Find all webhooks for this tenant that subscribe to this event
    webhooks = db.query(Webhook).filter(
        Webhook.tenant_id == tenant_id,
        Webhook.enabled == True,
        Webhook.events.contains([event_type])
    ).all()
    
    if not webhooks:
        logger.debug(f"No webhooks registered for {event_type} on tenant {tenant_id}")
        return
    
    # Send to each webhook
    for webhook in webhooks:
        try:
            await deliver_webhook(webhook, event_type, payload)
        except Exception as e:
            logger.error(f"Failed to deliver webhook {webhook.id}: {e}")


async def deliver_webhook(
    webhook: Webhook,
    event_type: str,
    payload: Dict[Any, Any],
    max_retries: int = 3
):
    """
    Deliver a webhook with retries.
    
    Args:
        webhook: Webhook configuration
        event_type: Event type
        payload: Event payload
        max_retries: Maximum retry attempts
    """
    timestamp = int(datetime.utcnow().timestamp())
    
    # Create signature if secret is configured
    signature = None
    if webhook.secret:
        signature = create_signature(webhook.secret, timestamp, payload)
    
    # Prepare headers
    headers = {
        'Content-Type': 'application/json',
        'X-Vault-Event': event_type,
        'X-Vault-Delivery': str(webhook.id),
    }
    
    if signature:
        headers['X-Vault-Signature'] = f't={timestamp},v1={signature}'
    
    # Attempt delivery with retries
    last_error = None
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    webhook.url,
                    json=payload,
                    headers=headers
                )
            
            if response.status_code < 500:
                # Success or client error (don't retry)
                logger.info(
                    f"Webhook delivered to {webhook.url}: "
                    f"{response.status_code} (attempt {attempt + 1})"
                )
                return
            else:
                # Server error, will retry
                last_error = f"HTTP {response.status_code}: {response.text}"
                logger.warning(
                    f"Webhook delivery failed (attempt {attempt + 1}/{max_retries}): "
                    f"{last_error}"
                )
        
        except Exception as e:
            last_error = str(e)
            logger.warning(
                f"Webhook delivery error (attempt {attempt + 1}/{max_retries}): {e}"
            )
        
        # Wait before retry (exponential backoff)
        if attempt < max_retries - 1:
            await asyncio.sleep(2 ** attempt)
    
    # All retries failed
    logger.error(f"Webhook delivery failed after {max_retries} attempts: {last_error}")
    raise Exception(f"Webhook delivery failed: {last_error}")


import asyncio
