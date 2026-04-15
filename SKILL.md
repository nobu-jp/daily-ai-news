---
name: daily-ai-news
description: 毎朝のAI・Claudeニュース収集（Anthropic/Claude更新、AI業界ニュース、Claude Code/MCP情報）
---

今日の日付を取得し、以下のAI・Claudeニュースを検索・収集して日本語でまとめてください。

【収集対象】
1. Anthropic / Claude の最新アップデート・リリース情報
2. AI業界の主要ニュース（過去24時間）
3. Claude Code・MCP関連の新情報があれば

【出力フォーマット】
# 🌅 AI朝刊 - {今日の日付}

## 🤖 Claude / Anthropic アップデート
- （あれば箇条書き、なければ「本日なし」）

## 📰 AI業界ニュース TOP3
1. 
2. 
3. 

## 💡 Claude Code / MCP 関連
- （あれば。なければ省略）

---

## 📖 用語解説
本日の記事に登場した専門用語を表形式で解説すること。

| 用語 | 解説 |
|------|------|
| （記事中の専門用語） | （平易な日本語で1〜2文の解説） |

---
情報源URLも各項目に付記すること。

収集が完了したら、結果をMarkdownファイルとして保存してください。ファイル名は `news/YYYY-MM-DD.md` の形式で。
