import streamlit as st
from app.rag_engine import ask
from datetime import datetime
from collections import defaultdict
import time

st.set_page_config(page_title="Medical Chatbot", layout="wide")


st.title("🏥 Medical Info Assistant")

# -------------------------------
# CHAT HISTORY
# -------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -------------------------------
# INPUT BOX
# -------------------------------
query = st.chat_input("Ask your question...")

# -------------------------------
# HANDLE NEW MESSAGE FIRST
# -------------------------------
if query:
    from datetime import datetime

    # Save user message
    st.session_state.messages.append({
        "role": "user",
        "content": query,
        "time": datetime.now().strftime("%I:%M %p")
    })

    # Thinking animation
    thinking = st.empty()
    for i in range(3):
        thinking.markdown("🤖 Thinking" + "." * (i % 3 + 1))
        time.sleep(0.4)

    # Get response
    answer, docs = ask(query)
    thinking.empty()

    # Save assistant message
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "time": datetime.now().strftime("%I:%M %p"),
        "docs": docs   # 👈 store docs with message
    })

# -------------------------------
# DISPLAY ALL MESSAGES (AFTER UPDATE)
# -------------------------------
for msg in st.session_state.messages:

    if msg["role"] == "user":
        st.markdown(
            f"""
            <div class="chat-row chat-user">
                <div class="bubble-user">
                    {msg['content']}<br>
                    <span class="timestamp">{msg.get('time','')}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    else:
        st.markdown(
            f"""
            <div class="chat-row chat-bot">
                <div class="bubble-bot">
                    {msg['content']}<br>
                    <span class="timestamp">{msg.get('time','')}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

# -------------------------------
# NEW MESSAGE
# -------------------------------
if query:
    st.session_state.messages.append({
        "role": "user",
        "content": query,
        "time": datetime.now().strftime("%I:%M %p")
    })

    # -------------------------------
    # THINKING ANIMATION
    # -------------------------------
    thinking_placeholder = st.empty()
    for i in range(3):
        thinking_placeholder.markdown("🤖 Thinking" + "." * (i % 3 + 1))
        time.sleep(0.5)

    # -------------------------------
    # GET RESPONSE
    # -------------------------------
    answer, docs = ask(query)

    thinking_placeholder.empty()

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "time": datetime.now().strftime("%I:%M %p")
    })

    st.markdown(f"<div style='text-align:left'>{answer}</div>", unsafe_allow_html=True)

    # -------------------------------
    # SHOW SOURCES
    # -------------------------------
    grouped = defaultdict(list)

    for d in docs:
        source = d.metadata.get("source", "")
        page = d.metadata.get("page", "")
        grouped[source].append(page)

    with st.expander("📚 Sources"):
        for src, pages in grouped.items():
            pages = sorted(set(pages))
            st.write(f"{src}")
            st.write(f"Pages: {pages}")

    # -------------------------------
    # OPTIONAL: CONFIDENCE SCORE
    # -------------------------------
    # 🔴 COMMENT THIS IF NOT NEEDED
    confidence = round(min(len(docs)/5, 1.0), 2)
    st.write(f"🔍 Confidence: {confidence}")

    # -------------------------------
    # OPTIONAL: SNIPPETS (FOR TESTING)
    # -------------------------------
    # 🔴 COMMENT THIS IF NOT NEEDED
    st.write("📄 Retrieved Snippets:")
    for d in docs[:2]:
        st.write(d.page_content[:200] + "...")