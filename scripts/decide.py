#!/usr/bin/env python3
"""スコア集計と停止判定"""
import argparse, json, glob, os, statistics, sys

def score_of(review: dict) -> float:
    if "reviews" in review:
        scores = [r.get("score", 0) for r in review["reviews"]]
        return round(statistics.mean(scores), 1) if scores else 0
    return 0

def is_converged(current: float, history: list) -> bool:
    """3ラウンド連続で 95+ かつ 改善+1未満で収束"""
    if current < 95:
        return False
    if len(history) < 2:
        return False
    recent = history[-2:] + [current]
    if all(s >= 95 for s in recent) and max(recent) - min(recent) < 1.0:
        return True
    return False

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", required=True)
    ap.add_argument("--history", default="reviews/")
    ap.add_argument("--force", default="false")
    a = ap.parse_args()

    current_review = json.load(open(a.review))
    current_score = score_of(current_review)

    history_scores = []
    for path in sorted(glob.glob(os.path.join(a.history, "round-*.json"))):
        if path == a.review:
            continue
        try:
            history_scores.append(score_of(json.load(open(path))))
        except Exception:
            pass

    stop = False
    reason = ""
    if a.force.lower() == "true":
        stop = False
        reason = "force_apply=true"
    elif is_converged(current_score, history_scores):
        stop = True
        reason = "converged (95+ stable)"

    out = {
        "score": current_score,
        "history": history_scores[-5:],
        "stop": stop,
        "reason": reason,
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
