#!/usr/bin/env python3
"""スクリーンショットを3ペルソナ視点で批評 (Anthropic Vision API 直叩き)

- GitHub Actions runner に gsk CLI は無いので Anthropic API を使う
- ANTHROPIC_API_KEY が未設定なら dry-run で固定スコアを返す
"""
import argparse, json, os, sys, base64, re, urllib.request

def critique(screenshot: str, personas: dict) -> dict:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        # dry-run: ダミースコアを返してループを継続テスト可能に
        print("[warn] ANTHROPIC_API_KEY not set — dry-run", file=sys.stderr)
        return {
            "round": personas["round"],
            "personas": personas["selected"],
            "reviews": [{"persona": k, "score": 92, "issues": ["dry-run"], "praise": []}
                        for k in personas["selected"]],
            "dry_run": True,
        }

    with open(screenshot, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()

    persona_desc = "\n".join(f"- {k}: {v}" for k, v in personas["prompts"].items())
    prompt = f"""日本語のロボット学習書ランディングページのスクリーンショット。
以下 {len(personas["prompts"])} 名の視点で並列に批評してください。それぞれ:
- 具体的な指摘を2-3個(場所+改善案)
- 0-100のスコア

必ずJSON形式**のみ**で回答:
{{"reviews":[{{"persona":"key","score":N,"issues":["..."],"praise":["..."]}}]}}

ペルソナ:
{persona_desc}

視覚的欠陥(オーバーラップ、テキスト切れ、コントラスト不足、位置ズレ)を必ずissuesに含めること。"""

    body = {
        "model": "claude-opus-4-7",
        "max_tokens": 8000,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": img_b64}},
                {"type": "text", "text": prompt},
            ]
        }]
    }
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        headers={
            "content-type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
        data=json.dumps(body).encode()
    )
    with urllib.request.urlopen(req, timeout=180) as r:
        resp = json.loads(r.read())
    raw = resp["content"][0]["text"]
    m = re.search(r'\{.*\}', raw, re.DOTALL)
    if m:
        payload = json.loads(m.group(0))
    else:
        payload = {"raw": raw, "reviews": []}
    payload["round"] = personas["round"]
    payload["personas"] = personas["selected"]
    return payload

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--screenshot", required=True)
    ap.add_argument("--personas", required=True)
    ap.add_argument("--output", required=True)
    a = ap.parse_args()
    personas = json.load(open(a.personas))
    result = critique(a.screenshot, personas)
    os.makedirs(os.path.dirname(a.output) or ".", exist_ok=True)
    with open(a.output, "w") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"ok: {a.output}")
