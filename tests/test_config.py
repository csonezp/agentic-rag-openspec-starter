import os
import unittest

from agent_kb.config import AppConfig


class AppConfigTest(unittest.TestCase):
    def test_loads_defaults_when_environment_is_empty(self):
        config = AppConfig.from_env({})

        self.assertEqual(config.model, "gpt-4.1-mini")
        self.assertEqual(config.embedding_model, "text-embedding-3-small")
        self.assertFalse(config.has_openai_api_key)

    def test_loads_values_from_environment(self):
        config = AppConfig.from_env(
            {
                "OPENAI_API_KEY": "sk-test",
                "OPENAI_MODEL": "gpt-test",
                "OPENAI_EMBEDDING_MODEL": "embed-test",
            }
        )

        self.assertEqual(config.openai_api_key, "sk-test")
        self.assertEqual(config.model, "gpt-test")
        self.assertEqual(config.embedding_model, "embed-test")
        self.assertTrue(config.has_openai_api_key)


if __name__ == "__main__":
    unittest.main()
