#!/usr/bin/env python3
"""Claude API に review を渡して index.html にパッチを適用"""
import argparse, json, os, sys, subprocess

def apply_patch(review_path: str, site_path: str, output_path: str):
    review = json.load(open(review_path))
    html = open(site_path).read()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ANTHROPIC_API_KEY not set — dry-run mode (no changes applied)")
        with open(output_path, "w") as f:
            f.write(html)
        return

    # anthropic SDK が無くても動くように直接 curl
    prompt = f"""あなたはWebフロントエンドのデザインエンジニアです。以下のレビューに基づき index.html を改善してください。

# レビュー
{json.dumps(review, ensure_ascii=False, indent=2)}

# 現在の index.html
```html
{html}
```

# ルール
- 出力は改善後の index.html **全文のみ**。前後の説明・マークダウンフェンス禁止。
- single self-contained HTML を維持(<style>と<script>を内包)。
- 破壊的変更禁止。デザインシステム(CSS変数)は維持。
- レビュー指摘のうち score < 90 のペルソナの issues を優先解消。
- 改善は差分最小限。無関係な箇所は変更しない。"""

    import urllib.request
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        headers={
            "content-type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
        data=json.dumps({
            "model": "claude-opus-4-7",
            "max_tokens": 32000,
            "messages": [{"role": "user", "content": prompt}]
        }).encode()
    )
    with urllib.request.urlopen(req, timeout=180) as r:
        resp = json.loads(r.read())
    new_html = resp["content"][0]["text"]
    # 前後のマークダウンフェンスが混入した場合の掃除
    if new_html.strip().startswith("```"):
        new_html = "\n".join(new_html.strip().split("\n")[1:-1])
    with open(output_path, "w") as f:
        f.write(new_html)
    print(f"ok: {output_path} ({len(new_html)} bytes)")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", required=True)
    ap.add_argument("--site", required=True)
    ap.add_argument("--output", required=True)
    a = ap.parse_args()
    apply_patch(a.review, a.site, a.output)
