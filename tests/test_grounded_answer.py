import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from agent_kb.grounded_answer import (
    GroundedAnswerResult,
    GroundedAnswerer,
    build_grounded_prompt,
)
from agent_kb.vector_store import SearchResult
from scripts.answer_with_context import main, parse_args
from scripts.index_knowledge_base import main as index_main


class FakeModelClient:
    def __init__(self) -> None:
        self.prompt = ""

    def complete(self, prompt: str) -> str:
        self.prompt = prompt
        return "基于上下文的回答"

    def stream(self, prompt: str):
        yield self.complete(prompt)


def _result(
    chunk_id: str = "agent.md#0",
    text: str = "Agent 会在目标、上下文、工具和反馈之间做选择。",
) -> SearchResult:
    return SearchResult(
        score=0.88,
        chunk_id=chunk_id,
        source_path="agent.md",
        title="Agent 概念边界",
        chunk_index=0,
        start_char=0,
        end_char=len(text),
        text=text,
    )


class GroundedAnswerTest(unittest.TestCase):
    def test_build_grounded_prompt_includes_question_and_context(self):
        prompt = build_grounded_prompt("什么是 Agent？", [_result()])

        self.assertIn("只能基于给定上下文回答", prompt)
        self.assertIn("什么是 Agent？", prompt)
        self.assertIn("[agent.md#0]", prompt)
        self.assertIn("Agent 概念边界", prompt)
        self.assertIn("Agent 会在目标、上下文、工具和反馈之间做选择。", prompt)

    def test_grounded_answerer_sends_prompt_to_model_client(self):
        client = FakeModelClient()

        result = GroundedAnswerer(client).answer("什么是 Agent？", [_result()])

        self.assertEqual(
            result,
            GroundedAnswerResult(
                question="什么是 Agent？",
                answer="基于上下文的回答",
                contexts=[_result()],
            ),
        )
        self.assertIn("什么是 Agent？", client.prompt)
        self.assertIn("Agent 会在目标、上下文、工具和反馈之间做选择。", client.prompt)

    def test_parse_args_uses_dry_run_defaults(self):
        args = parse_args(["什么是 Agent？"])

        self.assertEqual(args.question, "什么是 Agent？")
        self.assertFalse(args.real)
        self.assertEqual(args.provider, "fastembed")
        self.assertEqual(args.top_k, 3)

    def test_answer_script_uses_retrieved_context_in_dry_run(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source_dir = root / "knowledge"
            vector_store_path = root / "qdrant"
            source_dir.mkdir()
            (source_dir / "agent.md").write_text(
                "# Agent\n\nAgent 会在目标、上下文、工具和反馈之间做选择。",
                encoding="utf-8",
            )
            with redirect_stdout(io.StringIO()):
                index_main(
                    [
                        str(source_dir),
                        "--vector-store-path",
                        str(vector_store_path),
                        "--collection-name",
                        "test_chunks",
                        "--provider",
                        "hashing",
                        "--dimensions",
                        "8",
                        "--chunk-size",
                        "80",
                        "--overlap",
                        "0",
                    ]
                )

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(
                    [
                        "什么是 Agent？",
                        "--vector-store-path",
                        str(vector_store_path),
                        "--collection-name",
                        "test_chunks",
                        "--provider",
                        "hashing",
                        "--dimensions",
                        "8",
                        "--top-k",
                        "1",
                    ]
                )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertIn("mode=dry-run", output)
        self.assertIn("contexts=1", output)
        self.assertIn("answer:", output)
        self.assertIn("Agent 会在目标、上下文、工具和反馈之间做选择。", output)


if __name__ == "__main__":
    unittest.main()
