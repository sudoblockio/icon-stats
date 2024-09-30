from typing import Any, Dict
import requests
from pydantic import BaseModel


class OpenAPIOperation(BaseModel):
    def execute(self, *args, **kwargs) -> Any:
        pass


class FetchSchema(OpenAPIOperation):
    def execute(self, url: str) -> Dict[str, Any]:
        response = requests.get(url=url)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(
                f"Failed to Fetch URL : {url} with status code {response.status_code}")


class ResolveRefs(OpenAPIOperation):
    def execute(self, openapi_json: Dict[str, Any], base_url: str) -> Dict[str, Any]:
        def _resolve(obj, url):
            if isinstance(obj, dict):
                if '$ref' in obj:
                    ref_path = obj['$ref']
                    if not ref_path.startswith('#'):
                        # external reference
                        ref_url = f"{url}/{ref_path}"
                        ref_response = requests.get(ref_url)
                        if ref_response.status_code == 200:
                            ref_obj = ref_response.json()
                        else:
                            raise Exception(f"Reference url={ref_url} not found.")
                        return _resolve(ref_obj, url)
                    else:
                        # internal reference
                        ref_path = ref_path.lstrip('#/')
                        ref_parts = ref_path.split('/')
                        ref_obj = openapi_json
                        for part in ref_parts:
                            ref_obj = ref_obj.get(part)
                            if ref_obj is None:
                                raise KeyError(f"Reference path not found: {ref_path}")
                        return _resolve(ref_obj, url)
                else:
                    for key, value in obj.items():
                        obj[key] = _resolve(value, url)
            elif isinstance(obj, list):
                return [_resolve(item, url) for item in obj]
            return obj

        return _resolve(openapi_json, base_url)


class ValidateParams(OpenAPIOperation):
    def execute(self, openapi_json: Dict[str, Any]) -> Dict[str, Any]:
        def _validate(obj):
            if isinstance(obj, dict):
                if 'parameters' in obj:
                    for param in obj['parameters']:
                        if 'content' not in param and 'schema' not in param:
                            param['schema'] = {"type": "string"}  # Default schema type
                for key, value in obj.items():
                    _validate(value)
            elif isinstance(obj, list):
                for item in obj:
                    _validate(item)

        _validate(openapi_json)
        return openapi_json
