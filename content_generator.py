"""
content_generator.py - LLM API でツイート文を生成する

切り替え方法:
    .env の LLM_PROVIDER を変更するだけ
        LLM_PROVIDER=anthropic  → Claude (claude-haiku-4-5-20251001)
        LLM_PROVIDER=openai     → OpenAI (gpt-4o-mini)

必要な環境変数:
    Anthropic: ANTHROPIC_API_KEY
    OpenAI:    OPENAI_API_KEY
"""

import os
import re

# モデル設定（変更する場合はここを編集）
ANTHROPIC_MODEL = "claude-haiku-4-5-20251001"
OPENAI_MODEL    = "gpt-4o-mini"

SYSTEM_PROMPT = """あなたは X（旧Twitter）の投稿文を作成するアシスタントです。
与えられたニュース情報をもとに、読者の興味を引く投稿文を生成してください。"""

USER_PROMPT_TEMPLATE = """以下のニュース記事をもとに、X（旧Twitter）への投稿文を1つ作成してください。

【条件】
- 日本語で書く
- 140文字前後（最大280文字厳守）
- 読者が思わずリツイートしたくなるような書き出しにする
- 事実を正確に伝えつつ、自分の意見や感想を1文添える
- 関連するハッシュタグを2〜3個、末尾に付ける
- URLは含めない
- 余計な説明・前置き・括弧書きは不要。投稿文のみを返す

【参考ニュース】
{trends_text}"""


def generate_tweet(trends: list[dict]) -> str:
    """
    トレンド情報をもとに LLM でツイート文を生成する。
    使用プロバイダーは環境変数 LLM_PROVIDER で切り替え可能。
    """
    provider = os.getenv("LLM_PROVIDER", "anthropic").lower()

    if provider == "openai":
        return _generate_with_openai(trends)
    elif provider == "anthropic":
        return _generate_with_anthropic(trends)
    else:
        raise RuntimeError(f"LLM_PROVIDER='{provider}' は未対応です。'anthropic' または 'openai' を指定してください。")


def _generate_with_anthropic(trends: list[dict]) -> str:
    import anthropic

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY が設定されていません。.env ファイルを確認してください。")

    prompt = USER_PROMPT_TEMPLATE.format(trends_text=_format_trends(trends))
    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=400,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text.strip()


def _generate_with_openai(trends: list[dict]) -> str:
    from openai import OpenAI

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY が設定されていません。.env ファイルを確認してください。")

    prompt = USER_PROMPT_TEMPLATE.format(trends_text=_format_trends(trends))
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        max_tokens=400,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": prompt},
        ],
    )
    return response.choices[0].message.content.strip()


def _format_trends(trends: list[dict]) -> str:
    lines = []
    for i, t in enumerate(trends, 1):
        title = t.get("title", "").strip()
        summary = _strip_tags(t.get("summary", "")).strip()
        line = f"{i}. {title}"
        if summary:
            line += f"\n   {summary[:150]}"
        lines.append(line)
    return "\n".join(lines)


def _strip_tags(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text).strip()