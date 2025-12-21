#!/usr/bin/env python3
"""
merge_openapi.py

Fetch OpenAPI JSON from multiple services, namespace components, prefix paths,
optionally wrap responses into a unified ApiResponse envelope, and write unified file.

Usage:
    python tools/merge_openapi.py --services services.json --out unified-openapi.json --prefix-paths

services.json format:
[
  {"name": "data-service", "url": "http://data-service:8001/openapi.json"},
  {"name": "ai-hub", "url": "http://ai-hub:8002/openapi.json"}
]

This script is deterministic and avoids component name collisions by prefixing component
names with the service name and rewriting $ref references accordingly.
"""
import argparse
import json
import re
from copy import deepcopy
from typing import List, Dict

import requests


COMPONENT_KINDS = [
    "schemas",
    "responses",
    "parameters",
    "examples",
    "requestBodies",
    "headers",
    "securitySchemes",
    "links",
    "callbacks",
]


REF_RE = re.compile(r"#\/components\/([^\/]+)\/([^\"]+)")


def fetch_openapi(url: str) -> Dict:
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.json()


def ns_ref(match, svc_name: str):
    kind, name = match.group(1), match.group(2)
    return f"#/components/{kind}/{svc_name}_{name}"


def rewrite_refs(obj, svc_name: str):
    """Recursively rewrite $ref strings in a JSON-like dict/list."""
    if isinstance(obj, dict):
        new = {}
        for k, v in obj.items():
            if k == "$ref" and isinstance(v, str):
                new[k] = REF_RE.sub(lambda m: ns_ref(m, svc_name), v)
            else:
                new[k] = rewrite_refs(v, svc_name)
        return new
    elif isinstance(obj, list):
        return [rewrite_refs(i, svc_name) for i in obj]
    else:
        return obj


def namespace_components(spec: Dict, svc_name: str, merged_components: Dict):
    for kind in COMPONENT_KINDS:
        items = spec.get("components", {}).get(kind, {})
        for name, val in items.items():
            new_name = f"{svc_name}_{name}"
            # rewrite internal refs within component
            merged_components.setdefault(kind, {})[new_name] = rewrite_refs(val, svc_name)


def merge_services(services: List[Dict], prefix_paths: bool = True, wrap_responses: bool = True) -> Dict:
    merged = {
        "openapi": "3.0.0",
        "info": {"title": "Unified API", "version": "1.0.0"},
        "paths": {},
        "components": {"schemas": {}},
        "tags": [],
    }

    merged_components = {}

    for svc in services:
        name = svc["name"]
        url = svc["url"]
        print(f"Fetching {name} -> {url}")
        spec = fetch_openapi(url)

        # namespace components and add to merged_components
        namespace_components(spec, name, merged_components)

        # rewrite refs in full spec
        spec = rewrite_refs(spec, name)

        # merge tags: ensure tag for this service exists
        svc_tag = {"name": name, "description": f"APIs from {name}"}
        merged["tags"].append(svc_tag)

        # merge paths, optionally prefix path with service name to avoid collisions
        for path, path_item in spec.get("paths", {}).items():
            new_path = f"/{name}{path}" if prefix_paths else path
            # attach service tag to operations if not present
            for op, op_obj in path_item.items():
                if isinstance(op_obj, dict):
                    tags = op_obj.get("tags", [])
                    if name not in tags:
                        tags = [name] + tags
                    op_obj["tags"] = tags
                    # optionally wrap response schema for 200/201
                    if wrap_responses:
                        for status in list(op_obj.get("responses", {}).keys()):
                            resp = op_obj["responses"][status]
                            content = resp.get("content", {})
                            app_json = content.get("application/json")
                            if app_json and "schema" in app_json:
                                original_schema = app_json["schema"]
                                # create an inlined combined schema using allOf
                                wrapped = {
                                    "allOf": [
                                        {"$ref": "#/components/schemas/ApiResponse"},
                                        {"properties": {"data": original_schema}},
                                    ]
                                }
                                app_json["schema"] = wrapped
                                resp["content"]["application/json"] = app_json
                                op_obj["responses"][status] = resp

            if new_path in merged["paths"]:
                print(f"Warning: path collision {new_path}; merging operations")
                merged["paths"][new_path].update(path_item)
            else:
                merged["paths"][new_path] = path_item

    # assemble merged components
    merged["components"] = merged_components

    # ensure ApiResponse component exists
    if "schemas" not in merged["components"]:
        merged["components"]["schemas"] = {}
    merged["components"]["schemas"]["ApiResponse"] = {
        "type": "object",
        "properties": {
            "code": {"type": "integer", "example": 0},
            "message": {"type": "string", "example": "ok"},
            "data": {"type": "object"},
        },
        "required": ["code", "message", "data"],
    }

    return merged


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--services", required=True, help="JSON file listing services with name and url")
    parser.add_argument("--out", required=True, help="Output unified openapi json file")
    parser.add_argument("--prefix-paths", action="store_true", help="Prefix paths with service name to avoid collisions")
    parser.add_argument("--no-wrap-responses", dest="wrap_responses", action="store_false", help="Do not wrap responses into ApiResponse envelope")
    args = parser.parse_args()

    with open(args.services, "r", encoding="utf-8") as f:
        services = json.load(f)

    merged = merge_services(services, prefix_paths=args.prefix_paths, wrap_responses=args.wrap_responses)

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    print(f"Wrote unified OpenAPI to {args.out}")


if __name__ == "__main__":
    main()
