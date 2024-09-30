import pytest
import json

from unittest.mock import patch, Mock

from icon_stats.api.v1.endpoints.openapi import get_merged_openapi
from icon_stats.openapi.operations import FetchSchema, ResolveRefs, ValidateParams
from icon_stats.openapi.processor import OpenAPIProcessor


def test_fetch_schema():
    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"openapi": "3.0.0"}

        fetch_schema = FetchSchema()
        result = fetch_schema.execute("http://example.com/schema.json")

        assert result == {"openapi": "3.0.0"}
        mock_get.assert_called_once_with(url="http://example.com/schema.json")


def test_fetch_schema_error():
    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 404

        fetch_schema = FetchSchema()
        with pytest.raises(Exception, match="Failed to Fetch URL"):
            fetch_schema.execute("http://example.com/schema.json")


def test_resolve_refs():
    mock_schema = {
        "components": {"schemas": {"Test": {"type": "object"}}},
        "paths": {
            "/test": {
                "get": {
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Test"}
                                }
                            }
                        }
                    }
                }
            }
        },
    }

    resolve_refs = ResolveRefs()
    result = resolve_refs.execute(mock_schema, "http://example.com")

    assert result["paths"]["/test"]["get"]["responses"]["200"]["content"][
        "application/json"
    ]["schema"] == {"type": "object"}


def test_validate_params():
    mock_schema = {
        "paths": {"/test": {"get": {"parameters": [{"name": "param", "in": "query"}]}}}
    }

    validate_params = ValidateParams()
    result = validate_params.execute(mock_schema)

    assert result["paths"]["/test"]["get"]["parameters"][0]["schema"] == {
        "type": "string"
    }


def test_openapi_processor():
    with patch("requests.get") as mock_get, patch("requests.post") as mock_post:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "openapi": "3.0.0",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {
                "/test": {
                    "get": {
                        "summary": "Test endpoint",
                        "responses": {"200": {"description": "Successful response"}},
                    }
                }
            },
        }

        processor = OpenAPIProcessor(
            fetch_schema=FetchSchema(),
            resolve_schema_refs=ResolveRefs(),
            validate_params=ValidateParams(),
        )

        result = processor.process(["http://example.com/schema.json"], "Combined API")

        assert result.info.title == "Combined API"
        assert "/test" in result.paths
        assert result.paths["/test"].get.summary == "Test endpoint"


def test_generate_output():
    schema_urls = [
        "https://tracker.icon.community/api/v1/governance/docs/openapi.json",
        "https://tracker.icon.community/api/v1/contracts/docs/openapi.json",
        "https://tracker.icon.community/api/v1/statistics/docs/openapi.json",
        "https://tracker.icon.community/api/v1/docs/doc.json",
    ]
    schema_json_openapi = get_merged_openapi(schema_urls, title="Icon")

    with open("icon-out.json", "w") as f:
        json.dump(schema_json_openapi, f, indent=2)
