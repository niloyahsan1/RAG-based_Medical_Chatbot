import streamlit as st
from app.rag_engine import ask
from datetime import datetime
from collections import defaultdict

# Page config
st.set_page_config(page_title="FH Assistant", layout="wide")


# Session states
if "booking" not in st.session_state:
    st.session_state.booking = {"active": False, "step": None, "data": {}}

if "appointments" not in st.session_state:
    st.session_state.appointments = []

if "delete_mode" not in st.session_state:
    st.session_state.delete_mode = False

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


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
        query = last_user_msg.lower()


        # Appointment booking flow
        if st.session_state.booking["active"]:

            step = st.session_state.booking["step"]

            if step == "name":
                st.session_state.booking["data"]["name"] = last_user_msg
                st.session_state.booking["step"] = "time"
                answer = "What time would you prefer?"
                docs = []
            
            elif step == "time":
                st.session_state.booking["data"]["time"] = last_user_msg
                st.session_state.booking["step"] = "reason"
                answer = "What is the reason for the visit?"
                docs = []

            elif step == "reason":
                st.session_state.booking["data"]["reason"] = last_user_msg

                st.session_state.appointments.append(
                    st.session_state.booking["data"]
                )

                data = st.session_state.booking["data"]

                answer = f"""Appointment booked!

                - Name: {data['name']}
                - Time: {data['time']}
                - Reason: {data['reason']}

                """
                docs = []

                st.session_state.booking = {
                    "active": False,
                    "step": None,
                    "data": {}
                }


        # Delete appointment flow
        elif st.session_state.delete_mode:

            if not st.session_state.appointments:
                answer = "You have no appointments to delete."

            elif query.isdigit():
                index = int(query) - 1

                if 0 <= index < len(st.session_state.appointments):
                    removed = st.session_state.appointments.pop(index)

                    answer = f"""Appointment deleted:

                    - Name: {removed['name']}
                    - Time: {removed['time']}
                    - Reason: {removed['reason']}
                    
                    """

                else:
                    answer = "Invalid appointment number."

            else:
                answer = "Please enter a valid number."

            st.session_state.delete_mode = False
            docs = []



        # Show appointments
        elif "show" in query and "appointment" in query:

            if not st.session_state.appointments:
                answer = "You have no appointments."

            else:
                answer = "Your Appointments are below:\n\n"
                for i, a in enumerate(st.session_state.appointments, 1):
                    answer += f"""{i}.
                    - Name: {a['name']}
                    - Time: {a['time']}
                    - Reason: {a['reason']}

                    """
            docs = []


        # Delete appointments
        elif any(w in query for w in ["delete", "cancel", "remove"]):

            if not st.session_state.appointments:
                answer = "You have no appointments to delete."
            
            else:    
                # Extract appointment number
                words = query.split()
                index = None
            
                for w in words:
                    if w.isdigit():
                        index = int(w) - 1
                        break

                if index is not None:
                    if 0 <= index < len(st.session_state.appointments):
                        removed = st.session_state.appointments.pop(index)

                        answer = f"""Appointment deleted:

                        - Name: {removed['name']}
                        - Time: {removed['time']}
                        - Reason: {removed['reason']}
                        
                        """

                    else:
                        answer = "Invalid appointment number."

                else:
                    st.session_state.delete_mode = True
                    answer = "Which appointment number do you want to delete?"

            docs = []


        # Start booking flow
        elif "book" in query or "schedule" in query:
                        
            st.session_state.booking = {
                "active": True,
                "step": "name",
                "data": {}
            }
            answer = "Sure. What is your name?"
            docs = []


        # Normal RAG flow
        else:
            history = st.session_state.chat_history[-4:]
            appointments = st.session_state.appointments
            answer, docs = ask(last_user_msg, history, appointments)

        st.session_state.messages[-1] = {
            "role": "assistant",
            "content": answer,
            "time": datetime.now().strftime("%I:%M %p"),
            "docs": docs
        }

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": answer
        })

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

    st.session_state.chat_history.append({
    "role": "user",
    "content": query
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

    # Replace newlines with <br> for HTML display
    content_html = msg['content'].replace("\n", "<br>")

    # Render user and bot messages differently
    if msg["role"] == "user":
        st.markdown(f"""
        <div class="chat-row chat-user">
            <div class="bubble-user">
                {content_html}<br>
                <span class="timestamp">{msg.get('time','')}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    else:
        st.markdown(f"""
        <div class="chat-row chat-bot">
            <div class="bubble-bot">
                {content_html}<br>
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
            confidence = round(min(unique_docs / 2, 1.0), 2)
            st.write(f"Confidence: {confidence}")