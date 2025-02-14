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
        mock_get.assert_called_once_with(
            url="http://example.com/schema.json",
            headers={"User-Agent": "ICONStats/v1 (+https://tracker.icon.community)"},
        )


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
        "https://balanced.icon.community/api/v1/docs/openapi.json",
    ]
    schema_json_openapi = get_merged_openapi(schema_urls, title="Icon")

    with open("icon-out.json", "w") as f:
        json.dump(schema_json_openapi, f, indent=2)


def create_mock_processor():
    """Helper function to create a processor with mocked dependencies"""
    return OpenAPIProcessor(
        fetch_schema=Mock(spec=FetchSchema),
        resolve_schema_refs=Mock(spec=ResolveRefs),
        validate_params=Mock(spec=ValidateParams),
    )


def test_url_tag_extraction():
    processor = create_mock_processor()

    # Test balanced URL
    balanced_url = "https://balanced.icon.community/api/v1/docs/openapi.json"
    assert processor.get_tag_from_url(balanced_url) == "balanced"

    # Test icon URL
    icon_url = "https://tracker.icon.community/api/v1/docs/openapi.json"
    assert processor.get_tag_from_url(icon_url) == "icon"


def test_schema_processing():
    processor = create_mock_processor()

    balanced_schema = {
        "openapi": "3.0.0",
        "paths": {
            "/api/v1/pool": {
                "get": {"operationId": "getPool", "description": "Get pool info"}
            }
        },
    }

    icon_schema = {
        "openapi": "3.0.0",
        "paths": {
            "/api/v1/blocks": {
                "get": {"operationId": "getBlocks", "description": "Get blocks"}
            }
        },
    }

    processor.fetch_schema.execute.side_effect = [balanced_schema, icon_schema]
    processor.resolve_schema_refs.execute.side_effect = (
        lambda openapi_json, base_url: openapi_json
    )
    processor.validate_params.execute.side_effect = lambda openapi_json: openapi_json

    urls = [
        "https://balanced.icon.community/api/v1/docs/openapi.json",
        "https://tracker.icon.community/api/v1/docs/openapi.json",
    ]

    result = processor.process(urls, "Test API")

    # Test tag definitions
    tag_names = [tag.name for tag in result.tags]
    assert "balanced" in tag_names
    assert "icon" in tag_names

    # Test path tags
    assert "balanced" in result.paths["/api/v1/pool"].get.tags
    assert "icon" in result.paths["/api/v1/blocks"].get.tags


def test_empty_schema_handling():
    processor = create_mock_processor()

    processor.fetch_schema.execute.return_value = None

    urls = ["https://balanced.icon.community/api/v1/docs/openapi.json"]
    result = processor.process(urls, "Test API")

    assert result.paths == {}
    assert len(result.tags) == 2
