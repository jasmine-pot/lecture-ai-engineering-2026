# 第3回 解答

## 演習

- 第1回（素のLLM）とエージェントの回答の違い：  
推論によるもっともらしい一般的な回答から、[tool call]   search_glossary({'query': '3レベル'})を経由することで、確認性が高い回答をするようになった。
- `--trace` で見えたツール呼び出し（ツール名と引数）：  
[tool call]   search_glossary({'query': '3レベル'})
- 1つの質問での LLM 呼び出し回数（`requests`）：  
requests=2
- 追加したツールと、docstring に書いた説明：  
  - 追加したツール：agent.tool_plain(tools.make_quiz)  
  - docstring に書いた説明：  
def make_quiz(lecture: int) -> str:  
    """指定した回の用語から1つを選び、  
    確認問題と答えを返す。  
   
    「第2回の確認問題を出して」のように、  
    復習用の問題を求められたときに使う。  
    """

## 宿題

- 取り組んだレベル：基礎
- やったこと：[1] INSTRUCTIONS の変更と [2] make_quiz() docstring の変更  
1. INSTRUCTIONS の変更  
INSTRUCTIONS に以下の記述を追加し、$ uv run python -m app.agent --trace "「RNN」とは 何ですか ？"を実行。  
\- 「用語集にはない」と伝えた場合、「一般的には以下のようなことがありえます」と伝えて推測する。  
2. make_quiz()のdocstringの変更  
make_quiz()の docstring に以下の記述を追加し、uv run python -m app.agent --trace "第0回の内容 から問題を出して"を実行。

- 結果：
1. 用語集に存在しない用語に対する質問に対しては、用語集にないと答えた上で、一般的な回答を行うようになった。ただし、関連する回も推測して回答する。
2. 指定範囲外の講義回数を指定すると、ツールが呼び出しの対象外から外れ(trace [tool call] make_quiz()が発生しない)ようになった。処理が軽減された。

- 気づき・疑問：  
docstring に数値の指定範囲の制限を記述した際に、ゼロを指定範囲外にすることが難しかった。具体的な値のゼロを記述に含めることで解決した。このことはモデルによるのかもしれない。
