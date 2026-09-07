#!/usr/bin/env python3
"""gsk understand_images でスクリーンショットを3ペルソナ視点で批評"""
import argparse, json, subprocess, os, re, sys

def critique(screenshot: str, personas: dict) -> dict:
    # まず screenshot を gsk upload して URL 取得
    up = subprocess.run(["gsk", "upload", screenshot],
                        capture_output=True, text=True, check=True)
    up_json = json.loads(up.stdout)
    url = up_json["data"]["url"] if "data" in up_json else up_json.get("url")
    if not url:
        raise RuntimeError(f"upload failed: {up.stdout}")

    persona_desc = "\n".join(f"- {k}: {v}" for k, v in personas["prompts"].items())
    prompt = f"""日本語のロボット学習書ランディングページのスクリーンショット。
以下 {len(personas["prompts"])} 名の視点で並列に批評してください。それぞれ:
- 具体的な指摘を2-3個(場所+改善案)
- 0-100のスコア
- JSON形式で回答: {{"reviews":[{{"persona":"key","score":N,"issues":["..."],"praise":["..."]}},...]}}

ペルソナ:
{persona_desc}

視覚的欠陥(オーバーラップ、テキスト切れ、コントラスト不足、位置ズレ)があれば必ず flag に含めること。
全体平均スコアが95以上 かつ 重大欠陥ゼロなら "converged": true をトップレベルに置いてください。"""

    res = subprocess.run(
        ["gsk", "understand_images", "-i", url, "-r", prompt],
        capture_output=True, text=True, check=True
    )
    raw = res.stdout
    # JSON 抽出
    m = re.search(r'\{.*\}', raw.replace("\n", " "), re.DOTALL)
    try:
        # gsk のレスポンスから result 文字列を取り出す
        outer = json.loads(raw)
        result_text = outer["data"]["results"][0]["result"]
        m2 = re.search(r'\{.*\}', result_text, re.DOTALL)
        payload = json.loads(m2.group(0)) if m2 else {"raw": result_text}
    except Exception as e:
        payload = {"raw": raw, "error": str(e)}

    payload["round"] = personas["round"]
    payload["personas"] = personas["selected"]
    payload["screenshot_url"] = url
    return payload

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--screenshot", required=True)
    ap.add_argument("--personas", required=True)
    ap.add_argument("--output", required=True)
    a = ap.parse_args()

    personas = json.load(open(a.personas))
    result = critique(a.screenshot, personas)
    with open(a.output, "w") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"ok: {a.output}")
