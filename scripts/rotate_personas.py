#!/usr/bin/env python3
"""ペルソナローテーション: 16人プールから3人を選ぶ (履歴考慮)"""
import argparse, json, os, hashlib

PERSONAS = {
    # 固定8人
    "alex_design_lead":       "デザインリード。全体の視覚設計・独自性・AIっぽさを判断",
    "ken_frontend":           "フロントエンジニア。CSS/レイアウト精度・実装品質",
    "sara_ux":                "UXリサーチャー。情報階層・CTA明瞭性・遷移設計",
    "yuki_motion":            "モーションデザイナー。アニメ・インタラクションの効果",
    "ren_content":            "コンテンツ戦略。コピー・トーン・和英混在の妥当性",
    "mika_a11y":              "アクセシビリティ。WCAG準拠・コントラスト・キーボード",
    "yamada_marketing":       "書籍マーケ。CVR・above-the-fold・訴求強度",
    "tanaka_reader":          "一般読者32歳・未経験。買いたくなるか",
    # プール8人
    "chris_photographer":     "プロダクト写真家。ビジュアル訴求・実機説得力",
    "nao_youtuber":           "ロボットYouTuber(登録20万)。視聴者に薦めるか",
    "emma_rights_agent":      "海外版権エージェント。国際市場での売れ行き",
    "library_curator":        "大学図書館司書。教科書・参考図書としての採用",
    "student_reviewer":       "工学部3年ロボコン部。予算感・実現可能性",
    "senior_reader":          "60代趣味人。老眼でも読めるか、敷居の高さ",
    "a11y_advocate":          "障害当事者/A11y専門家。認知負荷・音声読み上げ",
    "vc_investor":            "テック系VC。事業性・エコシステム性",
}

def choose(round_n: int, history_dir: str):
    keys = list(PERSONAS.keys())
    # ラウンド番号ベースの決定的ローテーション + 微ランダム
    seed = int(hashlib.sha1(f"round-{round_n}".encode()).hexdigest()[:8], 16)
    idx = [(seed + round_n * i) % len(keys) for i in (0, 5, 11)]
    # 重複排除
    seen, out = set(), []
    for i in idx:
        while keys[i] in seen:
            i = (i + 1) % len(keys)
        seen.add(keys[i])
        out.append(keys[i])
    return out

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", type=int, required=True)
    ap.add_argument("--history", default="reviews/")
    ap.add_argument("--output", required=True)
    a = ap.parse_args()

    selected = choose(a.round, a.history)
    payload = {"round": a.round, "selected": selected,
               "prompts": {k: PERSONAS[k] for k in selected}}
    with open(a.output, "w") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
