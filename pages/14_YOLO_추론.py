import io
from pathlib import Path

import pandas as pd
import streamlit as st
from PIL import Image, ImageOps, UnidentifiedImageError

import ui

ui.setup("YOLO 사진 추론", "🎯", layout="wide")
st.write("사진을 올리거나 찍으면 YOLO 모델이 사진 속 물체를 찾아 상자로 표시합니다. 분석 설정은 사이드바에 있습니다.")

MODEL_DIR = Path(__file__).parent.parent / "models"
MODELS = {
    "YOLO11n (가장 빠름)": "yolo11n.pt",
    "YOLO11s (조금 더 정확)": "yolo11s.pt",
    "YOLO11n-seg (윤곽까지 표시)": "yolo11n-seg.pt",
    "YOLO11n-pose (사람 자세)": "yolo11n-pose.pt",
}
MODEL_NAMES = list(MODELS)

UPLOAD, CAMERA = "📁 사진 올리기", "📷 사진 찍기"

# 분석 설정의 기본값. 위젯의 key 와 같은 이름으로 session_state 에 들어간다.
DEFAULTS = {
    "yolo_model": MODEL_NAMES[0],
    "yolo_imgsz": 640,
    "yolo_conf": 0.25,
    "yolo_iou": 0.70,
    "yolo_max_det": 100,
    "yolo_classes": [],
    "yolo_augment": False,
    "yolo_agnostic": False,
    "yolo_boxes": True,
    "yolo_labels": True,
    "yolo_show_conf": True,
    "yolo_line_width": 0,
    "yolo_crops": False,
}
PRESETS = {
    "⚡ 빠르게": {"yolo_model": MODEL_NAMES[0], "yolo_imgsz": 320, "yolo_conf": 0.35, "yolo_augment": False},
    "⚖️ 균형": {"yolo_model": MODEL_NAMES[0], "yolo_imgsz": 640, "yolo_conf": 0.25, "yolo_augment": False},
    "🔍 정밀": {"yolo_model": MODEL_NAMES[1], "yolo_imgsz": 960, "yolo_conf": 0.20, "yolo_augment": True},
}

for key, value in DEFAULTS.items():
    st.session_state.setdefault(key, value)


def apply_settings(values: dict) -> None:
    st.session_state.update(values)
    # 모델이 바뀌면 고를 수 있는 물체 종류도 달라지므로 종류 선택은 비운다.
    st.session_state.yolo_classes = []


@st.cache_resource(show_spinner="모델을 불러오는 중… (처음에는 내려받느라 시간이 걸립니다)")
def load_model(filename: str):
    # 모델은 한 번만 읽어 서버 메모리에 두고 모든 실행에서 다시 쓴다.
    from ultralytics import YOLO

    MODEL_DIR.mkdir(exist_ok=True)
    return YOLO(MODEL_DIR / filename)


# ------------------------------ 사이드바: 분석 설정
with st.sidebar:
    st.header("🎯 분석 설정")

    st.caption("한 번에 맞추기")
    for column, (label, values) in zip(st.columns(len(PRESETS)), PRESETS.items()):
        column.button(label, on_click=apply_settings, args=(values,), width="stretch", key=f"preset_{label}")

    st.subheader("모델")
    model_name = st.selectbox("모델", MODEL_NAMES, key="yolo_model", on_change=apply_settings, args=({},))
    model = load_model(MODELS[model_name])
    imgsz = st.select_slider(
        "분석 크기 (px)",
        [320, 480, 640, 800, 960, 1280],
        key="yolo_imgsz",
        help="사진을 이 크기로 줄여서 분석합니다. 크면 작은 물체를 더 잘 찾지만 느려집니다.",
    )

    st.subheader("찾는 기준")
    conf = st.slider("신뢰도 기준", 0.05, 0.95, step=0.05, key="yolo_conf", help="이 값보다 확신이 낮은 결과는 버립니다.")
    iou = st.slider("겹침 기준 (IoU)", 0.10, 0.90, step=0.05, key="yolo_iou", help="이 값보다 많이 겹치는 상자는 하나로 합칩니다.")
    max_det = st.number_input("최대 물체 수", 1, 300, step=10, key="yolo_max_det")
    class_ids = {name: index for index, name in model.names.items()}
    classes = st.multiselect(
        "찾을 종류",
        list(class_ids),
        key="yolo_classes",
        placeholder="모든 종류",
        help="비워 두면 모델이 아는 모든 종류를 찾습니다.",
    )
    augment = st.toggle("정밀 분석 (느림)", key="yolo_augment", help="사진을 여러 방식으로 바꿔 가며 분석해 결과를 합칩니다.")
    agnostic = st.toggle("종류가 달라도 겹치면 합치기", key="yolo_agnostic")

    st.subheader("표시")
    show_boxes = st.toggle("상자 표시", key="yolo_boxes")
    show_labels = st.toggle("이름 표시", key="yolo_labels")
    show_conf = st.toggle("신뢰도 표시", key="yolo_show_conf")
    line_width = st.slider("선 굵기 (0 = 자동)", 0, 10, key="yolo_line_width")
    show_crops = st.toggle("찾은 물체 잘라 보기", key="yolo_crops")

    st.button("기본값으로 되돌리기", on_click=apply_settings, args=(DEFAULTS,), width="stretch")

# ------------------------------ 사진 받기
# 올리기와 찍기 중 지금 고른 한 가지만 쓴다. 두 입력을 동시에 두면 찍어 둔 사진이 올린 사진을 가려 버린다.
method = st.radio("사진 넣는 방법", [UPLOAD, CAMERA], horizontal=True, key="yolo_method", label_visibility="collapsed")

if method == UPLOAD:
    source = st.file_uploader(
        "사진 파일을 올리세요",
        type=["jpg", "jpeg", "jfif", "png", "bmp", "webp", "gif", "tif", "tiff", "heic", "heif"],
        key="yolo_upload",
    )
    source_label = f"올린 사진: {source.name}" if source else ""
else:
    st.caption("브라우저가 카메라 사용 허락을 물으면 허용해 주세요.")
    source = st.camera_input("사진을 찍으세요", key="yolo_camera")
    source_label = "방금 찍은 사진"

if source is None:
    st.info("사진을 올리거나 찍으면 여기에 결과가 나타납니다.")
    st.stop()

try:
    opened = Image.open(io.BytesIO(source.getvalue()))
    # 휴대폰 사진은 회전 정보(EXIF)가 따로 들어 있어, 바로 세워 준 뒤 분석한다.
    image = ImageOps.exif_transpose(opened).convert("RGB")
except (UnidentifiedImageError, OSError, ValueError) as exc:
    st.error(f"사진을 열 수 없습니다. 다른 파일로 시도해 주세요. ({type(exc).__name__})")
    st.stop()

# ------------------------------ 추론
with st.spinner("추론하는 중…"):
    result = model.predict(
        image,
        imgsz=imgsz,
        conf=conf,
        iou=iou,
        max_det=int(max_det),
        classes=[class_ids[name] for name in classes] or None,
        augment=augment,
        agnostic_nms=agnostic,
        verbose=False,
    )[0]

# plot() 은 BGR 순서의 배열을 돌려주므로 RGB 로 뒤집어 보여 준다.
annotated = result.plot(boxes=show_boxes, labels=show_labels, conf=show_conf, line_width=line_width or None)[..., ::-1]

st.caption(source_label)
left, right = st.columns(2)
left.subheader("원본")
left.image(image, width="stretch")
right.subheader("추론 결과")
right.image(annotated, width="stretch")

# ------------------------------ 결과 정리
boxes = result.boxes
rows = [
    {
        "물체": result.names[int(cls)],
        "신뢰도": round(float(score), 3),
        "왼쪽": int(x1),
        "위": int(y1),
        "오른쪽": int(x2),
        "아래": int(y2),
        "넓이 비율(%)": round((x2 - x1) * (y2 - y1) / (image.width * image.height) * 100, 1),
    }
    for cls, score, (x1, y1, x2, y2) in zip(boxes.cls.tolist(), boxes.conf.tolist(), boxes.xyxy.tolist())
]
found = pd.DataFrame(rows, columns=["물체", "신뢰도", "왼쪽", "위", "오른쪽", "아래", "넓이 비율(%)"])
found = found.sort_values("신뢰도", ascending=False, ignore_index=True)

m1, m2, m3, m4 = st.columns(4)
m1.metric("찾은 물체", f"{len(found)} 개")
m2.metric("종류", f"{found['물체'].nunique()} 가지")
m3.metric("추론 시간", f"{result.speed['inference']:.0f} ms")
m4.metric("사진 크기", f"{image.width} × {image.height}")

with st.expander("이번 분석에 쓴 설정"):
    st.table(
        pd.DataFrame(
            {
                "설정": ["모델", "분석 크기", "신뢰도 기준", "겹침 기준", "최대 물체 수", "찾을 종류", "정밀 분석"],
                "값": [
                    model_name,
                    f"{imgsz} px",
                    f"{conf:.2f}",
                    f"{iou:.2f}",
                    str(int(max_det)),
                    ", ".join(classes) or "모든 종류",
                    "켬" if augment else "끔",
                ],
            }
        ).set_index("설정")
    )

if found.empty:
    st.warning("물체를 찾지 못했습니다. 사이드바에서 신뢰도 기준을 낮추거나, 찾을 종류를 비우거나, 다른 사진으로 시도해 보세요.")
    st.stop()

chart_col, table_col = st.columns([1, 2])
chart_col.subheader("종류별 개수")
chart_col.bar_chart(found["물체"].value_counts(), horizontal=True)
table_col.subheader("찾은 물체 목록")
table_col.dataframe(
    found,
    hide_index=True,
    width="stretch",
    column_config={"신뢰도": st.column_config.ProgressColumn("신뢰도", min_value=0, max_value=1, format="%.2f")},
)

if show_crops:
    st.subheader("찾은 물체 잘라 보기")
    shown = found.head(12)
    grid = st.columns(6)
    for i, row in shown.iterrows():
        crop = image.crop((row["왼쪽"], row["위"], row["오른쪽"], row["아래"]))
        if crop.width and crop.height:
            grid[i % 6].image(crop, caption=f"{row['물체']} {row['신뢰도']:.2f}", width="stretch")
    if len(found) > len(shown):
        st.caption(f"신뢰도가 높은 {len(shown)}개만 보여 줍니다. (전체 {len(found)}개)")

buffer = io.BytesIO()
Image.fromarray(annotated).save(buffer, format="PNG")
c1, c2, _ = st.columns([1, 1, 3])
c1.download_button("결과 사진 내려받기", buffer.getvalue(), file_name="yolo_result.png", mime="image/png", width="stretch")
c2.download_button(
    "목록 CSV 내려받기",
    found.to_csv(index=False).encode("utf-8-sig"),
    file_name="yolo_result.csv",
    mime="text/csv",
    width="stretch",
)
