import hashlib
import os
import re
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

import ui

ui.setup("파일 업로드 과정 보기", "📤")
st.write("파일을 올리면 서버가 받은 파일을 검사하고, 체크섬을 계산하고, 저장하는 과정을 단계별로 보여 줍니다.")

UPLOAD_DIR = Path(os.environ.get("APP_UPLOADS", Path(__file__).parent.parent / "uploads"))
STEPS = 40  # 진행 막대가 움직이는 횟수


def human_size(size: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:,.0f} {unit}" if unit == "B" else f"{size:,.1f} {unit}"
        size /= 1024


def safe_name(name: str) -> str:
    """경로와 위험한 문자를 떼어 내고, 같은 이름끼리 덮어쓰지 않도록 시각을 앞에 붙인다."""
    cleaned = re.sub(r"[^\w.\- ]", "_", Path(name).name).strip(" .") or "file"
    return f"{datetime.now():%Y%m%d_%H%M%S_%f}_{cleaned}"


def chunks(data: bytes, slow: bool):
    """데이터를 STEPS 조각 안팎으로 나눠 (조각, 지금까지 처리한 비율) 을 차례로 내준다.

    천천히 보기에서는 작은 파일도 진행 막대가 움직이도록 조각 크기에 하한을 두지 않는다.
    """
    size = max(1 if slow else 64 * 1024, -(-len(data) // STEPS))
    view = memoryview(data)
    for start in range(0, len(data), size):
        yield view[start : start + size], min(1.0, (start + size) / len(data))


def process(uploaded, slow: bool) -> dict:
    """받은 파일 하나를 단계별로 처리하면서 화면에 진행 상황을 그린다."""
    pause = 0.04 if slow else 0
    started = time.perf_counter()
    with st.status(f"'{uploaded.name}' 처리 중…", expanded=True) as status:
        # 1. 받기: 브라우저에서 서버로 전송은 이 시점에 이미 끝나 있다.
        data = uploaded.getvalue()
        st.write(f"✅ **1. 받기** — {human_size(len(data))}, 종류: `{uploaded.type or '알 수 없음'}`")

        # 2. 검사
        if not data:
            status.update(label=f"'{uploaded.name}' 실패: 빈 파일", state="error")
            st.write("❌ **2. 검사** — 내용이 없는 파일입니다.")
            return {"이름": uploaded.name, "상태": "실패 (빈 파일)", "크기": "0 B"}
        st.write(f"✅ **2. 검사** — 확장자 `{Path(uploaded.name).suffix or '없음'}`, 빈 파일 아님")

        # 3. 체크섬
        bar = st.progress(0.0, text="3. 체크섬 계산 중…")
        digest = hashlib.sha256()
        for chunk, done in chunks(data, slow):
            digest.update(chunk)
            bar.progress(done, text=f"3. 체크섬 계산 중… {done:.0%}")
            time.sleep(pause)
        bar.empty()
        checksum = digest.hexdigest()
        st.write(f"✅ **3. 체크섬** — SHA-256 `{checksum[:16]}…`")

        # 4. 저장
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        target = UPLOAD_DIR / safe_name(uploaded.name)
        bar = st.progress(0.0, text="4. 저장 중…")
        written = 0
        with open(target, "wb") as out:
            for chunk, done in chunks(data, slow):
                written += out.write(chunk)
                bar.progress(done, text=f"4. 저장 중… {human_size(written)} / {human_size(len(data))}")
                time.sleep(pause)
        bar.empty()
        st.write(f"✅ **4. 저장** — `{target.name}`")

        # 5. 확인: 저장된 파일을 다시 읽어 체크섬이 같은지 본다.
        same = hashlib.sha256(target.read_bytes()).hexdigest() == checksum
        elapsed = time.perf_counter() - started
        if not same:
            status.update(label=f"'{uploaded.name}' 실패: 저장된 내용이 다릅니다", state="error")
            st.write("❌ **5. 확인** — 저장된 파일의 체크섬이 원본과 다릅니다.")
            return {"이름": uploaded.name, "상태": "실패 (확인)", "크기": human_size(len(data))}
        st.write(f"✅ **5. 확인** — 저장된 파일의 체크섬이 원본과 같습니다. ({elapsed:.2f}초)")
        status.update(label=f"'{uploaded.name}' 완료 ({elapsed:.2f}초)", state="complete", expanded=False)

    return {
        "이름": uploaded.name,
        "상태": "완료",
        "크기": human_size(len(data)),
        "걸린 시간(초)": round(elapsed, 2),
        "SHA-256": checksum,
        "저장 이름": target.name,
    }


# ------------------------------ 올리기
slow = st.toggle("과정을 천천히 보기", value=True, key="upload_slow", help="끄면 기다림 없이 실제 속도로 처리합니다.")
files = st.file_uploader("파일을 올리세요 (여러 개 가능)", accept_multiple_files=True, key="upload_files")

# 화면이 다시 그려질 때 같은 파일을 또 저장하지 않도록, 처리한 파일을 기억해 둔다.
done = st.session_state.setdefault("upload_done", {})

new_files = [f for f in files or [] if f.file_id not in done]
if new_files:
    overall = st.progress(0.0, text=f"전체 진행: 0 / {len(new_files)}")
    for i, uploaded in enumerate(new_files, start=1):
        done[uploaded.file_id] = process(uploaded, slow)
        overall.progress(i / len(new_files), text=f"전체 진행: {i} / {len(new_files)}")
    failed = sum(done[f.file_id]["상태"] != "완료" for f in new_files)
    if failed:
        st.error(f"{len(new_files)}개 중 {failed}개를 처리하지 못했습니다. 위 단계에서 이유를 확인하세요.")
    else:
        st.success(f"{len(new_files)}개 파일을 모두 저장했습니다.")

# ------------------------------ 결과
if done:
    st.subheader("이번 방문에서 올린 파일")
    st.dataframe(pd.DataFrame(done.values()), hide_index=True, width="stretch")

st.subheader("서버에 저장된 파일")
st.caption(f"저장 폴더: {UPLOAD_DIR}")
saved = sorted(UPLOAD_DIR.glob("*"), key=lambda p: p.stat().st_mtime, reverse=True) if UPLOAD_DIR.exists() else []
if saved:
    st.dataframe(
        pd.DataFrame(
            {
                "저장 이름": [p.name for p in saved],
                "크기": [human_size(p.stat().st_size) for p in saved],
                "저장 시각": [datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S") for p in saved],
            }
        ),
        hide_index=True,
        width="stretch",
    )
else:
    st.write("아직 저장된 파일이 없습니다.")

with st.expander("단계 설명"):
    st.markdown(
        """
1. **받기** — 브라우저가 보낸 파일을 서버가 메모리에 받습니다. 전송 진행률은 업로드 상자 안에 따로 표시됩니다.
2. **검사** — 빈 파일인지, 확장자가 무엇인지 확인합니다.
3. **체크섬** — 파일을 조각내어 읽으며 SHA-256 값을 계산합니다. 파일 내용의 지문입니다.
4. **저장** — 조각 단위로 디스크에 씁니다. 파일 이름은 안전한 글자만 남기고 앞에 시각을 붙입니다.
5. **확인** — 저장된 파일을 다시 읽어 체크섬이 원본과 같은지 봅니다.
"""
    )
