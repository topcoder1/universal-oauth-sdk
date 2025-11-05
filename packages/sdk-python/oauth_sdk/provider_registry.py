"""Provider registry for loading OAuth provider configurations

Based on Node SDK providerRegistry.ts implementation.
"""

from typing import Optional, Dict, Any
import json
from pathlib import Path

from oauth_sdk.models import Provider
from oauth_sdk.exceptions import ProviderNotFoundError


class ProviderRegistry:
    """Registry for OAuth provider configurations
    
    Loads provider manifests from JSON files and caches them.
    """

    def __init__(self, manifest_dir: Optional[str] = None, providers: Optional[list[Provider]] = None):
        """Initialize provider registry
        
        Args:
            manifest_dir: Directory containing provider manifest JSON files
            providers: Optional list of Provider objects to pre-load
        """
        self.manifest_dir = manifest_dir or self._get_default_manifest_dir()
        self._providers: Dict[str, Provider] = {}
        
        # Pre-load providers if provided
        if providers:
            for provider in providers:
                self._providers[provider.id] = provider

    def _get_default_manifest_dir(self) -> str:
        """Get default manifest directory
        
        Points to ../provider-catalog/manifests relative to this file
        """
        # Go up from oauth_sdk/ to packages/sdk-python/ to packages/ to provider-catalog/manifests
        current_file = Path(__file__)
        sdk_python_dir = current_file.parent.parent  # packages/sdk-python
        packages_dir = sdk_python_dir.parent  # packages
        manifest_dir = packages_dir / "provider-catalog" / "manifests"
        return str(manifest_dir)

    def add(self, provider: Provider) -> None:
        """Add a provider to the registry
        
        Args:
            provider: Provider object to add
        """
        self._providers[provider.id] = provider

    def get(self, provider_id: str) -> Optional[Provider]:
        """Get provider configuration (synchronous, from cache only)
        
        Args:
            provider_id: Provider ID (e.g., 'google', 'github')
            
        Returns:
            Provider object or None if not found in cache
        """
        return self._providers.get(provider_id)

    async def load_provider(self, provider_id: str) -> Provider:
        """Load provider configuration from JSON file
        
        Args:
            provider_id: Provider ID (e.g., 'google', 'github')
            
        Returns:
            Provider object
            
        Raises:
            ProviderNotFoundError: If provider manifest file not found
        """
        # Try to load from JSON file
        manifest_path = Path(self.manifest_dir) / f"{provider_id}.json"
        
        if not manifest_path.exists():
            raise ProviderNotFoundError(
                f"Provider '{provider_id}' not found. "
                f"Expected manifest at: {manifest_path}"
            )
        
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Parse provider manifest
            provider = Provider(
                id=data.get("name", provider_id),
                name=data.get("displayName", provider_id),
                auth_url=data["authorizationEndpoint"],
                token_url=data["tokenEndpoint"],
                scopes=data.get("scopes", []),
                default_scopes=data.get("scopes", []),
                pkce=data.get("pkceRecommended", False),
                metadata=data,
            )
            
            return provider
            
        except (json.JSONDecodeError, KeyError) as e:
            raise ProviderNotFoundError(
                f"Failed to parse provider manifest for '{provider_id}': {e}"
            ) from e
        except Exception as e:
            raise ProviderNotFoundError(
                f"Failed to load provider '{provider_id}': {e}"
            ) from e

    async def get_provider(self, provider_id: str) -> Provider:
        """Get provider configuration (cached or load from file)
        
        Args:
            provider_id: Provider ID (e.g., 'google', 'github')
            
        Returns:
            Provider object
            
        Raises:
            ProviderNotFoundError: If provider not found
        """
        # Check cache first
        if provider_id in self._providers:
            return self._providers[provider_id]
        
        # Load from file
        provider = await self.load_provider(provider_id)
        
        # Cache it
        self._providers[provider_id] = provider
        
        return provider

    async def list_providers(self) -> list[str]:
        """List all available provider IDs from manifest directory
        
        Returns:
            List of provider IDs
        """
        manifest_dir = Path(self.manifest_dir)
        
        if not manifest_dir.exists():
            return []
        
        # Find all .json files
        provider_ids = []
        for file_path in manifest_dir.glob("*.json"):
            # Use filename without extension as provider ID
            provider_ids.append(file_path.stem)
        
        return sorted(provider_ids)
    
    @classmethod
    def load_from_dir(cls, manifest_dir: str) -> "ProviderRegistry":
        """Load all providers from a directory
        
        Args:
            manifest_dir: Directory containing provider JSON files
            
        Returns:
            ProviderRegistry with all providers loaded
        """
        registry = cls(manifest_dir=manifest_dir)
        
        # Load all JSON files synchronously
        manifest_path = Path(manifest_dir)
        if manifest_path.exists():
            for file_path in manifest_path.glob("*.json"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    provider = Provider(
                        id=data.get("name", file_path.stem),
                        name=data.get("displayName", file_path.stem),
                        auth_url=data["authorizationEndpoint"],
                        token_url=data["tokenEndpoint"],
                        scopes=data.get("scopes", []),
                        default_scopes=data.get("scopes", []),
                        pkce=data.get("pkceRecommended", False),
                        metadata=data,
                    )
                    
                    registry.add(provider)
                except Exception:
                    # Skip invalid manifests
                    continue
        
        return registry
