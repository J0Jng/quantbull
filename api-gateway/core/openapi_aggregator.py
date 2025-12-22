"""
OpenAPI 聚合模块

负责从各个微服务拉取 OpenAPI 文档并合并成统一的文档。
"""
import asyncio
import json
import logging
from copy import deepcopy
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin

import httpx
from fastapi import HTTPException

logger = logging.getLogger(__name__)


class OpenAPIAggregator:
    """OpenAPI 文档聚合器"""

    def __init__(self, services_config: List[Dict], timeout: float = 30.0):
        """
        初始化聚合器

        Args:
            services_config: 服务配置列表
            timeout: 请求超时时间
        """
        self.services_config = services_config
        self.timeout = timeout
        self._merged_spec: Optional[Dict] = None

    async def fetch_service_openapi(self, service: Dict) -> Optional[Dict]:
        """异步拉取单个服务的 OpenAPI 文档"""
        name = service["name"]
        url = service["url"]
        enabled = service.get("enabled", True)

        if not enabled:
            logger.info(f"Service {name} is disabled, skipping")
            return None

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                spec = response.json()
                logger.info(f"Successfully fetched OpenAPI from {name}")
                return spec
        except Exception as e:
            logger.warning(f"Failed to fetch OpenAPI from {name} ({url}): {e}")
            return None

    def _namespace_schema_refs(self, obj: Any, service_name: str) -> Any:
        """递归重命名 schema 引用"""
        if isinstance(obj, dict):
            new_obj = {}
            for k, v in obj.items():
                if k == "$ref" and isinstance(v, str) and v.startswith("#/components/schemas/"):
                    # 重命名 schema 引用
                    schema_name = v.split("/")[-1]
                    new_ref = f"#/components/schemas/{service_name}_{schema_name}"
                    new_obj[k] = new_ref
                else:
                    new_obj[k] = self._namespace_schema_refs(v, service_name)
            return new_obj
        elif isinstance(obj, list):
            return [self._namespace_schema_refs(item, service_name) for item in obj]
        else:
            return obj

    def _merge_paths(self, merged_paths: Dict, service_spec: Dict, service: Dict) -> None:
        """合并路径"""
        service_name = service["name"]
        path_prefix = service["path_prefix"]

        for path, path_item in service_spec.get("paths", {}).items():
            # 添加路径前缀
            prefixed_path = urljoin(path_prefix + "/", path.lstrip("/"))

            # 重命名 schema 引用
            namespaced_path_item = self._namespace_schema_refs(path_item, service_name)

            # 添加服务标签
            for method, operation in namespaced_path_item.items():
                if isinstance(operation, dict):
                    tags = operation.get("tags", [])
                    if service_name not in tags:
                        operation["tags"] = [service_name] + tags

            # 合并到主文档
            if prefixed_path in merged_paths:
                logger.warning(f"Path collision: {prefixed_path}, merging operations")
                merged_paths[prefixed_path].update(namespaced_path_item)
            else:
                merged_paths[prefixed_path] = namespaced_path_item

    def _merge_components(self, merged_components: Dict, service_spec: Dict, service_name: str) -> None:
        """合并组件"""
        service_components = service_spec.get("components", {})

        # 合并 schemas（重命名）
        if "schemas" in service_components:
            for schema_name, schema_def in service_components["schemas"].items():
                namespaced_name = f"{service_name}_{schema_name}"
                namespaced_schema = self._namespace_schema_refs(schema_def, service_name)
                merged_components.setdefault("schemas", {})[namespaced_name] = namespaced_schema

        # 合并 securitySchemes
        if "securitySchemes" in service_components:
            merged_components.setdefault("securitySchemes", {}).update(service_components["securitySchemes"])

    def _merge_tags(self, merged_tags: List, service_spec: Dict, service_name: str) -> None:
        """合并标签"""
        service_tags = service_spec.get("tags", [])
        for tag in service_tags:
            if not any(t.get("name") == tag.get("name") for t in merged_tags):
                merged_tags.append(tag)

        # 确保服务标签存在
        if not any(t.get("name") == service_name for t in merged_tags):
            merged_tags.append({
                "name": service_name,
                "description": f"APIs from {service_name}"
            })

    async def aggregate(self) -> Dict:
        """执行聚合"""
        if self._merged_spec is not None:
            return self._merged_spec

        logger.info("Starting OpenAPI aggregation...")

        # 基础文档结构
        merged_spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "QuantBull Unified API",
                "version": "1.0.0",
                "description": "Unified API documentation for all QuantBull microservices"
            },
            "paths": {},
            "components": {
                "schemas": {},
                "securitySchemes": {
                    "OAuth2PasswordBearer": {
                        "type": "oauth2",
                        "flows": {
                            "password": {
                                "tokenUrl": "/auth/token",
                                "scopes": {}
                            }
                        }
                    }
                }
            },
            "tags": [],
            "security": [
                {"OAuth2PasswordBearer": []}
            ]
        }

        # 并发拉取所有服务的 OpenAPI
        tasks = [self.fetch_service_openapi(service) for service in self.services_config]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 处理结果
        for service, result in zip(self.services_config, results):
            if isinstance(result, Exception):
                logger.error(f"Exception while fetching {service['name']}: {result}")
                continue
            elif result is None:
                continue

            service_spec = result
            service_name = service["name"]

            # 合并各个部分
            self._merge_paths(merged_spec["paths"], service_spec, service)
            self._merge_components(merged_spec["components"], service_spec, service_name)
            self._merge_tags(merged_spec["tags"], service_spec, service_name)

        logger.info("OpenAPI aggregation completed")
        self._merged_spec = merged_spec
        return merged_spec

    def get_aggregated_openapi(self) -> Optional[Dict]:
        """获取已聚合的文档（同步方法，用于 FastAPI 的 openapi 生成器）"""
        if self._merged_spec is None:
            # 如果还没有聚合，尝试同步聚合（仅用于开发环境）
            logger.warning("OpenAPI not yet aggregated, this should not happen in production")
            return None
        return self._merged_spec