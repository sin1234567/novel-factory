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
LIBRARY_LINES = [
    "昼過ぎ、{name}は街の記録を調べるために図書館へ向かった。司書の{librarian_name}は薄い紙束を束ね直しながら、表向きは何でもない顔をしていたが、古い記録棚の前に立つときだけ視線の動きが慎重になる。過去の事故や異変は、街では忘れられるのではなく、誰かが見つけにくい場所へしまい込んでいるのだと感じられた。",
    "{name}が図書館の記録室へ足を踏み入れると、古紙の匂いと油のにおいが混ざっていた。工房の街らしい匂いだと一瞬思ったが、図書館に機械油の残り香があるのはおかしい。司書の{librarian_name}はその指摘に驚かなかった。むしろ、ようやく気づいたのかという目で棚の奥を一度だけ見た。",
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
    chapter_label = f"第{state['next_chapter']}話"
    mentor = next((c for c in characters if "師匠" in c["role"]), characters[0])
    librarian = next((c for c in characters if "司書" in c["role"]), characters[-1])

    return [
        random.choice(OPENINGS).format(place=place, chapter_label=chapter_label),
        random.choice(SCENE_SETUP).format(
            name=protagonist["name"],
            role=protagonist["role"],
            hook=hook,
        ),
        random.choice(INCITING_LINES).format(seed=seed["seed"]),
        random.choice(INVESTIGATION_LINES).format(name=protagonist["name"]),
        random.choice(MENTOR_LINES).format(name=protagonist["name"], mentor_name=mentor["name"]),
        random.choice(LIBRARY_LINES).format(name=protagonist["name"], librarian_name=librarian["name"]),
        random.choice(TWIST_LINES).format(name=protagonist["name"], twist=seed["twist"]),
        random.choice(INNER_LINES).format(name=protagonist["name"]),
        f"{protagonist['name']}の目的は{protagonist['goal']}ことだが、今回の出来事はその入口にすぎなかった。異変一つを追うだけなら修理工見習いの仕事の範囲を超えている。けれど街の異常が工房の仕事と日常の境目を少しずつ侵食している以上、もう見て見ぬふりでは済まない。自分の仕事を守るためにも、働く場所そのものを疑う必要が出てきていた。",
        random.choice(REVEAL_LINES).format(name=protagonist["name"]),
        random.choice(CLOSING_LINES).format(name=protagonist["name"]),
    ]


def build_chapter(settings: dict, seed: dict[str, str], characters: list[dict], state: dict) -> tuple[str, str]:
    protagonist = settings["protagonist"]
    chapter_number = state["next_chapter"]
    summary = build_summary(protagonist["name"], seed)
    body = build_body(settings, seed, characters, state)

    paragraphs = [
        f"# {settings['title']} 第{chapter_number}話下書き",
        "",
        f"ジャンル: {settings['genre']}",
        f"雰囲気: {settings['tone']}",
        f"目標文字数: {settings['style']['chapter_length']}",
        "",
    ]

    if state["last_summary"]:
        paragraphs.extend(["## 前回までの流れ", "", state["last_summary"], ""])

    paragraphs.extend(build_character_notes(characters))
    paragraphs.extend(["", "## 本文", ""])
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
    seed = load_unused_seed()
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
