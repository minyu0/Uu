import streamlit as st
from google import genai
from google.genai import types

# -----------------------------
# 페이지 설정
# -----------------------------
st.set_page_config(
    page_title="청소년 진로상담 챗봇",
    page_icon="🎓",
    layout="centered"
)

st.title("🎓 청소년 진로상담 챗봇")
st.caption("관심사, 적성, 진학, 직업 선택에 대해 상담해보세요.")

# -----------------------------
# API 키 로드
# -----------------------------
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)

except Exception:
    st.error(
        "GEMINI_API_KEY를 Streamlit Secrets에 설정해주세요."
    )
    st.stop()

# -----------------------------
# 시스템 프롬프트
# -----------------------------
SYSTEM_PROMPT = """
당신은 청소년 진로상담 전문 AI입니다.

역할:
- 중학생, 고등학생 대상 진로상담 제공
- 학생의 관심사, 성격, 강점을 파악
- 다양한 진로와 직업을 소개
- 특정 직업을 강요하지 않음
- 현실적인 학습 방법과 준비 과정을 설명
- 친절하고 이해하기 쉬운 한국어 사용

상담 원칙:
1. 학생의 상황을 먼저 파악한다.
2. 여러 선택지를 제시한다.
3. 장점과 고려사항을 균형 있게 설명한다.
4. 불확실한 정보는 단정하지 않는다.
5. 학생의 자기결정을 존중한다.

답변은 구체적이고 실용적으로 작성하라.
"""

# -----------------------------
# 채팅 기록 초기화
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "안녕하세요! 😊\n\n"
                "저는 청소년 진로상담 챗봇입니다.\n"
                "관심 있는 과목, 좋아하는 활동, 고민 중인 진로를 알려주시면 함께 탐색해볼게요."
            )
        }
    ]

# -----------------------------
# 기존 대화 출력
# -----------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -----------------------------
# Gemini 응답 생성 함수
# -----------------------------
def get_gemini_response():
    conversation = SYSTEM_PROMPT + "\n\n"

    for msg in st.session_state.messages:
        role = "사용자" if msg["role"] == "user" else "상담사"
        conversation += f"{role}: {msg['content']}\n"

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=conversation,
        config=types.GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=1000,
        )
    )

    return response.text


# -----------------------------
# 사용자 입력
# -----------------------------
if prompt := st.chat_input("진로에 대해 무엇이든 물어보세요"):

    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):

        try:
            with st.spinner("생각 중입니다..."):

                answer = get_gemini_response()

                st.markdown(answer)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer
                    }
                )

        except Exception as e:

            error_message = (
                "죄송합니다. 응답 생성 중 오류가 발생했습니다.\n\n"
                f"오류 내용: {str(e)}"
            )

            st.error(error_message)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": error_message
                }
            )
