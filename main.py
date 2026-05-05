import streamlit as st
from app.rag_engine import ask
from datetime import datetime
from collections import defaultdict
from app.retriever import get_retriever
from datetime import datetime
from app.rag_engine import is_valid_reason


# Page config
st.set_page_config(page_title="FH Assistant", layout="wide")


# Session states
if "booking" not in st.session_state:
    st.session_state.booking = {"active": False, "step": None, "data": {}}

if "delete_mode" not in st.session_state:
    st.session_state.delete_mode = False

if "doctor_select_mode" not in st.session_state:
    st.session_state.doctor_select_mode = False

if "appointments" not in st.session_state:
    st.session_state.appointments = []

if "selected_doctor" not in st.session_state:
    st.session_state.selected_doctor = None

if "doctor_options" not in st.session_state:
    st.session_state.doctor_options = []

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


# Handle typing states
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
                st.session_state.booking["step"] = "date"
                answer = "Please enter preferred date."
                docs = []
            
            elif step == "date":
                date_input = last_user_msg.strip()

                try:
                    parsed_date = datetime.strptime(date_input, "%d %B")

                    # Add current year
                    today = datetime.now()
                    parsed_date = parsed_date.replace(year=today.year)

                    # Check past date
                    if parsed_date.date() < today.date():
                        answer = "You cannot select a past date. Please choose a future date."
                        docs = []
                    
                    else:
                        st.session_state.booking["data"]["date"] = date_input
                        data = st.session_state.booking["data"]

                        answer = f"""Appointment booked!

                        - Name: {data['name']}
                        - Doctor: {data.get('doctor')}
                        - Date: {data['date']}
                        - Reason: {data.get('reason')}

                        """

                        st.session_state.appointments.append(data)

                        # Reset booking
                        st.session_state.booking = {
                            "active": False,
                            "step": None,
                            "data": {}
                        }

                        docs = []

                except:
                    answer = "Please enter a valid date (e.g., '4 May')."
                    docs = []


            elif step == "reason":
                if not is_valid_reason(last_user_msg):
                    answer = "Please describe a valid medical problem (e.g., fever, chest pain, infection)."
                    docs = []

                else:
                    st.session_state.selected_reason = last_user_msg
                    st.session_state.booking["data"]["reason"] = last_user_msg

                    enhanced_query = f"{last_user_msg} doctor treatment hospital"

                    retriever = get_retriever(k=8)
                    docs = retriever.invoke(enhanced_query)

                    doctors = []

                    # extraction logic
                    for d in docs:
                        lines = d.page_content.split("\n")

                        for i, line in enumerate(lines):
                            line = line.strip()

                            # Case 1: direct doctor line
                            if line.startswith("Dr."):
                                doctors.append(line)

                            # Case 2: match symptom → get previous line
                            if any(word in line.lower() for word in last_user_msg.lower().split()):
                                if i > 0:
                                    prev_line = lines[i - 1].strip()
                                    if prev_line.startswith("Dr."):
                                        doctors.append(prev_line)

                    # Remove duplicates
                    doctors = list(dict.fromkeys(doctors))

                    # If doctors found
                    if doctors:
                        st.session_state.doctor_options = doctors
                        st.session_state.doctor_select_mode = True

                        answer = "Available doctors:\n\n"
                        for i, d in enumerate(doctors, 1):
                            answer += f"{i}. {d}\n"

                        answer += "\nSelect a doctor by number."

                        # Pause booking until user selects doctor
                        st.session_state.booking["active"] = False

                    # If no doctors found
                    else:
                        answer = "No doctors found for your condition."

                    docs = []


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
                    - Doctor: {removed.get('doctor', 'Not assigned')}
                    - Date: {removed.get('date', 'Not set')}
                    - Reason: {removed['reason']}
                    
                    """

                else:
                    answer = "Invalid appointment number."

            else:
                answer = "Please enter a valid number."

            st.session_state.delete_mode = False
            docs = []


        # Doctor selection flow
        elif st.session_state.doctor_select_mode:

            # If user asks something else then exit selection mode
            if not query.isdigit():
                st.session_state.doctor_select_mode = False
                answer = "Okay, let me know what you want to do next."
                docs = []

            else:
                index = int(query) - 1

                if 0 <= index < len(st.session_state.doctor_options):
                    selected = st.session_state.doctor_options[index]

                    st.session_state.booking = {
                        "active": True,
                        "step": "name",
                        "data": {
                            "doctor": selected,
                            "reason": st.session_state.get("selected_reason", "")
                        }
                    }

                    st.session_state.doctor_select_mode = False

                    answer = f"You selected {selected}. What is your name?"

                else:
                    answer = "Invalid selection."

                docs = []


        # Show appointments
        elif "show" in query and "appointment" in query:

            if not st.session_state.appointments:
                answer = "You have no appointments."

            else:
                answer = "Your Appointments are below:\n\n"

                for i, a in enumerate(st.session_state.appointments, 1):
                    answer += f"""{i}.
                - Name: {a.get('name')}
                - Doctor: {a.get('doctor', 'Not assigned')}
                - Date: {a.get('date', 'Not set')}
                - Reason: {a.get('reason')}
                \n"""

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


        # Doctor informations
        elif ("doctor" in query or "doctors" in query) and "for" not in query and "book" not in query:

            history = st.session_state.chat_history[-4:]
            retriever = get_retriever(k=8)
            docs = retriever.invoke("doctor list hospital all departments")

            doctors = []

            for d in docs:
                lines = d.page_content.split("\n")
                for line in lines:
                    line = line.strip()

                    for i, line in enumerate(lines):
                        line = line.strip()

                        if line.startswith("Dr."):
                            doctors.append(line)

                        # fallback: if "Treats" matched, grab previous line (doctor)
                        if "treats" in line.lower() and i > 0:
                            prev_line = lines[i-1].strip()
                            if prev_line.startswith("Dr."):
                                doctors.append(prev_line)

            doctors = list(dict.fromkeys(doctors))

            if doctors:
                answer = "Here are the doctors available at the hospital:\n\n"
                for d in doctors:
                    answer += f"• {d}\n"
            else:
                answer = "No doctors found."

            docs = []


        # Doctors for symptoms
        elif "doctor" in query and "for" in query:

            history = st.session_state.chat_history[-4:]
            enhanced_query = f"{last_user_msg} doctor hospital treatment"
            retriever = get_retriever(k=8)
            docs = retriever.invoke(enhanced_query)

            doctors = []

            for d in docs:
                lines = d.page_content.split("\n")
                for line in lines:
                    line = line.strip()
                    if line.startswith("Dr."):
                        doctors.append(line)

            doctors = list(dict.fromkeys(doctors))

            if doctors:
                answer = "Doctors for your condition:\n\n"
                for d in doctors:
                    answer += f"• {d}\n"
            else:
                answer = "I couldn't find exact matches. You can consult a General Medicine doctor."

            docs = []


        # Doctor booking flow
        elif "book" in query and any(word in query for word in ["doctor", "dr"]):

            history = st.session_state.chat_history[-4:]
            answer, docs = ask(last_user_msg, history, st.session_state.appointments)

            # Extract doctor names from docs
            doctors = []

            for d in docs:
                lines = d.page_content.split("\n")
                for i, line in enumerate(lines):
                    line = line.strip()

                    if line.startswith("Dr."):
                        doctors.append(line)

            # Remove duplicates
            doctors = list(dict.fromkeys(doctors))

            if doctors:
                st.session_state.doctor_options = doctors
                st.session_state.doctor_select_mode = True

                answer = "Available doctors:\n\n"
                for i, d in enumerate(doctors, 1):
                    answer += f"{i}. {d}\n"

                answer += "\nSelect a doctor by number."
            else:
                answer = "No doctors found."

            docs = []


        # Start booking flow
        elif any(word in query for word in ["book", "appointment", "appoint", "schedule"]):

            st.session_state.booking = {
                "active": True,
                "step": "reason",
                "data": {}
            }

            answer = "What is the reason for your visit?"
            docs = []


        # Normal RAG fallback flow
        else:
            history = st.session_state.chat_history[-4:]
            answer, docs = ask(last_user_msg, history, st.session_state.appointments)

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


        # # confidence score
        # if docs:
        #     unique_docs = len(set([d.page_content for d in docs]))
        #     confidence = round(min(unique_docs / 2, 1.0), 2)
        #     st.write(f"Confidence: {confidence}")