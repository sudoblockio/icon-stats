from typing import List, Dict, Any

import requests
from pydantic import BaseModel
from openapi_pydantic import OpenAPI, Info, PathItem
from .operations import FetchSchema, ResolveRefs, ValidateParams

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

    def process(self, schema_urls: List[str], title: str) -> OpenAPI:
        output = OpenAPI(
            info=Info(
                title=title,
                version="v0.0.1",
            ),
            paths={},
        )

        for url in schema_urls:
            base_url = url.rsplit('/', 1)[0]
            openapi_json = self.fetch_schema.execute(url)
            openapi_json = check_openapi_version_and_convert(schema_json=openapi_json)
            openapi_json = self.resolve_schema_refs.execute(
                openapi_json=openapi_json, base_url=base_url
            )
            openapi_json = self.validate_params.execute(openapi_json=openapi_json)

            for path_name, operations in openapi_json['paths'].items():
                if path_name in IGNORED_PATHS:
                    continue
                if path_name in output.paths:
                    raise Exception(
                        f"Overlapping paths not supported (TODO) - {path_name}")
                output.paths[path_name] = PathItem(**operations)

        return output


def check_openapi_version_and_convert(schema_json: Dict[str, Any]) -> Dict:
    version = schema_json.get('openapi') or schema_json.get('swagger')
    if not version:
        raise ValueError("The schema does not have a valid OpenAPI or Swagger version.")

    major_version = int(version.split('.')[0])
    if major_version < 3:
        print(f"Converting OpenAPI version {version} to OpenAPI 3.x.x")

        response = requests.post(url=SWAGGER_CONVERT, json=schema_json)
        if response.status_code == 200:
            return response.json()

    else:
        return schema_json