"""Webhook delivery system with retry logic"""
import httpx
import hmac
import hashlib
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import asyncio

logger = logging.getLogger(__name__)


class WebhookDelivery:
    """Webhook delivery with retry and signature"""
    
    def __init__(self):
        self.max_retries = 3
        self.retry_delays = [1, 5, 15]  # seconds
    
    async def deliver(
        self,
        url: str,
        event_type: str,
        payload: Dict[str, Any],
        secret: Optional[str] = None
    ) -> bool:
        """
        Deliver webhook with retry logic
        
        Args:
            url: Webhook endpoint URL
            event_type: Event type (e.g., 'token.created')
            payload: Event payload
            secret: Optional secret for signature
        
        Returns:
            bool: True if delivered successfully
        """
        # Prepare webhook payload
        webhook_payload = {
            "event": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": payload
        }
        
        # Generate signature if secret provided
        headers = {"Content-Type": "application/json"}
        if secret:
            signature = self._generate_signature(webhook_payload, secret)
            headers["X-Webhook-Signature"] = signature
        
        # Try delivery with retries
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.post(
                        url,
                        json=webhook_payload,
                        headers=headers
                    )
                    
                    if response.status_code in [200, 201, 202, 204]:
                        logger.info(f"✅ Webhook delivered: {event_type} to {url}")
                        return True
                    else:
                        logger.warning(
                            f"⚠️  Webhook delivery failed (attempt {attempt + 1}/{self.max_retries}): "
                            f"{response.status_code} - {url}"
                        )
            
            except httpx.RequestError as e:
                logger.error(
                    f"❌ Webhook delivery error (attempt {attempt + 1}/{self.max_retries}): "
                    f"{str(e)} - {url}"
                )
            
            # Wait before retry (except on last attempt)
            if attempt < self.max_retries - 1:
                await asyncio.sleep(self.retry_delays[attempt])
        
        logger.error(f"❌ Webhook delivery failed after {self.max_retries} attempts: {url}")
        return False
    
    def _generate_signature(self, payload: Dict[str, Any], secret: str) -> str:
        """Generate HMAC signature for webhook payload"""
        payload_bytes = json.dumps(payload, sort_keys=True).encode('utf-8')
        signature = hmac.new(
            secret.encode('utf-8'),
            payload_bytes,
            hashlib.sha256
        ).hexdigest()
        return f"sha256={signature}"
    
    @staticmethod
    def verify_signature(payload: str, signature: str, secret: str) -> bool:
        """Verify webhook signature"""
        expected_signature = hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        expected = f"sha256={expected_signature}"
        return hmac.compare_digest(expected, signature)


class WebhookManager:
    """Manage webhook subscriptions and delivery"""
    
    def __init__(self):
        self.delivery = WebhookDelivery()
    
    async def trigger_event(
        self,
        event_type: str,
        payload: Dict[str, Any],
        db
    ):
        """
        Trigger webhook event for all subscribed webhooks
        
        Args:
            event_type: Event type (e.g., 'token.created')
            payload: Event payload
            db: Database session
        """
        from app.models.webhook import Webhook
        
        try:
            # Get all webhooks subscribed to this event
            webhooks = db.query(Webhook).filter(
                Webhook.enabled == True,
                Webhook.events.contains([event_type])
            ).all()
            
            if not webhooks:
                logger.debug(f"No webhooks subscribed to {event_type}")
                return
            
            logger.info(f"📤 Triggering {event_type} for {len(webhooks)} webhook(s)")
            
            # Deliver to all webhooks (in parallel)
            tasks = []
            for webhook in webhooks:
                task = self.delivery.deliver(
                    url=webhook.url,
                    event_type=event_type,
                    payload=payload,
                    secret=webhook.secret
                )
                tasks.append(task)
            
            # Wait for all deliveries
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Log results
            success_count = sum(1 for r in results if r is True)
            logger.info(f"📊 Webhook delivery: {success_count}/{len(webhooks)} successful")
        
        except Exception as e:
            logger.error(f"Error triggering webhook event: {e}")


# Global webhook manager
webhook_manager = WebhookManager()


# Event payload builders
def build_token_created_payload(token) -> Dict[str, Any]:
    """Build payload for token.created event"""
    return {
        "token_id": str(token.id),
        "provider": token.provider,
        "created_at": token.created_at.isoformat() if token.created_at else None,
        "expires_at": token.expires_at.isoformat() if token.expires_at else None
    }


def build_token_refreshed_payload(token) -> Dict[str, Any]:
    """Build payload for token.refreshed event"""
    return {
        "token_id": str(token.id),
        "provider": token.provider,
        "refreshed_at": token.last_refreshed_at.isoformat() if token.last_refreshed_at else None,
        "expires_at": token.expires_at.isoformat() if token.expires_at else None
    }


def build_token_expired_payload(token) -> Dict[str, Any]:
    """Build payload for token.expired event"""
    return {
        "token_id": str(token.id),
        "provider": token.provider,
        "expired_at": token.expires_at.isoformat() if token.expires_at else None
    }


def build_token_deleted_payload(token_id: str, provider: str) -> Dict[str, Any]:
    """Build payload for token.deleted event"""
    return {
        "token_id": token_id,
        "provider": provider,
        "deleted_at": datetime.now(timezone.utc).isoformat()
    }


def build_token_refresh_failed_payload(token) -> Dict[str, Any]:
    """Build payload for token.refresh_failed event"""
    return {
        "token_id": str(token.id),
        "provider": token.provider,
        "failed_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": token.expires_at.isoformat() if token.expires_at else None
    }
