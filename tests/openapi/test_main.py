import os
import pytest
import json

from unittest.mock import patch, Mock

from apisix.openapi_merger.main import main
from apisix.openapi_merger.operations.operations import FetchSchema, ResolveRefs, ValidateParams
from apisix.openapi_merger.operations.processor import OpenAPIProcessor

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")

FIXTURES = [
    "single_schema",
    "multiple_schemas",
]


@pytest.fixture()
def generate_input_url_fixture():
    return lambda fixture_name: f"http://example.com/{fixture_name}.json"


@pytest.fixture()
def cleanup_generated_files():
    yield
    for file in os.listdir(FIXTURES_DIR):
        if file.endswith(".json"):
            os.remove(os.path.join(FIXTURES_DIR, file))


@pytest.fixture()
def mock_requests_get():
    with patch('requests.get') as mock_get:
        yield mock_get


@pytest.fixture()
def mock_requests_post():
    with patch('requests.post') as mock_post:
        yield mock_post


@pytest.mark.parametrize("fixture_name", FIXTURES)
def test_main(fixture_name, generate_input_url_fixture, cleanup_generated_files, mock_requests_get, mock_requests_post):
    input_url = generate_input_url_fixture(fixture_name)
    output_file = os.path.join(FIXTURES_DIR, f"{fixture_name}_output.json")

    mock_requests_get.return_value.status_code = 200
    mock_requests_get.return_value.json.return_value = {
        "openapi": "3.0.0",
        "info": {"title": "Test API", "version": "1.0.0"},
        "paths": {
            "/test": {
                "get": {
                    "summary": "Test endpoint",
                    "responses": {"200": {"description": "Successful response"}}
                }
            }
        }
    }

    mock_requests_post.return_value.status_code = 200
    mock_requests_post.return_value.json.return_value = {"swagger": "2.0"}

    main([input_url], f"Test {fixture_name}", output_file)

    assert os.path.exists(output_file)
    with open(output_file, 'r') as f:
        content = json.load(f)
        assert content == {"swagger": "2.0"}


def test_fetch_schema():
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"openapi": "3.0.0"}

        fetch_schema = FetchSchema()
        result = fetch_schema.execute("http://example.com/schema.json")

        assert result == {"openapi": "3.0.0"}
        mock_get.assert_called_once_with(url="http://example.com/schema.json")


def test_fetch_schema_error():
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 404

        fetch_schema = FetchSchema()
        with pytest.raises(Exception, match="Failed to Fetch URL"):
            fetch_schema.execute("http://example.com/schema.json")


def test_resolve_refs():
    mock_schema = {
        "components": {
            "schemas": {
                "Test": {"type": "object"}
            }
        },
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
        }
    }

    resolve_refs = ResolveRefs()
    result = resolve_refs.execute(mock_schema, "http://example.com")

    assert result["paths"]["/test"]["get"]["responses"]["200"]["content"]["application/json"]["schema"] == {
        "type": "object"}


def test_validate_params():
    mock_schema = {
        "paths": {
            "/test": {
                "get": {
                    "parameters": [
                        {"name": "param", "in": "query"}
                    ]
                }
            }
        }
    }

    validate_params = ValidateParams()
    result = validate_params.execute(mock_schema)

    assert result["paths"]["/test"]["get"]["parameters"][0]["schema"] == {"type": "string"}


def test_openapi_processor():
    with patch('requests.get') as mock_get, patch('requests.post') as mock_post:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "openapi": "3.0.0",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {
                "/test": {
                    "get": {
                        "summary": "Test endpoint",
                        "responses": {"200": {"description": "Successful response"}}
                    }
                }
            }
        }

        processor = OpenAPIProcessor(
            fetch_schema=FetchSchema(),
            resolve_schema_refs=ResolveRefs(),
            validate_params=ValidateParams()
        )

        result = processor.process(["http://example.com/schema.json"], "Combined API")

        assert result.info.title == "Combined API"
        assert "/test" in result.paths
        assert result.paths["/test"].get.summary == "Test endpoint"


def test_main_with_multiple_schemas(mock_requests_get, mock_requests_post, cleanup_generated_files):
    schema_urls = ["http://example.com/schema1.json", "http://example.com/schema2.json"]
    output_file = os.path.join(FIXTURES_DIR, "multiple_schemas_output.json")

    mock_requests_get.return_value.status_code = 200
    mock_requests_get.return_value.json.side_effect = [
        {
            "openapi": "3.0.0",
            "info": {"title": "API 1", "version": "1.0.0"},
            "paths": {
                "/test1": {
                    "get": {
                        "summary": "Test endpoint 1",
                        "responses": {"200": {"description": "Successful response"}}
                    }
                }
            }
        },
        {
            "openapi": "3.0.0",
            "info": {"title": "API 2", "version": "1.0.0"},
            "paths": {
                "/test2": {
                    "get": {
                        "summary": "Test endpoint 2",
                        "responses": {"200": {"description": "Successful response"}}
                    }
                }
            }
        }
    ]

    mock_requests_post.return_value.status_code = 200
    mock_requests_post.return_value.json.return_value = {"swagger": "2.0"}

    main(schema_urls, "Combined APIs", output_file)

    assert os.path.exists(output_file)
    with open(output_file, 'r') as f:
        content = json.load(f)
        assert content == {"swagger": "2.0"}


def test_main_with_ignored_paths(mock_requests_get, mock_requests_post, cleanup_generated_files):
    schema_url = "http://example.com/schema.json"
    output_file = os.path.join(FIXTURES_DIR, "ignored_paths_output.json")

    mock_requests_get.return_value.status_code = 200
    mock_requests_get.return_value.json.return_value = {
        "openapi": "3.0.0",
        "info": {"title": "Test API", "version": "1.0.0"},
        "paths": {
            "/test": {
                "get": {
                    "summary": "Test endpoint",
                    "responses": {"200": {"description": "Successful response"}}
                }
            },
            "/health": {
                "get": {
                    "summary": "Health check",
                    "responses": {"200": {"description": "Healthy"}}
                }
            }
        }
    }

    mock_requests_post.return_value.status_code = 200
    mock_requests_post.return_value.json.return_value = {"swagger": "2.0"}

    main([schema_url], "Test API", output_file)

    assert os.path.exists(output_file)
    with open(output_file, 'r') as f:
        content = json.load(f)
        assert content == {"swagger": "2.0"}

    # Verify that the /health path was ignored
    processor = OpenAPIProcessor(
        fetch_schema=FetchSchema(),
        resolve_schema_refs=ResolveRefs(),
        validate_params=ValidateParams()
    )
    result = processor.process([schema_url], "Test API")
    assert "/test" in result.paths
    assert "/health" not in result.paths


def test_generate_output():
    schema_urls = [
        "https://tracker.icon.community/api/v1/governance/docs/openapi.json",
        "https://tracker.icon.community/api/v1/contracts/docs/openapi.json",
        "https://tracker.icon.community/api/v1/statistics/docs/openapi.json",
        "https://tracker.icon.community/api/v1/docs/doc.json",
    ]
    main(schema_urls, title="Icon", output_file="icon-out.json")
