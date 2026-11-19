import random

import streamlit as st

st.set_page_config(page_title="풍선과 괴물 나라", page_icon="🎈", layout="wide")

# ---------------------------------------------------------------
# 데이터
# ---------------------------------------------------------------
HEROES = {
    "🧙 마법사 루미": {"emoji": "🧙", "hp": 80, "atk": (12, 30), "desc": "별빛 마법을 쓰는 꼬마 마법사"},
    "🤖 로봇 볼트": {"emoji": "🤖", "hp": 120, "atk": (8, 18), "desc": "느리지만 아주 튼튼한 로봇"},
    "🦸 영웅 한별": {"emoji": "🦸", "hp": 100, "atk": (10, 24), "desc": "망토를 두른 동네 영웅"},
    "🧚 요정 티나": {"emoji": "🧚", "hp": 70, "atk": (15, 34), "desc": "작지만 가장 매서운 요정"},
    "🐱 고양이 나비": {"emoji": "🐱", "hp": 90, "atk": (9, 28), "desc": "발톱이 날카로운 길고양이 검객"},
}

MONSTERS = [
    {"name": "픽셀 침략자", "emoji": "👾", "hp": 60, "atk": (4, 10)},
    {"name": "장난꾸러기 유령", "emoji": "👻", "hp": 50, "atk": (5, 12)},
    {"name": "붉은 도깨비", "emoji": "👹", "hp": 90, "atk": (6, 14)},
    {"name": "졸린 좀비", "emoji": "🧟", "hp": 70, "atk": (3, 9)},
    {"name": "불꽃 용", "emoji": "🐲", "hp": 130, "atk": (8, 18)},
    {"name": "외계 문어", "emoji": "🐙", "hp": 80, "atk": (5, 13)},
]

# ---------------------------------------------------------------
# 움직이는 배경: 떠오르는 풍선, 걸어다니는 괴물과 캐릭터
# ---------------------------------------------------------------
random.seed(7)  # 새로 그려져도 배치가 바뀌지 않도록 고정
balloons_html = "".join(
    f'<span class="balloon" style="left:{random.randint(0, 96)}%;'
    f"font-size:{random.randint(28, 60)}px;"
    f"animation-duration:{random.randint(9, 20)}s;"
    f"animation-delay:-{random.randint(0, 20)}s;"
    f'filter:hue-rotate({random.randint(0, 360)}deg);">🎈</span>'
    for _ in range(18)
)
walkers_html = "".join(
    f'<span class="walker {"reverse" if i % 2 else ""}" style="bottom:{4 + (i % 3) * 5}px;'
    f"font-size:{random.randint(34, 54)}px;"
    f"animation-duration:{random.randint(14, 30)}s;"
    f'animation-delay:-{random.randint(0, 30)}s;">{emoji}</span>'
    for i, emoji in enumerate("👾👻👹🧟🐲🐙🤖🧙🦸🧚🐱🦄")
)
random.seed()

st.html(
    f"""
    <style>
      .stApp {{
        background: linear-gradient(180deg, #a8e0ff 0%, #d9f2ff 55%, #fff3d6 100%);
      }}
      .sky {{ position: fixed; inset: 0; pointer-events: none; overflow: hidden; z-index: 0; }}
      .balloon {{ position: absolute; bottom: -80px; opacity: .85;
                 animation: rise linear infinite; }}
      .walker {{ position: absolute; left: -80px; animation: walk linear infinite; }}
      .walker.reverse {{ animation-name: walk-back; }}
      @keyframes rise {{
        0%   {{ transform: translate(0, 0) rotate(-6deg); }}
        50%  {{ transform: translate(30px, -60vh) rotate(6deg); }}
        100% {{ transform: translate(-10px, -120vh) rotate(-6deg); }}
      }}
      @keyframes walk {{
        0%   {{ transform: translateX(0) translateY(0); }}
        25%  {{ transform: translateX(27vw) translateY(-10px); }}
        50%  {{ transform: translateX(55vw) translateY(0); }}
        75%  {{ transform: translateX(82vw) translateY(-10px); }}
        100% {{ transform: translateX(110vw) translateY(0); }}
      }}
      @keyframes walk-back {{
        0%   {{ transform: translateX(110vw) scaleX(-1); }}
        50%  {{ transform: translateX(55vw) translateY(-10px) scaleX(-1); }}
        100% {{ transform: translateX(0) scaleX(-1); }}
      }}
      @keyframes bob {{
        0%, 100% {{ transform: translateY(0) rotate(-4deg); }}
        50%      {{ transform: translateY(-14px) rotate(4deg); }}
      }}
      .big {{ font-size: 110px; line-height: 1.1; text-align: center;
             animation: bob 2s ease-in-out infinite; }}
      .card {{ background: rgba(255,255,255,.85); border-radius: 18px; padding: 14px;
              text-align: center; box-shadow: 0 6px 16px rgba(0,0,0,.12); color: #222; }}
      .card .face {{ font-size: 56px; animation: bob 2.4s ease-in-out infinite; }}
      .card small {{ color: #555; }}
      @media (prefers-reduced-motion: reduce) {{
        .balloon, .walker, .big, .card .face {{ animation: none; }}
        .walker {{ left: auto; position: static; }}
      }}
    </style>
    <div class="sky">{balloons_html}{walkers_html}</div>
    """
)

# ---------------------------------------------------------------
# 머리말
# ---------------------------------------------------------------
st.title("🎈 풍선과 괴물 나라 👾")
st.write("Hello Nam King")

b1, b2, _ = st.columns([1, 1, 4])
if b1.button("🎈 풍선 날리기", use_container_width=True):
    st.balloons()
if b2.button("❄️ 눈 내리기", use_container_width=True):
    st.snow()

# ---------------------------------------------------------------
# 캐릭터 도감
# ---------------------------------------------------------------
st.header("📖 캐릭터 도감")

st.subheader("우리 편")
for col, (name, hero) in zip(st.columns(len(HEROES)), HEROES.items()):
    col.html(
        f'<div class="card"><div class="face">{hero["emoji"]}</div>'
        f'<b>{name.split(" ", 1)[1]}</b><br><small>{hero["desc"]}</small><br>'
        f'<small>체력 {hero["hp"]} · 공격 {hero["atk"][0]}~{hero["atk"][1]}</small></div>'
    )

st.subheader("괴물들")
for col, monster in zip(st.columns(len(MONSTERS)), MONSTERS):
    col.html(
        f'<div class="card"><div class="face">{monster["emoji"]}</div>'
        f'<b>{monster["name"]}</b><br>'
        f'<small>체력 {monster["hp"]} · 공격 {monster["atk"][0]}~{monster["atk"][1]}</small></div>'
    )

# ---------------------------------------------------------------
# 괴물 물리치기 게임
# ---------------------------------------------------------------
st.header("⚔️ 괴물 물리치기")

ss = st.session_state


def new_monster():
    ss.monster = dict(random.choice(MONSTERS))
    ss.monster_hp = ss.monster["hp"]


def new_game():
    ss.hero_hp = HEROES[ss.hero_name]["hp"]
    ss.score = 0
    ss.log = ["새로운 모험이 시작됐다!"]
    new_monster()


hero_name = st.selectbox("캐릭터를 고르세요", list(HEROES), key="hero_name", on_change=new_game)
hero = HEROES[hero_name]
if "monster" not in ss:
    new_game()


def attack():
    dmg = random.randint(*hero["atk"])
    ss.monster_hp = max(0, ss.monster_hp - dmg)
    ss.log.insert(0, f'{hero["emoji"]} 공격! {ss.monster["emoji"]} 에게 {dmg} 피해')
    if ss.monster_hp == 0:
        ss.score += 1
        ss.celebrate = True
        ss.log.insert(0, f'🎉 {ss.monster["name"]} 을(를) 물리쳤다!')
        new_monster()
        ss.log.insert(0, f'{ss.monster["emoji"]} {ss.monster["name"]} 이(가) 나타났다!')
        return
    hit = random.randint(*ss.monster["atk"])
    ss.hero_hp = max(0, ss.hero_hp - hit)
    ss.log.insert(0, f'{ss.monster["emoji"]} 반격! {hit} 피해를 입었다')


def heal():
    amount = random.randint(15, 30)
    ss.hero_hp = min(hero["hp"], ss.hero_hp + amount)
    ss.log.insert(0, f"🧪 물약을 마셨다. 체력 +{amount}")
    hit = random.randint(*ss.monster["atk"])
    ss.hero_hp = max(0, ss.hero_hp - hit)
    ss.log.insert(0, f'{ss.monster["emoji"]} 그 틈에 공격! {hit} 피해를 입었다')


if ss.pop("celebrate", False):
    st.balloons()

left, mid, right = st.columns([2, 1, 2])
with left:
    st.html(f'<div class="big">{hero["emoji"]}</div>')
    st.progress(ss.hero_hp / hero["hp"], text=f'{hero_name}  ❤️ {ss.hero_hp} / {hero["hp"]}')
with mid:
    st.html('<div style="font-size:60px; text-align:center; padding-top:30px;">⚔️</div>')
    st.metric("물리친 괴물", f"{ss.score} 마리")
with right:
    st.html(f'<div class="big">{ss.monster["emoji"]}</div>')
    st.progress(
        ss.monster_hp / ss.monster["hp"],
        text=f'{ss.monster["name"]}  💜 {ss.monster_hp} / {ss.monster["hp"]}',
    )

fallen = ss.hero_hp == 0
a1, a2, a3 = st.columns(3)
a1.button("⚔️ 공격", on_click=attack, disabled=fallen, use_container_width=True, type="primary")
a2.button("🧪 물약", on_click=heal, disabled=fallen, use_container_width=True)
a3.button("🔄 다시 시작", on_click=new_game, use_container_width=True)

if fallen:
    st.error(f"쓰러지고 말았다… 괴물 {ss.score} 마리를 물리쳤습니다. '다시 시작'을 눌러 보세요.")

with st.container(border=True, height=200):
    for line in ss.log[:30]:
        st.write(line)
