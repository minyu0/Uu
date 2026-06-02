import streamlit as st
from google import genai
from google.genai import types
from google.genai.errors import APIError

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="달콤살벌 연애상담소", page_icon="💌")
st.title("💌 달콤살벌 연애상담소")
st.caption("Gemini 2.5 Flash-Lite가 당신의 연애 고민을 들어줍니다.")

# 2. Streamlit Secrets에서 API 키 불러오기 및 클라이언트 초기화
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
except KeyError:
    st.error("Streamlit Secrets에 'GEMINI_API_KEY'가 설정되지 않았습니다. 설정 후 다시 시도해주세요.")
    st.stop()

# 3. 세션 상태(Session State)로 채팅 기록 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. 기존 대화 기록 화면에 출력
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. 사용자 입력 받기
if prompt := st.chat_input("연애 고민을 편하게 털어놓으세요..."):
    # 사용자 메시지 화면에 표시 및 세션에 저장
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 6. Gemini 모델을 통한 답변 생성 (오류 처리 포함)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("🤔 고민 접수 중... 잠시만 기다려주세요.")
        
        try:
            # 연애 상담가 페르소나 부여를 위한 시스템 지침 설정
            system_instruction = (
                "당신은 공감 능력이 뛰어나면서도 필요할 땐 뼈 때리는 조언을 아끼지 않는 "
                "프로 연애 상담가입니다. 친근하고 다정한 말투를 사용하되, 진정성 있게 답변해주세요."
            )
            
            # 대화 기록 형식 변환 (Gemini SDK 규격에 맞춤)
            contents = []
            for msg in st.session_state.messages:
                role = "user" if msg["role"] == "user" else "model"
                contents.append(types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=msg["content"])]
                ))
            
            # API 호출 (gemini-2.5-flash-lite 모델 사용)
            response = client.models.generate_content(
                model='gemini-2.5-flash-lite',
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.7,
                )
            )
            
            # 답변 출력 및 세션에 저장
            ai_response = response.text
            message_placeholder.markdown(ai_response)
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            
        except APIError as e:
            # 구글 API 측 에러 처리
            message_placeholder.empty()
            st.error(f"Gemini API 오류가 발생했습니다: {e.message}")
        except Exception as e:
            # 기타 예기치 못한 에러 처리
            message_placeholder.empty()
            st.error(f"시스템 오류가 발생했습니다: {str(e)}")
