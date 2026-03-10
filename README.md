# novel-factory

無料で回す前提の小説生成プロジェクトです。

## 目的

- 設定ファイルとネタ在庫から連載向けの章を自動生成する
- 外部AI APIは使わず、ローカルのテンプレ組み立てで回す
- 将来的に有料AIを足しても分離しやすい構成にする

## 構成

```text
novel-factory
├─ data
│  ├─ characters.json
│  ├─ series_state.json
│  ├─ story_seeds.csv
│  ├─ used_seeds.txt
│  └─ settings.json
├─ out
│  └─ chapters
├─ scripts
│  ├─ generate_chapter.py
│  └─ mark_used.py
└─ README.md
```

## 使い方

1. `python scripts/generate_chapter.py`
2. `out/chapter_latest.md` を確認
3. 問題なければ `python scripts/mark_used.py`

`mark_used.py` を実行すると `used_seeds.txt` と `series_state.json` が更新されます。

## 方針

- 完全無料
- まずは連載1話分を2000字以上で下書き生成
- 同じネタの重複防止あり
- 前回あらすじと話数を引き継げる
