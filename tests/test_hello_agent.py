import unittest

from agent_kb.hello_agent import HelloAgent, ModelClient


class FakeModelClient(ModelClient):
    def complete(self, prompt: str) -> str:
        return f"echo: {prompt}"


class HelloAgentTest(unittest.TestCase):
    def test_runs_prompt_through_injected_model_client(self):
        agent = HelloAgent(model_client=FakeModelClient())

        result = agent.run("Say hello to agent development.")

        self.assertEqual(result, "echo: Say hello to agent development.")


if __name__ == "__main__":
    unittest.main()
