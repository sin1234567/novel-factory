# novel-factory

無料で回す前提の小説生成プロジェクトです。

## 目的

- 設定ファイルとネタ在庫から連載向けの章を自動生成する
- 外部AI APIは使わず、ローカルのテンプレ組み立てで回す
- 将来的に有料AIを足しても分離しやすい構成にする

## 構成

```text
novel-factory
├─ auth
├─ data
│  ├─ characters.json
│  ├─ publish_config.json
│  ├─ series_state.json
│  ├─ story_seeds.csv
│  ├─ used_seeds.txt
│  └─ settings.json
├─ out
│  └─ chapters
├─ requirements.txt
├─ scripts
│  ├─ generate_chapter.py
│  ├─ login_kakuyomu.py
│  ├─ mark_used.py
│  └─ publish_kakuyomu.py
└─ README.md
```

## 使い方

1. `python scripts/generate_chapter.py`
2. `out/chapter_latest.md` を確認
3. 問題なければ `python scripts/mark_used.py`

`mark_used.py` を実行すると `used_seeds.txt` と `series_state.json` が更新されます。

## カクヨム下書き投稿

1. `pip install -r requirements.txt`
2. `python -m playwright install chromium`
3. `python scripts/login_kakuyomu.py`
4. `data/publish_config.json` の `work_new_episode_url` を設定
5. `python scripts/publish_kakuyomu.py`

注意:

- 既存の Chrome ログインプロファイルを使う前提です
- Chrome を閉じてから実行した方が安定します
- 投稿はブラウザ自動操作なので、サイトUI変更に弱いです
- 現在のスクリプトは「下書き保存」前提です
- セレクタはカクヨム側の画面変更で調整が必要になることがあります

## 方針

- 完全無料
- まずは連載1話分を2000字以上で下書き生成
- 同じネタの重複防止あり
- 前回あらすじと話数を引き継げる
- `story_seeds.csv` は40話超の種を収録
- 地の文だけでなく会話と情景描写も混ぜる
- 話数に応じて序盤・中盤・終盤の空気を変える
- 中盤以降は監査役「灰島」の影を出しやすくする
- `series_state.json` で未回収の伏線と現在の対立相手を保持する
- Playwright でカクヨム下書き投稿まで自動化できるようにしている
