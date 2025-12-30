"""Price and TVL data services."""

import httpx
from typing import Optional, Dict, List
from decimal import Decimal
from datetime import datetime

from app.config import settings


class PriceService:
    """Price data service with CoinGecko and DeFiLlama integration."""

    def __init__(self):
        self.coingecko_base = "https://api.coingecko.com/api/v3"
        self.defillama_base = "https://coins.llama.fi"
        self._cache: Dict[str, tuple] = {}  # Simple in-memory cache
        self._cache_ttl = 60  # seconds

    def _get_cached(self, key: str) -> Optional[Decimal]:
        """Get value from cache if not expired."""
        if key in self._cache:
            price, timestamp = self._cache[key]
            if datetime.now().timestamp() - timestamp < self._cache_ttl:
                return price
        return None

    def _set_cached(self, key: str, price: Decimal) -> None:
        """Set value in cache."""
        self._cache[key] = (price, datetime.now().timestamp())

    async def get_price_coingecko(self, coingecko_id: str) -> Optional[Decimal]:
        """Fetch price from CoinGecko API."""
        cache_key = f"cg_{coingecko_id}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        async with httpx.AsyncClient() as client:
            try:
                headers = {}
                if settings.coingecko_api_key:
                    headers["x-cg-demo-api-key"] = settings.coingecko_api_key

                response = await client.get(
                    f"{self.coingecko_base}/simple/price",
                    params={"ids": coingecko_id, "vs_currencies": "usd"},
                    headers=headers,
                    timeout=10,
                )
                response.raise_for_status()
                data = response.json()

                if coingecko_id in data and "usd" in data[coingecko_id]:
                    price = Decimal(str(data[coingecko_id]["usd"]))
                    self._set_cached(cache_key, price)
                    return price
                return None
            except Exception as e:
                print(f"CoinGecko error for {coingecko_id}: {e}")
                return None

    async def get_price_defillama(
        self, chain: str, contract: str
    ) -> Optional[Decimal]:
        """Fetch price from DeFiLlama Prices API."""
        cache_key = f"dl_{chain}_{contract}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        # Map common chain names to DeFiLlama format
        chain_map = {
            "ethereum": "ethereum",
            "arbitrum": "arbitrum",
            "base": "base",
            "polygon": "polygon",
            "optimism": "optimism",
        }
        dl_chain = chain_map.get(chain.lower(), chain.lower())
        coin_id = f"{dl_chain}:{contract}"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.defillama_base}/prices/current/{coin_id}",
                    timeout=10,
                )
                response.raise_for_status()
                data = response.json()

                if coin_id in data.get("coins", {}):
                    price = Decimal(str(data["coins"][coin_id]["price"]))
                    self._set_cached(cache_key, price)
                    return price
                return None
            except Exception as e:
                print(f"DeFiLlama error for {coin_id}: {e}")
                return None

    async def get_price(
        self,
        coingecko_id: Optional[str] = None,
        chain: Optional[str] = None,
        contract: Optional[str] = None,
    ) -> Optional[Decimal]:
        """Get price, preferring CoinGecko over DeFiLlama."""
        # Try CoinGecko first
        if coingecko_id:
            price = await self.get_price_coingecko(coingecko_id)
            if price is not None:
                return price

        # Fall back to DeFiLlama
        if chain and contract:
            return await self.get_price_defillama(chain, contract)

        return None

    async def get_prices_batch(self, coingecko_ids: List[str]) -> Dict[str, Decimal]:
        """Batch fetch prices from CoinGecko."""
        if not coingecko_ids:
            return {}

        # Check cache first
        result = {}
        uncached_ids = []
        for cg_id in coingecko_ids:
            cached = self._get_cached(f"cg_{cg_id}")
            if cached is not None:
                result[cg_id] = cached
            else:
                uncached_ids.append(cg_id)

        if not uncached_ids:
            return result

        # Fetch uncached prices
        ids_str = ",".join(uncached_ids)
        async with httpx.AsyncClient() as client:
            try:
                headers = {}
                if settings.coingecko_api_key:
                    headers["x-cg-demo-api-key"] = settings.coingecko_api_key

                response = await client.get(
                    f"{self.coingecko_base}/simple/price",
                    params={"ids": ids_str, "vs_currencies": "usd"},
                    headers=headers,
                    timeout=15,
                )
                response.raise_for_status()
                data = response.json()

                for cg_id, info in data.items():
                    if "usd" in info:
                        price = Decimal(str(info["usd"]))
                        self._set_cached(f"cg_{cg_id}", price)
                        result[cg_id] = price

                return result
            except Exception as e:
                print(f"Batch price error: {e}")
                return result


class TVLService:
    """TVL data service with DeFiLlama integration."""

    def __init__(self):
        self.base_url = settings.defillama_base_url

    async def get_protocol_tvl(self, protocol_slug: str) -> Optional[float]:
        """Get protocol TVL from DeFiLlama."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/tvl/{protocol_slug}",
                    timeout=10,
                )
                response.raise_for_status()
                # Returns a number directly
                return response.json()
            except Exception as e:
                print(f"TVL error for {protocol_slug}: {e}")
                return None

    async def get_protocol_details(self, protocol_slug: str) -> Optional[Dict]:
        """Get detailed protocol information from DeFiLlama."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/protocol/{protocol_slug}",
                    timeout=10,
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                print(f"Protocol details error for {protocol_slug}: {e}")
                return None
