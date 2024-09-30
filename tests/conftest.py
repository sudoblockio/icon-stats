import asyncio
import logging
import os
from typing import Generator

import pytest
from _pytest.logging import caplog as _caplog
from fastapi.testclient import TestClient
from loguru import logger

from icon_stats.config import Settings, config
from icon_stats.db import get_session


@pytest.fixture(scope="session", autouse=True)
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    pending = asyncio.tasks.all_tasks(loop)
    loop.run_until_complete(asyncio.gather(*pending))
    loop.run_until_complete(asyncio.sleep(1))

    loop.close()


@pytest.fixture(scope="session")
def db():
    # SessionMade = sessionmaker(bind=engine)
    SessionMade = get_session("stats")
    session = SessionMade()

    yield session


@pytest.fixture(scope="module")
def client() -> Generator:
    from icon_stats.main_api import app

    with TestClient(app) as c:
        yield c


@pytest.fixture
def caplog(_caplog):
    class PropogateHandler(logging.Handler):
        def emit(self, record):
            logging.getLogger(record.name).handle(record)

    handler_id = logger.add(PropogateHandler(), format="{message} {extra}")
    yield _caplog
    logger.remove(handler_id)


class EnvLoader:
    """
    Singleton to read env file and return list of env vars. Only want to run this once
     per test since this won't change through tests.
    """

    _instance = None
    _loaded = False
    _env_vars = []

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_env(self, filepath):
        if not self._loaded:
            self._env_vars = self._set_env_from_file(filepath)
            self._loaded = True
        return self._env_vars

    def _set_env_from_file(self, filepath) -> list[tuple[str, str]]:
        """Get list of tuples from an env file to temporarily set them on tests."""
        env_vars = []
        if os.path.isfile(filepath):
            with open(filepath, "r") as f:
                for line in f:
                    line = line.strip()  # Remove leading and trailing whitespace
                    if line and not line.startswith("#"):  # Ignore empty lines and comments
                        key, value = line.split("=", 1)
                        value = value.strip().strip('"').strip("'")
                        env_vars.append((key, value))
        return env_vars


@pytest.fixture(autouse=True)
def config_override(request):
    """
    Override the config with values in an .env.test file for tests. Needed for sensitive
     items such as API keys for tests.
    """
    no_config_override = request.node.get_closest_marker("no_config_override")
    if not no_config_override:
        # Run the override logic unless the test is marked
        test_env_file = os.path.join(os.path.dirname(__file__), "..", ".env.test")

        # If .env.test does not exist, do nothing
        if not os.path.exists(test_env_file):
            # Skip if the file does not exist
            yield

        # Get environment variables from .env.test
        loader = EnvLoader.instance()
        env_vars = loader.get_env(test_env_file)

        # Store the original environment variables
        original_values = {}
        for key, value in env_vars:
            original_values[key] = os.environ.get(key)
            os.environ[key] = value

        # Create temp config which will pick up new environment variable values
        tmp_config = Settings()

        # Override the values in the imported config
        for k, v in tmp_config.__dict__.items():
            setattr(config, k, v)

        yield

        # Cleanup: Restore original environment variable values if they didn't exist
        for key, original_value in original_values.items():
            if original_value is not None:
                os.environ[key] = original_value
            else:
                os.environ.pop(key, None)
    else:
        # Need to yield no matter what for some reason?
        yield
