import csv
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "out"
OUT.mkdir(exist_ok=True)
CHAPTERS = OUT / "chapters"
CHAPTERS.mkdir(exist_ok=True)

SETTINGS = DATA / "settings.json"
SEEDS = DATA / "story_seeds.csv"
USED = DATA / "used_seeds.txt"
CHARACTERS = DATA / "characters.json"
STATE = DATA / "series_state.json"

MIN_BODY_LENGTH = 2000

ARC_RULES = {
    "序盤": {"max": 10, "mood": "謎を積み上げる", "focus": "異変の観察と街の違和感"},
    "中盤": {"max": 20, "mood": "不穏さを強める", "focus": "人間関係の揺れと隠された意図"},
    "終盤": {"max": 999, "mood": "回収を進める", "focus": "過去の事件との接続と真相への接近"},
}

OPENINGS = [
    "{place}では、夜が深くなるほど機械の音がよく響く。霧の向こうに隠れた工房の屋根は朝になっても鈍い色のままで、街の人間はその灰色を見慣れた空模様のように受け入れていた。けれど{chapter_label}の朝だけは、空気の流れまで何かを隠しているように重かった。",
    "{place}の朝は遅い。陽が差し込んでも石畳はすぐには温まらず、古い配管の奥で遅れて目を覚ましたような音が鳴る。{chapter_label}の始まりにふさわしくないほど静かな朝だったが、そういう朝に限って厄介な異変は見つかるものだった。",
    "その街では、静かな朝ほど何かが隠れている。{place}に暮らす人間は皆それを知っていて、だからこそ大きな声で不安を口にしない。沈黙の底に沈んだ違和感を拾うのは、いつだって一番忙しくて一番目立たない誰かだった。",
]
SCENE_SETUP = [
    "{name}は{role}として工房の鍵を開けながら、{hook}という噂を思い出していた。ただの噂として片づけるには妙に具体的で、誰に聞いても細部だけが少しずつ違う。その違いが逆に不気味だった。街の人は何かを見たのではなく、同じ種類の異常をそれぞれ別の角度から知っているのではないか。そんな考えが、朝の冷えた空気より先に胸の内側へ入り込んでいた。",
    "{name}は工具箱の留め具を確かめ、いつもの順番で作業台を整えた。手を動かしている間だけは余計な考えを脇に置けるはずだったが、{hook}という噂が頭の隅から離れない。職人見習いとして一日を始めるだけなら十分な朝のはずなのに、今日はまだ何も起きていない段階で、すでに歯車が一枚ずれているような感覚があった。",
]
INCITING_LINES = [
    "その日も異変は小さく始まった。{seed}。最初に聞いた瞬間は誰かの見間違いか、古い機械らしい気まぐれのようにも思えた。だが細部をたどるほど、単なる偶然にしては説明のつかない整い方をしている。",
    "朝の仕事が一段落したころ、{seed}という話が持ち込まれた。よくある故障報告なら作業伝票の一枚で済む。けれど今回は違った。話し手は自分でも何が異常なのか説明しきれない顔をしていて、その曖昧さがむしろ本物の不気味さを連れてきた。",
]
INVESTIGATION_LINES = [
    "{name}は違和感を見過ごせず、ひとまず記録を取ることにした。時間、場所、音、匂い、周囲にいた人の名前。師匠に鍛えられてきたせいか、異常を見た瞬間よりも、後から振り返ったときに役立つ細部のほうが先に気になる。現場へ向かう途中、街路の端で朝露を弾く金属片が目に入り、それがなぜか今回の件と無関係ではないように思えた。",
    "{name}は仕事を続けるふりをしながら、妙な点を一つずつ頭の中で並べていった。異変そのものより、それを見た人間の口ぶりが揃いすぎている。驚いているようで、どこか諦めたようでもある。その温度感は、初めて起きた出来事ではなく、以前にも似たものがあったときの反応に近かった。",
]
MENTOR_LINES = [
    "師匠の{mentor_name}は、いつもなら一言で指示を出すのに、この件になると道具箱の整理ばかり気にしていた。無関心を装っているのか、逆に気づかれたくないのか、その境目が見えない。{name}は問いただすかわりに横顔を観察した。古い傷のある指先が、必要以上に几帳面な動きで部品を並べ替えている。",
    "{mentor_name}は露骨に話題を変えたわけではない。ただ、異変の細部に触れた瞬間だけ、返事の間がわずかに長くなった。長年同じ工房で働く者でなければ気づけないほど小さな違和感だが、{name}にとっては十分だった。その沈黙は、知らないのではなく知っていて伏せている人間の沈黙だった。",
]
MENTOR_DIALOGUES = [
    "「その話はあとにしろ」\n\n{mentor_name}は顔を上げずに言った。\n\n「今朝のうちに片づける仕事がある」\n\n短い言い方だったが、追及を嫌っていることは十分に伝わった。",
    "「気にするなと言っても無理か」\n\n{mentor_name}は工具を拭きながら、小さく息をついた。\n\n「だが、見たものをすぐ口に出すな。街はそういう場所じゃない」\n\n忠告というより、昔から自分に言い聞かせてきた言葉のように聞こえた。",
]
LIBRARY_LINES = [
    "昼過ぎ、{name}は街の記録を調べるために図書館へ向かった。司書の{librarian_name}は薄い紙束を束ね直しながら、表向きは何でもない顔をしていたが、古い記録棚の前に立つときだけ視線の動きが慎重になる。過去の事故や異変は、街では忘れられるのではなく、誰かが見つけにくい場所へしまい込んでいるのだと感じられた。",
    "{name}が図書館の記録室へ足を踏み入れると、古紙の匂いと油のにおいが混ざっていた。工房の街らしい匂いだと一瞬思ったが、図書館に機械油の残り香があるのはおかしい。司書の{librarian_name}はその指摘に驚かなかった。むしろ、ようやく気づいたのかという目で棚の奥を一度だけ見た。",
]
LIBRARY_DIALOGUES = [
    "「記録は残っています。ただし、見つけにくくしてあるだけです」\n\n{librarian_name}は薄い帳面を閉じ、真琴をまっすぐ見た。\n\n「誰かが隠したのではなく、誰も見たがらなかった結果かもしれません」\n\nその静かな言い方が、かえって重かった。",
    "「あなたが探しているのは故障の記録ではありませんね」\n\n{librarian_name}は棚の奥へ手を伸ばしながら言った。\n\n「故障のふりをしたもの、そのほうでしょう」\n\n真琴は答えず、代わりに差し出された古い台帳を受け取った。",
]
SENSORY_LINES = [
    "地下へ向かう通路は昼でも薄暗く、壁に染みこんだ油のにおいが靴音にまでまとわりついてくる。遠くで水滴が落ちるたび、金属の反響が少し遅れて返ってきた。",
    "石畳の継ぎ目にはまだ朝の湿り気が残っていた。指先で手すりに触れるとひやりと冷たく、その感触だけで人の少ない場所へ来たことが分かる。",
    "街の機械音はいつもなら背景に溶けるのに、その日は妙に輪郭がはっきりしていた。回転音の合間に混ざる沈黙までが、誰かの意図のように思えた。",
]
REACTION_LINES = [
    "真琴はすぐに返事をしなかった。理解が追いつかなかったというより、言葉にした瞬間に曖昧な違和感がただの感想へ変わってしまう気がしたからだ。",
    "喉の奥まで出かかった問いを、真琴はいったん飲み込んだ。急いで答えを取ろうとすると、この街のものは決まって形を変える。",
    "その場で結論を出すには材料が足りない。けれど、見逃していい気配ではないことだけは、皮膚の内側が先に理解していた。",
]
TWIST_LINES = [
    "手がかりは単純ではない。{twist}。その事実は、異変をただの故障から切り離し、誰かの意思が介在した出来事へ変えてしまう。事故や偶然ならば不揃いであるはずの痕跡が、今回は妙なほど整っていた。整いすぎているものは、たいてい自然には生まれない。",
    "{twist}。その一点だけで、{name}の見立ては大きく変わった。壊れた結果として残った跡ではなく、ある結末へ導くために配置された跡だと考えるほうが筋が通る。問題は誰が、何のために、街の片隅でそんな手間をかけているのかということだった。",
]
INNER_LINES = [
    "{name}は、自分が知りたいのは異変の犯人だけではないのだと気づき始めていた。なぜ街の人たちがこれほど静かに振る舞うのか。なぜ噂は広がるのに、核心に触れた記録だけが欠けているのか。工房都市で起きる小さな異変の真相を追うという自分の目的は、いつの間にか街の沈黙そのものに向かっていた。",
    "怖さがないわけではない。けれど{name}にとって本当に厄介なのは恐怖ではなく、曖昧なまま放置された違和感だった。正体が分からないことより、誰も正体を知ろうとしていないことのほうが、ずっと気味が悪い。だからこそ手を引く理由が見つからない。",
]
REVEAL_LINES = [
    "そこで見つかったのは故障ではなく、誰かが残した意図そのものだった。部品の摩耗の仕方、油の拭き取り跡、目立たない位置に刻まれた印。そのどれもが、偶然では説明しにくい方向へそろっている。街の異変は自然発生ではなく、誰かに繰り返し観測され、あるいは再現されているのかもしれなかった。",
    "現場に残っていたのは事故の痕跡ではなく、再現のための準備だった。まるで同じ出来事を何度も起こすことで、誰かが何かを確かめようとしているようだった。{name}はその発想に寒気を覚えたが、同時に初めて輪郭のある敵の存在を感じた。",
    "異変の中心にあったのは壊れた機械ではなく、人の記憶に関わる仕掛けだった。物が壊れるだけなら直せば済む。だが記憶や証言の形まで誘導されているなら、街全体が少しずつ同じ方向へずらされている可能性がある。",
]
CLOSING_LINES = [
    "その夜、{name}は街の異変が一度きりでは終わらないと確信する。工房の窓を閉めたあとも、朝に見たわずかな違和感が胸の中で金属片のように重く残っていた。答えはまだ遠い。それでも、今日得た手がかりが次の扉を開く鍵になることだけははっきりしていた。",
    "{name}は答えに近づいた気がしたが、同時にもっと大きな秘密の存在にも気づく。街の一件一件を別々の出来事として扱う限り、真相には届かない。ばらばらに見える異変の奥で、同じ手つきがずっと続いている。その確信だけを持って、{name}は明日の朝を待つことにした。",
    "真相はまだ遠い。それでも{name}は、次に止まる時計を待つことにした。待つというより、今度は先に見つけに行くつもりだった。街の静けさの中には、耳を澄ませた者にしか聞こえない予兆がある。今日ようやく、その聞き方の入口に立てた気がしていた。",
]
ARC_EXPANSIONS = {
    "序盤": [
        "まだ答えよりも疑問のほうが多い。だからこそ、真琴は今のうちに街の小さな違和感を一つずつ集めておくべきだと考えた。大きな真相は、たいてい最初に見逃された細部の中から立ち上がる。",
        "序盤で大事なのは、答えを急がないことだ。真琴はそう自分に言い聞かせながら、目の前の異変を街全体の地図の中に置いて考えようとした。点のままでは意味を持たない出来事も、線で結べば別の顔を見せる。",
    ],
    "中盤": [
        "ここから先は、異変そのものより人の沈黙のほうが重くなっていく。真琴は記録を追うほど、隠されているのが事実だけではなく、誰がどこまで知っているかという関係そのものだと感じ始めていた。街は秘密を守っているのではなく、秘密を抱えたまま動き続けている。",
        "中盤に入った今、真琴の前には手がかりだけでなく選択肢も増え始めていた。誰を信じるか、どこまで問い詰めるか、何を見たことにして何を見なかったことにするか。その判断一つで、真相への道筋も人との距離も変わってしまう。",
    ],
    "終盤": [
        "終盤に近づくにつれ、過去に拾った違和感はばらばらな記録ではなく、同じ設計図の断片のように見え始める。真琴が今向き合っているのは新しい謎ではなく、ずっと前から街に置かれていた問いの続きなのかもしれなかった。",
        "回収の段階では、新しい情報そのものより、既に知っていた事実の意味が変わることのほうが大きい。真琴は今日見つけた手がかりを胸の中で反転させながら、これまでの出来事が一つの輪郭へ収束していく気配を感じていた。",
    ],
}
ARC_CATEGORY_HINTS = {
    "序盤": {"導入", "人物", "秘密"},
    "中盤": {"事件", "対立", "秘密"},
    "終盤": {"回収", "秘密", "事件"},
}
WATCHER_LINES = [
    "{watcher_name}はその場にいなかったはずなのに、後から振り返ると最初から近くに視線だけ置いていたように思える人物だった。街の仕組みを守る側なのか、壊さないよう監視する側なのか、その立ち位置はまだ読めない。ただ一つ言えるのは、真琴が手がかりを拾うたびに、その人物の影もまた濃くなるということだった。",
    "{watcher_name}という名は記録にも会話にも頻繁には出てこない。だが工房組合の決定や街の検査記録を辿ると、いつも最後にその名前が静かに残っている。表では穏やかに微笑み、裏では流れを止める。そういう人間が一人いるだけで、街の空気は驚くほど変わる。",
]
WATCHER_DIALOGUES = [
    "「記録は残したほうがいい。ただし、残し方を間違えると街のためにならない」\n\n灰島は柔らかな声でそう言った。\n\n脅しには聞こえない。だからこそ、真琴は余計に警戒した。",
    "「君はよく見ている。だが、見えたもの全部に名前を付ける必要はない」\n\n灰島はそう言って微笑んだ。\n\n穏やかな言い方なのに、後ろへ半歩下がりたくなる種類の声だった。",
]
THREAD_LINES = [
    "真琴の頭から離れない未回収の問いは、{thread}だった。今回の異変もその線上に置いてみると、偶然では説明しにくい位置でつながり始める。",
    "まだ片づいていない問題として残っているのは、{thread}だ。目の前の異変だけを追うより、その糸がどこへ続いているかを見失わないことのほうが重要になりつつある。",
]
ANTAGONIST_LINES = [
    "真琴は最近、{antagonist}という名前を考える回数が増えていた。姿を見ない日でも、その人物の判断だけが先に街へ届いているように感じる。",
    "直接対立したわけではない。それでも{antagonist}の存在は、真琴にとって次第に街のルールそのもののように重くなっていた。",
]


def load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_used_ids() -> set[str]:
    if not USED.exists():
        return set()
    with open(USED, encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip()}


def load_unused_seed() -> dict[str, str]:
    used = load_used_ids()
    with open(SEEDS, encoding="utf-8") as f:
        rows = [row for row in csv.DictReader(f) if row["seed_id"] not in used]
    if not rows:
        raise RuntimeError("No unused story seeds left. Add more rows to story_seeds.csv.")
    return random.choice(rows)


def get_arc(chapter_number: int) -> str:
    for arc_name, rule in ARC_RULES.items():
        if chapter_number <= rule["max"]:
            return arc_name
    return "終盤"


def choose_seed_for_arc(chapter_number: int) -> dict[str, str]:
    used = load_used_ids()
    arc = get_arc(chapter_number)
    with open(SEEDS, encoding="utf-8") as f:
        rows = [row for row in csv.DictReader(f) if row["seed_id"] not in used]
    if not rows:
        raise RuntimeError("No unused story seeds left. Add more rows to story_seeds.csv.")

    preferred = [row for row in rows if row["category"] in ARC_CATEGORY_HINTS[arc]]
    return random.choice(preferred or rows)


def build_character_notes(characters: list[dict]) -> list[str]:
    lines = ["## 登場人物メモ", ""]
    for character in characters:
        lines.append(f"- {character['name']}: {character['role']} / {character['trait']} / 目的: {character['goal']}")
    return lines


def build_summary(protagonist_name: str, seed: dict[str, str]) -> str:
    return (
        f"{protagonist_name}は{seed['seed']}という異変に向き合い、"
        f"{seed['twist']}という新しい手がかりを得た。"
    )


def build_body(settings: dict, seed: dict[str, str], characters: list[dict], state: dict) -> list[str]:
    protagonist = settings["protagonist"]
    place = settings["setting"]["place"]
    hook = settings["setting"]["hook"]
    chapter_number = state["next_chapter"]
    chapter_label = f"第{chapter_number}話"
    arc = get_arc(chapter_number)
    mentor = next((c for c in characters if "師匠" in c["role"]), characters[0])
    librarian = next((c for c in characters if "司書" in c["role"]), characters[-1])
    watcher = next((c for c in characters if "監査役" in c["role"]), characters[-1])

    body = [
        random.choice(OPENINGS).format(place=place, chapter_label=chapter_label),
        random.choice(SCENE_SETUP).format(
            name=protagonist["name"],
            role=protagonist["role"],
            hook=hook,
        ),
        random.choice(INCITING_LINES).format(seed=seed["seed"]),
        random.choice(SENSORY_LINES),
        random.choice(INVESTIGATION_LINES).format(name=protagonist["name"]),
        random.choice(MENTOR_LINES).format(name=protagonist["name"], mentor_name=mentor["name"]),
        random.choice(MENTOR_DIALOGUES).format(mentor_name=mentor["name"]),
        random.choice(REACTION_LINES),
        random.choice(LIBRARY_LINES).format(name=protagonist["name"], librarian_name=librarian["name"]),
        random.choice(LIBRARY_DIALOGUES).format(librarian_name=librarian["name"]),
        random.choice(TWIST_LINES).format(name=protagonist["name"], twist=seed["twist"]),
        random.choice(INNER_LINES).format(name=protagonist["name"]),
        f"{protagonist['name']}の目的は{protagonist['goal']}ことだが、今回の出来事はその入口にすぎなかった。異変一つを追うだけなら修理工見習いの仕事の範囲を超えている。けれど街の異常が工房の仕事と日常の境目を少しずつ侵食している以上、もう見て見ぬふりでは済まない。自分の仕事を守るためにも、働く場所そのものを疑う必要が出てきていた。",
        random.choice(REVEAL_LINES).format(name=protagonist["name"]),
        random.choice(ARC_EXPANSIONS[arc]),
        random.choice(CLOSING_LINES).format(name=protagonist["name"]),
    ]

    if state.get("open_threads"):
        body.insert(3, random.choice(THREAD_LINES).format(thread=random.choice(state["open_threads"])))

    if state.get("current_antagonist"):
        body.insert(4, random.choice(ANTAGONIST_LINES).format(antagonist=state["current_antagonist"]))

    if arc != "序盤":
        body.insert(-2, random.choice(WATCHER_LINES).format(watcher_name=watcher["name"]))
        body.insert(-2, random.choice(WATCHER_DIALOGUES))

    return body


def build_chapter(settings: dict, seed: dict[str, str], characters: list[dict], state: dict) -> tuple[str, str]:
    protagonist = settings["protagonist"]
    chapter_number = state["next_chapter"]
    arc = get_arc(chapter_number)
    summary = build_summary(protagonist["name"], seed)
    body = build_body(settings, seed, characters, state)

    paragraphs = [
        f"# 第{chapter_number}話",
        "",
    ]

    if state["last_summary"]:
        paragraphs.extend(["前回までのあらすじ", "", state["last_summary"], ""])

    paragraphs.extend(body)

    chapter = "\n\n".join(paragraphs) + "\n"

    if len(chapter) < MIN_BODY_LENGTH:
        extra = (
            f"{protagonist['name']}はその日の記録をノートにまとめながら、"
            f"今日見た異変が単独の事件ではなく、街の仕組みそのものに触れている可能性を考え続けた。"
            f"分かったことはまだ少ない。それでも、何が分かっていないのかを言葉にできるだけ前より進んでいる。"
            f"工房都市では、沈黙しているものほど長く残る。だからこそ、沈黙の理由を追う者が必要なのだと、"
            f"{protagonist['name']}はようやく自分の役割を理解し始めていた。"
        )
        chapter += "\n" + extra + "\n"

    return chapter, summary


def main() -> None:
    settings = load_json(SETTINGS)
    characters = load_json(CHARACTERS)
    state = load_json(STATE)
    arc = get_arc(state["next_chapter"])
    seed = choose_seed_for_arc(state["next_chapter"])
    chapter, summary = build_chapter(settings, seed, characters, state)

    latest = OUT / "chapter_latest.md"
    meta = OUT / "chapter_meta.json"
    chapter_file = CHAPTERS / f"chapter_{state['next_chapter']:03d}.md"

    latest.write_text(chapter, encoding="utf-8")
    chapter_file.write_text(chapter, encoding="utf-8")
    meta.write_text(
        json.dumps(
            {
                **seed,
                "chapter_number": state["next_chapter"],
                "summary": summary,
                "character_count": len(chapter),
                "arc": arc,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"Generated chapter with seed {seed['seed_id']}")
    print(f"Characters: {len(chapter)}")
    print(latest)


if __name__ == "__main__":
    main()
