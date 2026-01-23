"""OpenAPI aggregation utilities."""

import asyncio
import logging
import os
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
import time
import yaml
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel, ValidationError, field_validator

logger = logging.getLogger(__name__)

# Paths that are intentionally owned by the gateway and commonly appear in downstream specs.
# We suppress collision warnings for these to reduce noise.
COLLISION_IGNORE_PATHS = {
    "/",
    "/health",
    "/api/auth/login",
    "/api/auth/login/json",
    "/api/auth/verify",
    "/api/auth/register",
    "/api/admin/users",
    "/api/admin/users/{user_id}",
    "/api/admin/users/{user_id}/ai-tokens",
}


def _resolve_env(value: Any) -> Any:
    if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
        key = value[2:-1]
        return os.getenv(key, value)
    return value


class ServiceConfig(BaseModel):
    name: str
    display_name: str
    url: str
    prefix: str
    openapi_path: str = "/openapi.json"
    enabled: bool = True
    timeout: float = 5.0

    @field_validator("prefix")
    @classmethod
    def normalize_prefix(cls, value: str) -> str:
        prefix = value or ""
        if not prefix.startswith("/"):
            prefix = f"/{prefix}"
        return prefix.rstrip("/") or "/"

    @property
    def openapi_url(self) -> str:
        base = self.url.rstrip("/")
        path = self.openapi_path.lstrip("/")
        return f"{base}/{path}"


def load_service_configs(config_path: Path) -> List[ServiceConfig]:
    if not config_path.exists():
        logger.warning("Service config file not found: %s", config_path)
        return []

    try:
        raw = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        logger.warning("Failed to read service config %s: %s", config_path, exc)
        return []

    services_raw = raw.get("services") if isinstance(raw, dict) else raw
    if not isinstance(services_raw, list):
        logger.warning("Service config format invalid, expected list under 'services'")
        return []

    configs: List[ServiceConfig] = []
    for entry in services_raw:
        if not isinstance(entry, dict):
            continue
        resolved = {key: _resolve_env(val) for key, val in entry.items()}
        try:
            configs.append(ServiceConfig(**resolved))
        except ValidationError as exc:
            logger.warning("Invalid service config for %s: %s", entry.get("name", "unknown"), exc)

    return configs


class OpenAPIAggregator:
    def __init__(self, app: FastAPI, services: List[ServiceConfig]):
        self.app = app
        self.services = services
        self._merged_spec: Optional[Dict[str, Any]] = None

        # Retry settings for pulling downstream OpenAPI docs to handle slow starts
        self._fetch_retries = 3
        self._fetch_backoff = 1.0  # seconds

    async def aggregate(self) -> Dict[str, Any]:
        base_spec = self._build_base_spec()

        async with httpx.AsyncClient() as client:
            specs = await asyncio.gather(
                *[self._fetch_service_openapi(client, svc) for svc in self.services],
                return_exceptions=True,
            )

        for svc, spec in zip(self.services, specs):
            if isinstance(spec, BaseException):
                logger.warning("OpenAPI fetch for %s raised: %s", svc.name, spec)
                continue
            if not spec:
                continue
            self._merge_service_spec(base_spec, spec, svc)

        self._merged_spec = base_spec
        return base_spec

    def get_aggregated_openapi(self) -> Optional[Dict[str, Any]]:
        return self._merged_spec

    async def _fetch_service_openapi(self, client: httpx.AsyncClient, svc: ServiceConfig) -> Optional[Dict[str, Any]]:
        if not svc.enabled:
            logger.info("Service %s disabled, skip OpenAPI pull", svc.name)
            return None

        for attempt in range(1, self._fetch_retries + 1):
            try:
                response = await client.get(svc.openapi_url, timeout=svc.timeout)
                response.raise_for_status()
                logger.info("Fetched OpenAPI from %s", svc.name)
                return response.json()
            except Exception as exc:
                logger.warning(
                    "Failed to fetch OpenAPI from %s (%s) (attempt %s/%s): %s",
                    svc.name,
                    svc.openapi_url,
                    attempt,
                    self._fetch_retries,
                    exc,
                )
                if attempt < self._fetch_retries:
                    time.sleep(self._fetch_backoff * attempt)
                else:
                    return None

    def _build_base_spec(self) -> Dict[str, Any]:
        spec = get_openapi(
            title=self.app.title or "API Gateway",
            version=self.app.version or "1.0.0",
            description=self.app.description or "QuantBull API Gateway",
            routes=self.app.routes,
        )

        components = spec.setdefault("components", {})
        components.setdefault("schemas", {})
        security_schemes = components.setdefault("securitySchemes", {})
        security_schemes.setdefault(
            "OAuth2PasswordBearer",
            {
                "type": "oauth2",
                "flows": {"password": {"tokenUrl": "/api/auth/login", "scopes": {}}},
            },
        )
        spec.setdefault("security", [{"OAuth2PasswordBearer": []}])
        spec.setdefault("tags", [])
        spec.setdefault("paths", {})
        return spec

    def _merge_service_spec(self, base_spec: Dict[str, Any], service_spec: Dict[str, Any], svc: ServiceConfig) -> None:
        self._merge_tags(base_spec["tags"], svc)
        self._merge_paths(base_spec["paths"], service_spec, svc)
        self._merge_components(base_spec["components"], service_spec, svc)

    def _merge_tags(self, merged_tags: List[Dict[str, Any]], svc: ServiceConfig) -> None:
        if not any(tag.get("name") == svc.display_name for tag in merged_tags):
            merged_tags.append({"name": svc.display_name, "description": f"{svc.display_name} APIs"})

    def _merge_paths(self, merged_paths: Dict[str, Any], service_spec: Dict[str, Any], svc: ServiceConfig) -> None:
        for path, path_item in service_spec.get("paths", {}).items():
            prefixed_path = self._apply_prefix(path, svc.prefix)
            if prefixed_path in merged_paths:
                if prefixed_path not in COLLISION_IGNORE_PATHS:
                    logger.warning("Path collision detected, keeping gateway definition: %s", prefixed_path)
                continue

            namespaced_path_item = self._namespace_schema_refs(deepcopy(path_item), svc.name)
            for _, operation in namespaced_path_item.items():
                if isinstance(operation, dict):
                    operation["tags"] = [svc.display_name]

            merged_paths[prefixed_path] = namespaced_path_item

    def _merge_components(self, merged_components: Dict[str, Any], service_spec: Dict[str, Any], svc: ServiceConfig) -> None:
        service_components = service_spec.get("components", {})

        schemas = service_components.get("schemas", {}) or {}
        for schema_name, schema_def in schemas.items():
            namespaced_name = f"{svc.name}_{schema_name}"
            merged_components.setdefault("schemas", {})[namespaced_name] = self._namespace_schema_refs(
                deepcopy(schema_def), svc.name
            )

        security_schemes = service_components.get("securitySchemes", {}) or {}
        for scheme_name, scheme_def in security_schemes.items():
            merged_components.setdefault("securitySchemes", {}).setdefault(scheme_name, scheme_def)

    def _namespace_schema_refs(self, obj: Any, service_name: str) -> Any:
        if isinstance(obj, dict):
            new_obj = {}
            for key, val in obj.items():
                if key == "$ref" and isinstance(val, str) and val.startswith("#/components/schemas/"):
                    schema_name = val.split("/")[-1]
                    new_obj[key] = f"#/components/schemas/{service_name}_{schema_name}"
                else:
                    new_obj[key] = self._namespace_schema_refs(val, service_name)
            return new_obj
        if isinstance(obj, list):
            return [self._namespace_schema_refs(item, service_name) for item in obj]
        return obj

    @staticmethod
    def _apply_prefix(path: str, prefix: str) -> str:
        normalized = f"{prefix.rstrip('/')}/{path.lstrip('/')}"
        return "/" + normalized.lstrip("/")