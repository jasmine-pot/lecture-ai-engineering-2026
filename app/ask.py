"""第1回: 素のLLMと会話するスクリプト。

使い方:
    uv run python -m app.ask "LoRAとは何ですか？"
    uv run python -m app.ask            # 質問を省略すると、講座に固有の質問をする

回答後に続けて質問すると、会話履歴を保ったまま応答する。
ツールを持たない「素の」呼び出し。
講座に固有のことを聞くと、「分からない」と答えるか、一般論でもっともらしく答える
（講座の実際とは違う）ことを確かめよう。
（第3回で、用語集を検索できるエージェントにして改善する）
"""

import argparse
import time

from google import genai
from google.genai import errors

from app.config import MODEL, api_error_message, get_api_key

from google.genai import types  # 設定用の型をインポート

# 講座に固有の質問。正しい答えは data/glossary.json の homework-levels にある
DEFAULT_QUESTION = "AIE2026の講座の宿題にある「3レベル」とは何ですか？"


def ask(question: str, history: list[types.Content] | None = None) -> str:
    client = genai.Client(api_key=get_api_key())
    # response = client.models.generate_content(model=MODEL, contents=question)
    # 1. configオブジェクトを作成し、内部でtemperatureを指定する
    config = types.GenerateContentConfig(
        temperature=1.0,  # 0.0（堅実）〜 2.0（クリエイティブ）の間で調整
    )
    user_message = types.Content(
        role="user",
        parts=[types.Part.from_text(text=question)],
    )
    contents = [*(history or []), user_message]
    # 2. generate_content の config 引数に渡す
    started_at = time.perf_counter()
    response = client.models.generate_content(
        model=MODEL,
        contents=contents,
        config=config  # ← ここに追記します
    )
    elapsed_seconds = time.perf_counter() - started_at
    usage = response.usage_metadata
    input_tokens = usage.prompt_token_count if usage else None
    output_tokens = usage.candidates_token_count if usage else None
    print(f"[usage] input_tokens={input_tokens}, output_tokens={output_tokens}")
    print(f"[response time] {elapsed_seconds:.2f}s")

    if history is not None:
        history.extend(
            [
                user_message,
                types.Content(
                    role="model",
                    parts=[types.Part.from_text(text=response.text)],
                ),
            ]
        )

    return response.text


def main() -> None:
    parser = argparse.ArgumentParser(description="素のLLMに質問する")
    parser.add_argument("question", nargs="?", default=DEFAULT_QUESTION)
    args = parser.parse_args()

    print(f"[model] {MODEL}")
    question = args.question
    history: list[types.Content] = []
    try:
        while True:
            print(f"[質問] {question}\n")
            print(ask(question, history))
            question = input("\n続けて質問してください（終了: q、または空入力）: ").strip()
            if not question or question.lower() in {"q", "quit", "exit"}:
                break
    except errors.APIError as e:
        print(api_error_message(e.code, e.message))
        raise SystemExit(1)
    except EOFError:
        pass


if __name__ == "__main__":
    main()
