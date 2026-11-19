import streamlit as st

st.set_page_config(page_title="Streamlit 연습", page_icon="🎈")

st.title("Streamlit 연습 페이지")
st.write("Hello Nam King")

# ---------------------------------------------------------------
# 1. HTML 태그
# ---------------------------------------------------------------
st.header("1. HTML 태그")

st.html(
    """
    <h3 style="color:#e74c3c;">h3 제목 태그</h3>
    <p>
      문단(p) 안에서 <b>굵게</b>, <i>기울임</i>, <u>밑줄</u>,
      <mark>형광펜</mark>, <del>취소선</del>, <code>code</code>,
      H<sub>2</sub>O, x<sup>2</sup> 를 쓸 수 있습니다.
    </p>
    <hr>
    <blockquote style="border-left:4px solid #3498db; margin:0; padding-left:12px;">
      blockquote 인용문 태그입니다.
    </blockquote>
    """
)

col1, col2 = st.columns(2)

with col1:
    st.html(
        """
        <h4>목록 (ul / ol)</h4>
        <ul>
          <li>사과</li>
          <li>바나나</li>
          <li>포도</li>
        </ul>
        <ol>
          <li>환경 만들기</li>
          <li>패키지 설치</li>
          <li>앱 실행</li>
        </ol>
        """
    )

with col2:
    st.html(
        """
        <h4>표 (table)</h4>
        <table style="border-collapse:collapse; width:100%;">
          <tr style="background:#3498db; color:white;">
            <th style="padding:6px; border:1px solid #999;">이름</th>
            <th style="padding:6px; border:1px solid #999;">언어</th>
            <th style="padding:6px; border:1px solid #999;">점수</th>
          </tr>
          <tr>
            <td style="padding:6px; border:1px solid #999;">철수</td>
            <td style="padding:6px; border:1px solid #999;">Python</td>
            <td style="padding:6px; border:1px solid #999;">95</td>
          </tr>
          <tr>
            <td style="padding:6px; border:1px solid #999;">영희</td>
            <td style="padding:6px; border:1px solid #999;">JavaScript</td>
            <td style="padding:6px; border:1px solid #999;">88</td>
          </tr>
        </table>
        """
    )

st.html(
    """
    <div style="padding:16px; border-radius:10px; color:white;
                background:linear-gradient(90deg,#8e44ad,#3498db);">
      <strong>div 박스</strong> — 인라인 style 로 꾸민 카드입니다.
      <span style="background:#f1c40f; color:#000; padding:2px 8px;
                   border-radius:12px; margin-left:8px;">span 배지</span>
    </div>

    <details style="margin-top:12px;">
      <summary>details / summary (클릭해서 펼치기)</summary>
      <p>숨겨져 있던 내용이 나타납니다.</p>
    </details>

    <p style="margin-top:12px;">
      progress 태그: <progress value="70" max="100"></progress> 70%
    </p>

    <img src="https://picsum.photos/600/200" alt="랜덤 이미지"
         style="border-radius:10px; max-width:100%;">
    """
)

# ---------------------------------------------------------------
# 2. 마크다운
# ---------------------------------------------------------------
st.header("2. 마크다운")

st.markdown(
    """
### 텍스트 꾸미기
**굵게**, *기울임*, ~~취소선~~, `인라인 코드`,
:red[빨강], :blue[파랑], :green[초록], :rainbow[무지개] :sparkles:

### 목록
- 항목 1
- 항목 2
    - 하위 항목 2-1
    - 하위 항목 2-2

1. 첫째
2. 둘째
3. 셋째

- [x] 완료한 일
- [ ] 해야 할 일

### 인용문
> 마크다운 인용문입니다.

### 표
| 명령어 | 설명 |
|---|---|
| `st.write` | 무엇이든 출력 |
| `st.markdown` | 마크다운 출력 |
| `st.html` | HTML 출력 |

### 수식
$E = mc^2$, $\\sum_{i=1}^{n} i = \\frac{n(n+1)}{2}$

### 코드 블록
```python
import streamlit as st

def hello(name: str) -> str:
    return f"Hello, {name}!"

st.write(hello("World"))
```

```bash
conda activate streamlit
streamlit run st.py
```

---
"""
)

st.code("SELECT name, score FROM students WHERE score >= 90;", language="sql")

# ---------------------------------------------------------------
# 3. 링크
# ---------------------------------------------------------------
st.header("3. 링크")

st.subheader("마크다운 링크")
st.markdown(
    """
- [Streamlit 공식 문서](https://docs.streamlit.io)
- [Python 공식 사이트](https://www.python.org)
- [GitHub](https://github.com)
- [네이버](https://www.naver.com)
- 주소 그대로: <https://www.google.com>
- 이미지 링크: [![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
"""
)

st.subheader("HTML a 태그 링크")
st.html(
    """
    <p>
      <a href="https://www.wikipedia.org" target="_blank">위키백과 (새 탭)</a> |
      <a href="https://www.youtube.com" target="_blank"
         style="color:#e74c3c; font-weight:bold; text-decoration:none;">YouTube (스타일 적용)</a> |
      <a href="https://pandas.pydata.org" target="_blank"
         style="background:#2ecc71; color:white; padding:4px 12px;
                border-radius:6px; text-decoration:none;">pandas (버튼 모양)</a>
    </p>
    """
)

st.subheader("Streamlit 링크 위젯")
c1, c2, c3 = st.columns(3)
c1.link_button("Streamlit 갤러리", "https://streamlit.io/gallery")
c2.link_button("Anaconda", "https://www.anaconda.com")
c3.link_button("Stack Overflow", "https://stackoverflow.com")

st.page_link("https://docs.streamlit.io/develop/api-reference", label="API 레퍼런스 바로가기", icon="📚")
