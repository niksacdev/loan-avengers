"""
Test that the conftest.py environment variable isolation works correctly.
"""

import os

import pytest


class TestEnvironmentIsolation:
    """Test environment variable isolation in conftest.py."""

    def test_env_vars_isolated_when_none_originally(self):
        """Test that env vars are properly cleaned up when they were None originally."""
        # These should be set by the conftest.py fixture
        assert os.environ.get("FOUNDRY_PROJECT_ENDPOINT") == "https://test-project.projects.ai.azure.com"
        assert os.environ.get("FOUNDRY_MODEL_DEPLOYMENT_NAME") == "test-model"

    def test_env_vars_isolated_between_tests(self):
        """Test that environment changes don't leak between tests."""
        # Change env vars during test
        os.environ["FOUNDRY_PROJECT_ENDPOINT"] = "https://modified-endpoint.ai.azure.com"
        os.environ["FOUNDRY_MODEL_DEPLOYMENT_NAME"] = "modified-model"

        # These changes should not persist to other tests due to conftest.py cleanup

    def test_env_vars_reset_after_modification(self):
        """Test that env vars are reset properly even if previous test modified them."""
        # Should be back to test values, not modified values
        assert os.environ.get("FOUNDRY_PROJECT_ENDPOINT") == "https://test-project.projects.ai.azure.com"
        assert os.environ.get("FOUNDRY_MODEL_DEPLOYMENT_NAME") == "test-model"


@pytest.mark.integration
class TestIntegrationEnvNotOverridden:
    """Test that integration tests don't get env overrides."""

    def test_integration_uses_real_env_values(self):
        """Integration tests should use real .env values, not test overrides."""
        # For integration tests, the conftest should not override these
        # The values will depend on what's in the actual .env file
        endpoint = os.environ.get("FOUNDRY_PROJECT_ENDPOINT")
        model = os.environ.get("FOUNDRY_MODEL_DEPLOYMENT_NAME")

        # Should NOT be the test values
        if endpoint is not None:
            assert endpoint != "https://test-project.projects.ai.azure.com"
        if model is not None:
            assert model != "test-model"
