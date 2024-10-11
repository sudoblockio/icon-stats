import time
from typing import Any, Dict, Optional

import requests
from pydantic import BaseModel

from icon_stats.log import logger


class OpenAPIOperation(BaseModel):
    def execute(self, *args, **kwargs) -> Any:
        pass


class FetchSchema(OpenAPIOperation):
    def execute(self, url: str) -> Optional[Dict[str, Any]]:
        max_retries = 10  # Predefined maximum number of retries
        retry_delay = 2  # Delay between retries in seconds
        retries = 0

        while retries < max_retries:
            try:
                response = requests.get(
                    url=url,
                    headers={
                        "User-Agent": "ICONStats/v1 (+https://tracker.icon.community)"
                    },
                )

                # If successful, return the response data
                if response.status_code == 200:
                    return response.json()

                logger.error(f"Failed: status code: {response.status_code} for URL: {url} response : {response.json()}")
                return None

            except Exception as e:
                # Only retry on exceptions
                retries += 1
                if retries < max_retries:
                    logger.warning(f"Retrying {retries}/{max_retries} after error: {e}")
                    time.sleep(retry_delay)
                else:
                    logger.error(f"Max retries exceeded for URL: {url}. Last error: {e}")
                    return None

class ResolveRefs(OpenAPIOperation):
    def execute(self, openapi_json: Dict[str, Any], base_url: str) -> Optional[Dict[str, Any]]:
        def _resolve(obj, url):
            if isinstance(obj, dict):
                if "$ref" in obj:
                    ref_path = obj["$ref"]
                    if not ref_path.startswith("#"):
                        # external reference
                        ref_url = f"{url}/{ref_path}"
                        ref_response = requests.get(ref_url)
                        if ref_response.status_code == 200:
                            ref_obj = ref_response.json()
                        else:
                            logger.error(f"Reference URL not found: {ref_url}")
                            return None
                        return _resolve(ref_obj, url)
                    else:
                        # internal reference
                        ref_path = ref_path.lstrip("#/")
                        ref_parts = ref_path.split("/")
                        ref_obj = openapi_json
                        for part in ref_parts:
                            ref_obj = ref_obj.get(part)
                            if ref_obj is None:
                                logger.error(f"Reference path not found: {ref_path}")
                                return None
                        return _resolve(ref_obj, url)
                else:
                    for key, value in obj.items():
                        resolved_value = _resolve(value, url)
                        if resolved_value is None:
                            return None
                        obj[key] = resolved_value
            elif isinstance(obj, list):
                resolved_list = [_resolve(item, url) for item in obj]
                if None in resolved_list:
                    return None
                return resolved_list
            return obj

        return _resolve(openapi_json, base_url)


class ValidateParams(OpenAPIOperation):
    def execute(self, openapi_json: Dict[str, Any]) -> Dict[str, Any]:
        def _validate(obj):
            if isinstance(obj, dict):
                if "parameters" in obj:
                    for param in obj["parameters"]:
                        if "content" not in param and "schema" not in param:
                            param["schema"] = {"type": "string"}  # Default schema type
                for key, value in obj.items():
                    _validate(value)
            elif isinstance(obj, list):
                for item in obj:
                    _validate(item)

        _validate(openapi_json)
        return openapi_json
