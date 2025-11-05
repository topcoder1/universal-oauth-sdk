"""Token refresh scheduler using APScheduler"""

import asyncio
import httpx
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging

from app.database import SessionLocal
from app.models.token import Token
from app.core.encryption import get_encryption
from app.core.webhooks import send_webhook_async

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = AsyncIOScheduler()


async def refresh_expiring_tokens():
    """
    Check for tokens expiring in next 5 minutes and refresh them.
    
    This runs every minute to ensure tokens are refreshed before expiration.
    """
    db = SessionLocal()
    try:
        # Find tokens expiring in next 5 minutes
        threshold = datetime.utcnow() + timedelta(minutes=5)
        now = datetime.utcnow()
        
        expiring_tokens = db.query(Token).filter(
            Token.expires_at <= threshold,
            Token.expires_at > now,
            Token.refresh_token_encrypted.isnot(None)
        ).all()
        
        logger.info(f"Found {len(expiring_tokens)} tokens to refresh")
        
        for token in expiring_tokens:
            try:
                await refresh_single_token(token, db)
            except Exception as e:
                logger.error(f"Failed to refresh token {token.id}: {e}")
                # Send failure webhook
                try:
                    await send_webhook_async(
                        token.tenant_id,
                        'token.refresh_failed',
                        {
                            'token_id': str(token.id),
                            'provider': token.provider,
                            'key': token.key,
                            'error': str(e)
                        },
                        db
                    )
                except Exception as webhook_error:
                    logger.error(f"Failed to send webhook: {webhook_error}")
        
    finally:
        db.close()


async def refresh_single_token(token: Token, db: Session):
    """
    Refresh a single OAuth token.
    
    Args:
        token: Token to refresh
        db: Database session
    """
    logger.info(f"Refreshing token {token.id} for provider {token.provider}")
    
    # Decrypt refresh token
    encryption = get_encryption()
    refresh_token = encryption.decrypt(token.refresh_token_encrypted)
    
    # Get provider configuration
    # For MVP, we'll use a simple mapping
    # In production, load from provider registry
    provider_configs = {
        'google': {
            'token_url': 'https://oauth2.googleapis.com/token',
            'grant_type': 'refresh_token'
        },
        'github': {
            'token_url': 'https://github.com/login/oauth/access_token',
            'grant_type': 'refresh_token'
        },
        'microsoft': {
            'token_url': 'https://login.microsoftonline.com/common/oauth2/v2.0/token',
            'grant_type': 'refresh_token'
        },
        # Add more providers as needed
    }
    
    provider_config = provider_configs.get(token.provider)
    if not provider_config:
        raise ValueError(f"Provider {token.provider} not configured for refresh")
    
    # Make refresh request
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            provider_config['token_url'],
            data={
                'grant_type': provider_config['grant_type'],
                'refresh_token': refresh_token,
                'client_id': token.client_id if hasattr(token, 'client_id') else None,
                'client_secret': token.client_secret if hasattr(token, 'client_secret') else None,
            },
            headers={'Accept': 'application/json'}
        )
    
    if response.status_code != 200:
        raise Exception(f"OAuth refresh failed: {response.status_code} {response.text}")
    
    # Parse response
    data = response.json()
    new_access_token = data.get('access_token')
    new_refresh_token = data.get('refresh_token', refresh_token)  # Some providers don't return new refresh token
    expires_in = data.get('expires_in', 3600)
    
    # Update token in database
    token.access_token_encrypted = encryption.encrypt(new_access_token)
    token.refresh_token_encrypted = encryption.encrypt(new_refresh_token)
    token.expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
    token.last_refreshed_at = datetime.utcnow()
    token.updated_at = datetime.utcnow()
    
    db.commit()
    
    logger.info(f"Successfully refreshed token {token.id}")
    
    # Send success webhook
    try:
        await send_webhook_async(
            token.tenant_id,
            'token.refreshed',
            {
                'token_id': str(token.id),
                'provider': token.provider,
                'key': token.key,
                'expires_at': token.expires_at.isoformat(),
                'refreshed_at': token.last_refreshed_at.isoformat()
            },
            db
        )
    except Exception as e:
        logger.error(f"Failed to send webhook: {e}")


def start_scheduler():
    """Start the token refresh scheduler"""
    # Schedule refresh job to run every minute
    scheduler.add_job(
        refresh_expiring_tokens,
        trigger=IntervalTrigger(minutes=1),
        id='refresh_tokens',
        name='Refresh expiring OAuth tokens',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("Token refresh scheduler started")


def stop_scheduler():
    """Stop the scheduler"""
    scheduler.shutdown()
    logger.info("Token refresh scheduler stopped")
