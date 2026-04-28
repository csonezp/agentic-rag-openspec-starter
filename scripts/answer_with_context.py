import os
import sys
from argparse import ArgumentParser, Namespace
from typing import Mapping, Optional, Sequence

from agent_kb.call_observability import format_observation_lines
from agent_kb.config import AppConfig
from agent_kb.deepseek_client import (
    DeepSeekCallError,
    DeepSeekChatCompletionsModelClient,
)
from agent_kb.embeddings import (
    DEFAULT_FASTEMBED_DIMENSIONS,
    DEFAULT_FASTEMBED_MODEL_NAME,
    FastEmbedEmbeddingModel,
    HashingEmbeddingModel,
)
from agent_kb.grounded_answer import build_grounded_prompt
from agent_kb.hello_agent import DryRunModelClient
from agent_kb.vector_store import LocalQdrantVectorStore, VectorStoreConfig


def parse_args(argv: Sequence[str]) -> Namespace:
    parser = ArgumentParser(description="基于本地检索上下文生成回答。")
    parser.add_argument("question")
    parser.add_argument("--vector-store-path", default="data/qdrant")
    parser.add_argument("--collection-name", default="knowledge_chunks")
    parser.add_argument("--provider", choices=["fastembed", "hashing"], default="fastembed")
    parser.add_argument("--model-name", default=DEFAULT_FASTEMBED_MODEL_NAME)
    parser.add_argument("--dimensions", type=int, default=DEFAULT_FASTEMBED_DIMENSIONS)
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--real", action="store_true", help="调用真实 DeepSeek 模型生成回答。")
    parser.add_argument(
        "--show-prompt",
        action="store_true",
        help="打印真实传递给模型的 grounded prompt。",
    )
    return parser.parse_args(argv)


def main(
    argv: Optional[Sequence[str]] = None,
    env: Optional[Mapping[str, str]] = None,
) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    config = AppConfig.from_env(os.environ if env is None else env)
    embedding_model = _create_embedding_model(args)
    query_embedding = embedding_model.embed(args.question)
    store = LocalQdrantVectorStore(
        VectorStoreConfig(
            path=args.vector_store_path,
            collection_name=args.collection_name,
            dimensions=embedding_model.dimensions,
        )
    )
    contexts = store.search(query_embedding=query_embedding, top_k=args.top_k)

    if args.real:
        if config.model_provider != "deepseek":
            print(f"不支持的 MODEL_PROVIDER：{config.model_provider}", file=sys.stderr)
            return 2
        if not config.has_deepseek_api_key:
            print("真实模式需要先配置 DEEPSEEK_API_KEY。", file=sys.stderr)
            return 2
        model_client = DeepSeekChatCompletionsModelClient(config)
        mode = "real"
    else:
        model_client = DryRunModelClient()
        mode = "dry-run"

    print(f"mode={mode}")
    print(f"question={args.question}")
    print(f"vector_store_path={args.vector_store_path}")
    print(f"collection_name={args.collection_name}")
    print(f"provider={args.provider}")
    if args.provider == "fastembed":
        print(f"embedding_model={args.model_name}")
    print(f"top_k={args.top_k}")
    print(f"contexts={len(contexts)}")
    prompt = build_grounded_prompt(args.question, contexts)
    if args.show_prompt:
        print("prompt:")
        print(prompt)

    try:
        if args.real:
            result = model_client.complete_with_observation(prompt)
            answer = result.text
            observation = result.observation
        else:
            answer = model_client.complete(prompt)
            observation = None
    except DeepSeekCallError as exc:
        _print_observation_summary(format_observation_lines(exc.observation))
        print(str(exc), file=sys.stderr)
        return 1

    print("answer:")
    print(answer)
    if observation is not None:
        _print_observation_summary(format_observation_lines(observation))
    return 0


def _create_embedding_model(args: Namespace):
    if args.provider == "fastembed":
        return FastEmbedEmbeddingModel(
            model_name=args.model_name,
            dimensions=args.dimensions,
        )
    return HashingEmbeddingModel(dimensions=args.dimensions)


def _print_observation_summary(lines: Sequence[str]) -> None:
    print("observation:")
    for line in lines:
        print(line)


if __name__ == "__main__":
    sys.exit(main())
