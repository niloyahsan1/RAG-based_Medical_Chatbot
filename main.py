import streamlit as st
from app.rag_engine import ask
from datetime import datetime
from collections import defaultdict


st.set_page_config(page_title="FGH Assistant", layout="wide")

# Header
col1, col2 = st.columns([8, 2])

# Title
with col1:
    st.title("🤖 Fictional Hospital Assistant")

# Reset button
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Reset Chat"):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Hello! I am your hospital assistant. How can I help you today?",
                "time": datetime.now().strftime("%I:%M %p")
            }
        ]

        st.rerun()


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello! I am your hospital assistant. How can I help you today?",
            "time": datetime.now().strftime("%I:%M %p")
        }
    ]


# Handle typing state
if st.session_state.messages and st.session_state.messages[-1].get("typing"):

    last_user_msg = None

    for msg in reversed(st.session_state.messages):
        if msg["role"] == "user":
            last_user_msg = msg["content"]
            break

    if last_user_msg:
        answer, docs = ask(last_user_msg)

        st.session_state.messages[-1] = {
            "role": "assistant",
            "content": answer,
            "time": datetime.now().strftime("%I:%M %p"),
            "docs": docs
        }

        st.rerun()


# Chat input
query = st.chat_input("Ask your question...")


# Handle new message
if query:
    st.session_state.messages.append({
        "role": "user",
        "content": query,
        "time": datetime.now().strftime("%I:%M %p")
    })

    # Add typing placeholder
    st.session_state.messages.append({
        "role": "assistant",
        "content": "🤖 Typing...",
        "time": "",
        "typing": True
    })

    st.rerun()


# Custom CSS for chat bubbles
st.markdown("""
            <style>
            .chat-row { display: flex; margin: 10px 0; }
            .chat-user { justify-content: flex-end; }
            .chat-bot { justify-content: flex-start; }

            .bubble-user {
                background-color: #2F2F2F;
                color: white;
                padding: 10px;
                border-radius: 12px;
                max-width: 70%;
                transition: transform 0.2s ease, box-shadow 0.2s ease;
            }

            .bubble-user:hover {
                transform: scale(1.02);
                box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            }

            .bubble-bot {
                background-color: #E8E8E8;
                color: black;
                padding: 10px;
                border-radius: 12px;
                max-width: 70%;
                transition: transform 0.2s ease, box-shadow 0.2s ease;
            }

            .bubble-bot:hover {
                transform: scale(1.02);
                box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            }

            .timestamp {
                font-size: 0.75em;
                opacity: 0.6;
            }
            </style>
            """, unsafe_allow_html=True)


# Display chat messages
for msg in st.session_state.messages:

    if msg["role"] == "user":
        st.markdown(f"""
        <div class="chat-row chat-user">
            <div class="bubble-user">
                {msg['content']}<br>
                <span class="timestamp">{msg.get('time','')}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    else:
        st.markdown(f"""
        <div class="chat-row chat-bot">
            <div class="bubble-bot">
                {msg['content']}<br>
                <span class="timestamp">{msg.get('time','')}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


        # sources
        docs = msg.get("docs", [])

        if docs:
            grouped = defaultdict(list)

            for d in docs:
                source = d.metadata.get("source", "")                
                page = d.metadata.get("page", 0) + 1
                grouped[source].append(page)

            with st.expander("📖 Sources"):
                for src, pages in grouped.items():
                    pages = sorted(set(pages))
                    st.write(f"{src}")
                    st.write(f"Pages: {pages}")


        # confidence score
        if docs:
            unique_docs = len(set([d.page_content for d in docs]))
            confidence = round(min(unique_docs / 3, 1.0), 2)
            st.write(f"Confidence: {confidence}")