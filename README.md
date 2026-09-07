# robot-book-lp — 32週間ロボット書籍 ランディングページ

**24時間自己改善ループ搭載**の書籍ランディングページ。GitHub Actions が2時間ごとにサイトを評価・改善・commit・deployします。

## 🚀 セットアップ (5分)

### 1. リポジトリ作成 & push

```bash
cd robot-book-lp
git init
git add .
git commit -m "initial: v3 (score 95/100)"
gh repo create robot-book-lp --public --source=. --remote=origin --push
```

### 2. Secrets 登録

GitHub リポジトリの **Settings → Secrets and variables → Actions** で以下を登録:

| Secret 名 | 値 |
|---|---|
| `GSK_TOKEN` | あなたの Genspark API key (`~/.genspark-tool-cli/config.json` から取得) |
| `ANTHROPIC_API_KEY` | Anthropic Console で発行 (https://console.anthropic.com) |

### 3. GitHub Pages 有効化

**Settings → Pages → Source: GitHub Actions** を選択。

### 4. Workflow 起動

```bash
gh workflow run 24h-loop.yml
```

または **Actions タブ → "24h Self-Improvement Loop" → "Run workflow"**。

以降、cron `0 */2 * * *` (2時間ごと) で自動改善が回ります。

## 📁 ディレクトリ構成

```
robot-book-lp/
├── index.html                    # メイン LP (v3, score 95/100)
├── .github/workflows/24h-loop.yml # 24時間ループ workflow
├── scripts/
│   ├── screenshot.js             # Playwright フルページ撮影
│   ├── rotate_personas.py        # 16人プールから3名選抜
│   ├── run_critique.py           # gsk understand_images で批評
│   ├── decide.py                 # スコア集計・停止判定
│   └── apply_review.py           # Claude API でパッチ適用
├── lighthouserc.json             # 品質ゲート設定
├── snapshots/                    # 各ラウンドのスクリーンショット
└── reviews/                      # 各ラウンドの批評 JSON
```

## 🔄 ループの動作

1. **screenshot**: 現行 `index.html` を Playwright で撮影
2. **rotate**: 16ペルソナから3名を決定的ローテーション(重複防止)
3. **critique**: `gsk understand_images` で並列AIレビュー
4. **decide**: スコア集計、95+が3連続なら停止
5. **patch**: Claude API で改善版 `index.html` 生成
6. **verify**: Lighthouse + Pa11y で回帰チェック(失敗ならrevert)
7. **commit + push**: bot commit で main に反映
8. **deploy**: GitHub Pages 自動デプロイ

## 🛑 停止条件

以下いずれかで自動停止:

- 平均スコアが 95+ で 3ラウンド連続 かつ 改善 +1点未満
- Lighthouse A11y < 90 の連続失敗 3回
- `workflow_dispatch` の `force_apply=false` で手動停止

## 📊 モニタリング

- **Actions タブ**: 各ラウンドの実行結果
- **Artifacts**: `round-N` に screenshot + review JSON + pa11y レポート
- **Commits**: `round N: score X` のコミット履歴でスコア推移を可視化

## ⚠️ コスト目安

- gsk understand_images: 1ラウンド ~5 credit × 12/日 = 60 credit/日
- Claude API: 1ラウンド ~$0.5 (opus) × 12/日 = ~$6/日
- GitHub Actions: 1ラウンド ~5分 × 12 = 60分/日 (無料枠2,000分/月内)

**24時間で ~$6 / 60 credit** 程度。fast mode(30分間隔)は4倍。

## 🧑‍💻 チーム(バーチャル16名)

固定8名(Alex/Ken/Sara/Yuki/Ren/Mika/山田/田中) + プール8名(Chris/Nao/Emma/司書/学生/シニア/A11y専門家/VC)

ラウンドごとに3名選抜、同じ組合せ禁止。詳細は `scripts/rotate_personas.py`。

## 📜 v3 到達スコア

| バージョン | 平均スコア |
|---|---|
| v1 | 63.75 |
| v2 | 88.00 |
| **v3** (現行) | **95.00** |

24時間 = 12ラウンド後、スコア98/100 収束見込み。
