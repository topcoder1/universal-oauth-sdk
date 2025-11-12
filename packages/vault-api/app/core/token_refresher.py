"""Automatic token refresh background job"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta, timezone
import httpx
import logging
from typing import Dict

from app.database import SessionLocal
from app.models.token import Token
from app.core.encryption import get_encryption
from app.core.metrics import metrics_collector

logger = logging.getLogger(__name__)


class TokenRefresher:
    """Background service for automatic token refresh"""
    
    def __init__(self, oauth_configs: Dict):
        self.oauth_configs = oauth_configs
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
    
    def start(self):
        """Start the token refresh scheduler"""
        if self.is_running:
            logger.warning("Token refresher already running")
            return
        
        # Schedule job to run every minute
        self.scheduler.add_job(
            self.refresh_expiring_tokens,
            'interval',
            minutes=1,
            id='token_refresh',
            replace_existing=True
        )
        
        self.scheduler.start()
        self.is_running = True
        logger.info("🔄 Token refresher started (runs every 1 minute)")
    
    def stop(self):
        """Stop the token refresh scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("Token refresher stopped")
    
    async def refresh_expiring_tokens(self):
        """Check and refresh tokens expiring in the next 5 minutes"""
        db = SessionLocal()
        
        try:
            # Get tokens expiring in the next 5 minutes
            now_utc = datetime.now(timezone.utc)
            threshold = now_utc + timedelta(minutes=5)
            
            expiring_tokens = db.query(Token).filter(
                Token.expires_at.isnot(None),
                Token.expires_at <= threshold,
                Token.expires_at > now_utc,  # Not already expired
                Token.refresh_token_encrypted.isnot(None)  # Has refresh token
            ).all()
            
            if not expiring_tokens:
                logger.debug("No tokens need refreshing")
                return
            
            logger.info(f"🔄 Found {len(expiring_tokens)} token(s) to refresh")
            
            for token in expiring_tokens:
                try:
                    await self.refresh_single_token(token, db)
                except Exception as e:
                    logger.error(f"Failed to refresh token {token.id}: {e}")
                    metrics_collector.record_token_refresh(token.provider, success=False)
        
        except Exception as e:
            logger.error(f"Error in refresh_expiring_tokens: {e}")
        
        finally:
            db.close()
    
    async def refresh_single_token(self, token: Token, db):
        """Refresh a single token"""
        provider = token.provider
        config = self.oauth_configs.get(provider)
        
        if not config:
            logger.error(f"No config for provider: {provider}")
            return
        
        try:
            # Decrypt refresh token
            encryption = get_encryption()
            refresh_token_value = encryption.decrypt(token.refresh_token_encrypted)
            
            # Prepare refresh request
            refresh_data = {
                "client_id": config["client_id"],
                "client_secret": config["client_secret"],
                "refresh_token": refresh_token_value,
                "grant_type": "refresh_token"
            }
            
            # Make refresh request
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    config["token_url"],
                    data=refresh_data,
                    headers={"Accept": "application/json"},
                    timeout=10.0
                )
                
                if response.status_code != 200:
                    logger.error(f"Token refresh failed for {provider}: {response.text}")
                    metrics_collector.record_token_refresh(provider, success=False)
                    return
                
                token_response = response.json()
                
                # Encrypt new tokens
                new_access_token = encryption.encrypt(token_response.get("access_token"))
                new_refresh_token = encryption.encrypt(token_response.get("refresh_token")) if token_response.get("refresh_token") else token.refresh_token_encrypted
                
                # Calculate new expiration
                expires_in = token_response.get("expires_in")
                new_expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in) if expires_in else None
                
                # Update token in database
                token.access_token_encrypted = new_access_token
                token.refresh_token_encrypted = new_refresh_token
                token.expires_at = new_expires_at
                token.last_refreshed_at = datetime.now(timezone.utc)
                token.updated_at = datetime.now(timezone.utc)
                
                db.commit()
                
                logger.info(f"✅ Token refreshed automatically for {provider} (token_id: {token.id})")
                metrics_collector.record_token_refresh(provider, success=True)
        
        except httpx.RequestError as e:
            logger.error(f"HTTP error refreshing token: {e}")
            metrics_collector.record_token_refresh(provider, success=False)
        except Exception as e:
            logger.error(f"Unexpected error refreshing token: {e}")
            metrics_collector.record_token_refresh(provider, success=False)


# Global instance
token_refresher = None


def get_token_refresher(oauth_configs: Dict) -> TokenRefresher:
    """Get or create token refresher instance"""
    global token_refresher
    if token_refresher is None:
        token_refresher = TokenRefresher(oauth_configs)
    return token_refresher
