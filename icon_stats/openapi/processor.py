from typing import List, Dict, Any
from urllib.parse import urlparse

import requests
from openapi_pydantic import OpenAPI, Info, PathItem, Tag
from pydantic import BaseModel

from icon_stats.log import logger
from .operations import FetchSchema, ResolveRefs, ValidateParams
from ..config import config

IGNORED_PATHS = [
    "/health",
    "/ready",
    "/metadata",
    "/version",
]

SWAGGER_CONVERT = "https://converter.swagger.io/api/convert"


class OpenAPIProcessor(BaseModel):
    fetch_schema: FetchSchema
    resolve_schema_refs: ResolveRefs
    validate_params: ValidateParams

    def get_tag_from_url(self, url: str) -> str:
        """Extract tag name from the URL domain."""
        domain = urlparse(url).netloc
        if domain.startswith("balanced."):
            return "balanced"
        return "icon"  # default tag

    def process(self, schema_urls: List[str], title: str) -> OpenAPI:
        output = OpenAPI(
            info=Info(
                title=title,
                version="v0.0.1",
            ),
            servers=[
                {"url": config.COMMUNITY_API_ENDPOINT},
                {"url": config.LISBON_COMMUNITY_API_ENDPOINT},
                {"url": config.BERLIN_COMMUNITY_API_ENDPOINT},
                {"url": config.BALANCED_API_ENDPOINT},
            ],
            paths={},
            tags=[
                Tag(name="icon", description="ICON Network API endpoints"),
                Tag(name="balanced", description="Balanced API endpoints"),
            ],
        )

        for url in schema_urls:
            base_url = url.rsplit("/", 1)[0]
            openapi_json = self.fetch_schema.execute(url)
            tag_name = self.get_tag_from_url(url)

            if openapi_json is None:
                logger.info(f"Empty schema returned for URL: {url}")
                continue

            openapi_json = check_openapi_version_and_convert(schema_json=openapi_json)
            openapi_json = self.resolve_schema_refs.execute(
                openapi_json=openapi_json, base_url=base_url
            )
            openapi_json = self.validate_params.execute(openapi_json=openapi_json)

            for path_name, operations in openapi_json["paths"].items():
                if path_name in IGNORED_PATHS:
                    continue
                if path_name in output.paths:
                    logger.error(
                        f"Overlapping paths not supported (TODO) - {path_name}"
                    )
                    continue

                # Add tags to each operation in the path
                for operation in operations.values():
                    if isinstance(
                        operation, dict
                    ):  # Ensure it's a dict before modifying
                        if "tags" not in operation:
                            operation["tags"] = []
                        if tag_name not in operation["tags"]:
                            operation["tags"].append(tag_name)

                output.paths[path_name] = PathItem(**operations)

        return output


def check_openapi_version_and_convert(schema_json: Dict[str, Any]) -> Dict:
    version = schema_json.get("openapi") or schema_json.get("swagger")
    if not version:
        logger.error("The schema does not have a valid OpenAPI or Swagger version.")
        return {}

    major_version = int(version.split(".")[0])
    if major_version < 3:
        print(f"Converting OpenAPI version {version} to OpenAPI 3.x.x")

        response = requests.post(url=SWAGGER_CONVERT, json=schema_json)
        if response.status_code == 200:
            return response.json()

    else:
        return schema_json
