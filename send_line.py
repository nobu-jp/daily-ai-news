"""
Daily AI News - LINE Notifier
毎朝のAIニュースを収集してLINEに送信するスクリプト
"""
import os
import re
import sys
import requests
from datetime import datetime, timezone, timedelta

import anthropic

JST = timezone(timedelta(hours=9))


def get_today_date():
    now = datetime.now(JST)
    return now.strftime('%Y-%m-%d'), now.strftime('%Y年%-m月%-d日')


def collect_news(date_str, date_jp):
    client = anthropic.Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])

    prompt = f"""今日の日付は{date_jp}です。以下のAI・Claudeニュースを検索・収集して日本語でまとめてください。

【収集対象】
1. Anthropic / Claude の最新アップデート・リリース情報
2. AI業界の主要ニュース（過去24時間）
3. Claude Code・MCP関連の新情報があれば

【出力フォーマット（必ずこの形式で）】
# 🌅 AI朝刊 - {date_jp}

## 🤖 Claude / Anthropic アップデート
- （あれば箇条書き、なければ「本日なし」）

## 📰 AI業界ニュース TOP3
1.
2.
3.

## 💡 Claude Code / MCP 関連
- （あれば。なければ省略）

---
情報源URLも各項目に付記すること。"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 5}],
        messages=[{"role": "user", "content": prompt}]
    )

    content = ""
    for block in message.content:
        if hasattr(block, 'text'):
            content += block.text

    return content


def save_news(date_str, content):
    os.makedirs('news', exist_ok=True)
    filepath = f'news/{date_str}.md'
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
        if '収集日時' not in content:
            f.write(f'\n\n---\n\n*収集日時: {date_str} | データソース: Web検索による自動収集*\n')
    return filepath


def format_for_line(content):
    """Markdown → LINE用テキストに変換"""
    lines = content.split('\n')
    formatted = []

    for line in lines:
        line = line.rstrip()
        if line.startswith('# '):
            formatted.append(line[2:])
        elif line.startswith('## '):
            formatted.append('\n▼ ' + line[3:])
        elif line.startswith('### '):
            formatted.append('◆ ' + line[4:])
        elif line.startswith('- **') or line.startswith('- '):
            formatted.append('• ' + line[2:])
        elif line.startswith('---'):
            formatted.append('─────────────')
        else:
            formatted.append(line)

    text = '\n'.join(formatted)

    # Markdownリンク → テキストのみ
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # 太字
    text = re.sub(r'\*\*([^\*]+)\*\*', r'\1', text)
    # 斜体
    text = re.sub(r'\*([^\*]+)\*', r'\1', text)
    # 連続改行を整理
    text = re.sub(r'\n{3,}', '\n\n', text)

    # LINE上限 5000文字
    if len(text) > 4900:
        text = text[:4900] + '\n\n…(省略)'

    return text.strip()


def send_line_message(text):
    token = os.environ['LINE_CHANNEL_ACCESS_TOKEN']
    user_id = os.environ['LINE_USER_ID']

    url = 'https://api.line.me/v2/bot/message/push'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
    }
    payload = {
        "to": user_id,
        "messages": [{"type": "text", "text": text}],
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        print(f"LINE API error: {response.status_code} {response.text}", file=sys.stderr)
        response.raise_for_status()

    return response.json()


def main():
    date_str, date_jp = get_today_date()
    print(f"Date: {date_jp}")

    filepath = f'news/{date_str}.md'

    if os.path.exists(filepath):
        print(f"既存ファイルを使用: {filepath}")
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        print("ニュース収集中...")
        content = collect_news(date_str, date_jp)
        save_news(date_str, content)
        print(f"保存完了: {filepath}")

    print("LINEに送信中...")
    text = format_for_line(content)
    result = send_line_message(text)
    print(f"送信完了: {result}")


if __name__ == '__main__':
    main()
