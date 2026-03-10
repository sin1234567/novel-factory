import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "out"
CHAPTERS = OUT / "chapters"
OUT.mkdir(exist_ok=True)
CHAPTERS.mkdir(exist_ok=True)

SETTINGS = DATA / "settings.json"
CHARACTERS = DATA / "characters.json"
OUTLINE = DATA / "long_story_outline.csv"
STATE = DATA / "series_state.json"
META = OUT / "chapter_meta.json"
MANUSCRIPT = OUT / "full_manuscript.md"

TARGET_EPISODES = 40

OPENERS = {
    "導入": [
        "{place}では、異変はいつも工具より先に噂として届く。真琴は工房の扉を開けた瞬間、その朝の空気が昨日よりひとつ重いことに気づいた。",
        "{place}の朝は遅い。陽が石畳へ落ちても温度はすぐに上がらず、街はまだ夜の秘密を抱えたままの顔をしていた。",
    ],
    "中盤": [
        "{place}で何かを調べるということは、誰かの沈黙に手をかけることでもある。真琴はもう、その手触りから逃げられなくなっていた。",
        "街の異変は記録の上では別々に見える。だが真琴の中では、すでに同じ地下水脈から湧いた出来事のように重なり始めていた。",
    ],
    "終盤": [
        "ここまで来ると、真琴が見ているのは新しい異変ではなく、ずっと街の底で回り続けてきた仕掛けの全景だった。",
        "終わりが近づくほど、街は静かになる。派手な音が消える代わりに、隠されてきた因果だけがくっきりと輪郭を持ち始めていた。",
    ],
}

TRANSITIONS = [
    "真琴は現場へ向かう途中で、会話の切れ目や道具の置かれ方まで注意して見た。異変は結果だけでなく、そこへ至る順番にこそ人の意思が残る。",
    "工房を出るころには、噂だけが先に街路を走っていた。大声で騒ぐ者は少ないのに、誰もが『見ないふりの仕方』だけはよく知っているようだった。",
    "足元の石畳、壁に残る油の筋、止まった視線。真琴は今回も、物より先に配置の不自然さから追うことにした。",
]

DIALOGUES = [
    "「順番は誰かが作れる」\n\n志乃は短くそう言って、工具箱の蓋を閉じた。\n\n「見えたままを並べるだけじゃ、街の都合に負ける」",
    "「記録は消える。でも消し方には癖が残るんです」\n\n白崎は台帳の余白を指でなぞりながら言った。\n\n「だから、本当に見るべきなのは本文じゃなく欠けた場所なんですよ」",
    "「君は見すぎる」\n\n灰島は穏やかに言った。\n\n「だが、ここで見たもの全部を外へ持ち出せば、街そのものが壊れる」",
]

REFLECTIONS = [
    "真琴は、自分が追っているのが一つの故障ではないと何度でも思い知らされる。時計、地下通路、設計図、帳簿、名簿。ばらばらな出来事のふりをしながら、どれも同じ中心を隠していた。",
    "異変に慣れた街で、慣れきれないまま立っていること。それ自体が、いつの間にか真琴の役目になり始めていた。",
    "調べるほど、街は秘密を隠しているというより、秘密ごと動くように設計されているとしか思えなくなる。ならば必要なのは解決より先に、構造を見抜く目だった。",
]

ENDINGS = [
    "その日、真琴は記録帳の余白へ短い一文だけを書き足した。今日つかんだ断片はまだ弱い。だが弱いままでも、次の扉の蝶番にはなり得る。",
    "工房へ戻る道で、真琴は何度も今日の順番を頭の中で並べ直した。答えより先に、次にどこを見るべきかだけがはっきりしていく。",
    "夜の街は静かだったが、真琴にはそれが終わりの静けさではなく、次の異変が息を潜めている静けさに思えた。",
]


def load_json(path: Path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_outline() -> list[dict[str, str]]:
    with open(OUTLINE, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def build_scene_block(index: int, row: dict[str, str], settings: dict, characters: list[dict]) -> str:
    place = settings["setting"]["place"]
    mentor = next(c for c in characters if c["name"] == "志乃")
    librarian = next(c for c in characters if c["name"] == "白崎")
    watcher = next(c for c in characters if c["name"] == "灰島")

    opener = OPENERS[row["arc"]][index % len(OPENERS[row["arc"]])].format(place=place)
    transition = TRANSITIONS[index % len(TRANSITIONS)]
    reflection = REFLECTIONS[index % len(REFLECTIONS)]
    ending = ENDINGS[index % len(ENDINGS)]
    dialogue = DIALOGUES[index % len(DIALOGUES)]

    scene_a = (
        f"{opener} 真琴はその朝、{row['focus']}に関わる違和感を道具の重さより先に意識していた。"
        f"{row['incident']}という報告は、一見すると小さな故障や偶然の延長に見える。"
        f"けれど実際には、街の人間が出来事そのものより『どう受け止めるか』を先に決めているような、不自然な整い方をしていた。 "
        f"{transition} 真琴は、ただ壊れたものを直すのでは足りないと分かっていた。"
    )
    scene_mid = (
        f"現場に近づくにつれ、真琴は街の沈黙の質が少しずつ変わっていくのを感じた。"
        f" 工具を持つ手は止まらないのに、視線だけが妙に早く逸らされる。"
        f" 誰も真琴を露骨には避けない。だが、{row['incident']}に触れた話題だけが、決まって半歩ぶん浅いところで切り上げられていた。"
        f" その不自然さは、現象そのものよりもむしろ街のほうが先に異変へ慣れようとしている証拠に見えた。"
    )
    scene_work = (
        f"真琴は修理工見習いとして叩き込まれてきた手順を守りながら、目の前の痕跡を一つずつ書き留めた。"
        f" 音のした位置、油の乾き方、部品の向き、報告した人間の言い淀み。"
        f" 志乃は『壊れ方には癖がある』と言っていたが、真琴には最近、その癖が機械より人のほうに濃く出ているように思えた。"
        f" 誰かが長い時間をかけて街の見え方を調整してきたのだとすれば、修理の対象は部品ではなく順番そのものなのかもしれない。"
    )

    if row["arc"] == "導入":
        scene_b = (
            f"昼過ぎ、真琴は{librarian['name']}のいる記録室で古い台帳を開き、{row['discovery']}という事実に辿り着く。"
            f" その一点が加わった瞬間、{row['incident']}は単独の異変ではなく、地下工房と大火災の記録を結ぶ線の上へ置き直された。"
            f" {dialogue} {reflection} {ending} 次に真琴を動かしたのは、{row['cliffhanger']}という小さくも決定的な選択だった。"
        )
        scene_c = (
            f"{librarian['name']}は、本文より余白を見ろと真琴に言った。"
            f" 消されるものには、消し方の癖が残る。残された記録より、わざわざ欠かれた記録のほうに街の本音が出ることもある。"
            f" 真琴は台帳の欠落や朱線の引かれ方を追ううち、{row['discovery']}がたまたま見つかった事実ではなく、"
            f" 誰かが見つかることを恐れながらも完全には消しきれなかった事実なのだと理解した。"
        )
    elif row["arc"] == "中盤":
        scene_b = (
            f"{mentor['name']}は必要なところだけ妙に短くうなずき、{watcher['name']}は姿を見せないまま規則や署名で先回りしてきた。"
            f" その挟み撃ちの中で、真琴は{row['discovery']}という事実を掴む。"
            f" それは証拠であると同時に、街の沈黙が誰によって保たれてきたかを示す印でもあった。"
            f" {dialogue} {reflection} {ending} そして真琴は、{row['cliffhanger']}という次の行動へ踏み出すしかないと悟った。"
        )
        scene_c = (
            f"この頃になると、真琴は異変を追うこと自体が誰かの監視の中へ入る行為だと知っていた。"
            f" {watcher['name']}の名前は会話に頻繁には出ない。だが提出日、閲覧制限、夜間外出証、検査の時刻といった形で、"
            f" 常に真琴の半歩先へ規則が置かれている。{row['discovery']}という事実は、ただ謎を深めるだけでなく、"
            f" その規則がどこから街へ降ろされているかを示す座標にもなっていた。"
        )
    else:
        scene_b = (
            f"{librarian['name']}が守ってきた台帳、{mentor['name']}が燃やしてきた手紙、{watcher['name']}が押し通してきた規則は、"
            f"ここでようやく同じ仕掛けの別の面だったと分かる。{row['discovery']}という事実は、"
            f"{row['incident']}の意味を逆から照らし返した。 {dialogue} {reflection} {ending}"
            f" それでも物語はそこで閉じず、真琴の前には{row['cliffhanger']}という最後の仕事が残った。"
        )
        scene_c = (
            f"終盤に入ってからの真琴は、異変を一件ずつ追うのではなく、散らばっていた断片の意味がどう反転するかを見るようになっていた。"
            f" 火災の名簿、地下工房、停止手順、監査印、設計図。{row['discovery']}によって一つの線がつながるたび、"
            f" それまで説明不能だった沈黙の理由も別の顔を見せ始める。街は壊れたまま放置されてきたのではない。"
            f" 壊れた状態を保つよう継続的に調整されてきたのだと、真琴はもう疑っていなかった。"
        )

    scene_d = (
        f"真琴は工房へ戻る道で、今日拾った言葉と痕跡を何度も並べ直した。"
        f" {row['incident']}の意味は、見つけた瞬間より、半日遅れて胸に沈む。"
        f" それはいつも次の行動と一緒にやって来る。今回は{row['cliffhanger']}が、その形だった。"
        f" 街を相手にする以上、一つの真相で何かが終わることはない。だが、終わらないからこそ、"
        f" いまここで取り落としてはならない断片がある。真琴はそれを抱えたまま、次の朝へ進むことを選んだ。"
    )
    scene_e = (
        f"夜になるころ、真琴は作業台の上へ記録帳、写し取った図面、切れた封印、控えの紙片を順に広げた。"
        f" ひとつずつ見れば取るに足らない断片でも、同じ机の上へ並べた瞬間に関係の匂いが立ち上がる。"
        f" {row['incident']}と{row['discovery']}は、出来事と手がかりというより、街の底で長く噛み合っていた歯車の表と裏のようだった。"
        f" 真琴はそこに志乃の沈黙、白崎の保存癖、灰島の規則がどう重なっているかを考え、"
        f" 誰が何を守ろうとしているのかを機械ではなく人の配置から読み解こうとした。"
        f" 工房都市では、壊れたものより壊れたまま残されているもののほうが雄弁だ。"
        f" だからこそ真琴は、修理の手を止めてでも、その『残され方』を見届ける必要があると確信していた。"
    )
    scene_f = (
        f"窓の外では、塔の時計も地下の通風孔も、何事もなかったように街の夜へ溶け込んでいた。"
        f" だが真琴には、その平穏こそが最も不自然に見える。{row['focus']}をめぐって今日拾った違和感は、"
        f" 明日になれば別の顔で街のどこかへ現れるはずだった。真琴は椅子にもたれ、"
        f" 自分が追っているのが犯人探しだけではなく、『この街がどんな理屈で壊れた状態を維持してきたのか』という問いだと再確認した。"
        f" その問いに答えるには、一件ずつ解決した気になることより、長く続いてきた連なりを見失わないことのほうが重要だった。"
        f" だから真琴は、その夜も記録を閉じる前に、次の朝へつながる印だけは必ず残しておくことにした。"
    )

    return "\n\n".join([scene_a, scene_mid, scene_work, scene_b, scene_c, scene_d, scene_e, scene_f])


def main() -> None:
    settings = load_json(SETTINGS)
    characters = load_json(CHARACTERS)
    outline = load_outline()

    manuscript_sections: list[str] = []
    for index, row in enumerate(outline):
        manuscript_sections.append(build_scene_block(index, row, settings, characters))

    MANUSCRIPT.write_text("\n\n".join(manuscript_sections) + "\n", encoding="utf-8")

    for idx, body in enumerate(manuscript_sections, start=1):
        chapter_text = f"# 第{idx}話\n\n{body.strip()}\n"
        (CHAPTERS / f"chapter_{idx:03d}.md").write_text(chapter_text, encoding="utf-8")

    latest_text = (CHAPTERS / "chapter_040.md").read_text(encoding="utf-8")
    (OUT / "chapter_latest.md").write_text(latest_text, encoding="utf-8")
    META.write_text(
        json.dumps(
            {
                "episode_count": TARGET_EPISODES,
                "last_episode": TARGET_EPISODES,
                "character_count": len(latest_text),
                "mode": "full_manuscript_split",
                "manuscript_path": str(MANUSCRIPT),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    state = load_json(STATE)
    state["next_chapter"] = TARGET_EPISODES + 1
    state["last_summary"] = "真琴は再現装置停止後の街に残る修理を引き受け、灰島の残した記録を次の世代へ渡す準備を始めた。"
    state["last_seed_id"] = "MANUSCRIPT40"
    state["last_seed"] = "長編原稿から40話へ分割済み"
    state["current_antagonist"] = "灰島"
    state["open_threads"] = [
        "停止後の地下工房に再起動の兆候はないか",
        "灰島の残した監査記録は公開されるのか",
        "志乃の沈黙で守られていた人物は他にもいるのか",
        "白崎の台帳に続編へつながる空白は残るのか",
        "真琴は街に残りどこまで修理を引き受けるのか",
    ]
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Generated full manuscript and split into {TARGET_EPISODES} episodes.")


if __name__ == "__main__":
    main()
