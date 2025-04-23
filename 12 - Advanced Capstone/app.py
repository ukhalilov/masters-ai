import streamlit as st
from chatbot import get_chain
from ticket import create_github_issue
from langchain_openai import ChatOpenAI
from datetime import datetime

# MUST BE FIRST Streamlit CALL
st.set_page_config(page_title="Customer Support AI", page_icon="🤖")

st.title("📞 Lexus Support Chatbot")

# Default GitHub credentials (maintainer-owned)
DEFAULT_GITHUB_TOKEN = "" # github token
DEFAULT_GITHUB_USER = "" # github user
DEFAULT_GITHUB_REPO = "" # github repo

# Session state setup
if "openai_key_submitted" not in st.session_state:
    st.session_state.openai_key_submitted = False
if "qa_chain" not in st.session_state:
    st.session_state.chat_history = []
    st.session_state.awaiting_ticket_consent = False
    st.session_state.awaiting_user_info = False
    st.session_state.ticket_data = {
        "name": None,
        "email": None,
        "summary": None,
        "question_summary": None,
        "original_question": None,
        "issue_url": None
    }

# OpenAI key input (main area)
if not st.session_state.openai_key_submitted:
    st.markdown("### 🔐 Enter your OpenAI API Key to begin")
    if "openai_input" not in st.session_state:
        st.session_state.openai_input = ""
    openai_input = st.text_input(
        "OpenAI API Key",
        type="password",
        value=st.session_state.openai_input,
        key="openai_input_visible"
    )
    if openai_input != st.session_state.openai_input:
        st.session_state.openai_input = openai_input
    if st.button("Submit"):
        if st.session_state.openai_input.strip():
            st.session_state.openai_key = st.session_state.openai_input
            st.session_state.qa_chain = get_chain(st.session_state.openai_key)
            st.session_state.openai_key_submitted = True
            st.rerun()
        else:
            st.warning("Please enter a valid API key.")
    st.stop()

# -------------------------------------------------
# Utility: decide whether the answer warrants sources
# -------------------------------------------------
def should_show_sources(answer: str, sources: list[str]) -> bool:
    """Return True only if the answer is substantive enough to justify showing sources."""
    # Very short or clearly trivial answers → hide sources
    if len(answer.strip()) < 40:          # tweak threshold if needed
        return False

    trivial_phrases = {
        "yes", "no", "okay", "ok", "sure",
        "thank you", "thanks", "you're welcome"
    }
    if answer.strip().lower() in trivial_phrases:
        return False

    # Otherwise, show them only when we actually have ≥ 2 distinct docs
    return len(sources) >= 2

# -------------------------------------------------
# Utility: normalise a reply into YES / NO / UNKNOWN
# -------------------------------------------------
def classify_yes_no(text: str) -> str:
    """Return 'yes', 'no', or 'unknown'."""
    text = text.strip().lower()

    affirmative = {
        "yes", "yeah", "yep", "sure", "ok", "okay",
        "please", "please do", "go ahead", "certainly", "of course"
    }
    negative = {
        "no", "nah", "nope", "cancel", "stop", "not now", "maybe later"
    }

    if any(phrase == text for phrase in affirmative):
        return "yes"
    if any(phrase == text for phrase in negative):
        return "no"
    return "unknown"


# Chat input
query = st.chat_input("Ask a question about Lexus cars or services:")

if query:
    timestamp = datetime.now().strftime("%H:%M")

    if st.session_state.awaiting_user_info:
        data = st.session_state.ticket_data
        llm = ChatOpenAI(
            temperature=0,
            openai_api_key=st.session_state.openai_key
        )
        extraction_prompt = f"""
        Extract the user's full name and email if available from this message:

        Message: {query}

        Respond with JSON in the format:
        {{"name": "<full name or null>", "email": "<email or null>"}}
        """
        result = llm.predict(extraction_prompt)

        import json
        try:
            extracted = json.loads(result)
            if extracted.get("email"):
                data["email"] = extracted["email"]
            if extracted.get("name"):
                data["name"] = extracted["name"]
        except Exception:
            pass

        # Check missing info
        missing = []
        if not data.get("name"):
            missing.append("name")
        if not data.get("email"):
            missing.append("email")

        if missing:
            st.session_state.chat_history.append({
                "q": query,
                "a": "Thanks! Please provide your name and email so we can contact you.",
                "sources": [],
                "timestamp": timestamp
            })
        else:
            # Store for future reuse
            st.session_state.default_user_name = data["name"]
            st.session_state.default_user_email = data["email"]

            # Create GitHub issue
            body = (
                f"**Name:** {data['name']}\n"
                f"**Email:** {data['email']}\n"
                f"**Original Question:** {data['original_question']}\n\n"
                f"**Summary:**\n{data['summary']}"
            )
            status, response = create_github_issue(
                DEFAULT_GITHUB_TOKEN,
                DEFAULT_GITHUB_USER,
                DEFAULT_GITHUB_REPO,
                title=data["question_summary"],
                body=body
            )
            if status == 201:
                url = response["html_url"]
                st.session_state.chat_history.append({
                    "q": query,
                    "a": f"✅ Your support ticket has been submitted! [View it here]({url})",
                    "sources": [],
                    "timestamp": timestamp
                })
                st.session_state.awaiting_user_info = False
            else:
                st.session_state.chat_history.append({
                    "q": query,
                    "a": "❌ Failed to create the ticket.",
                    "sources": [],
                    "timestamp": timestamp
                })

    elif st.session_state.awaiting_ticket_consent:
        intent = classify_yes_no(query)

        if "yes" in query.lower():
            llm = ChatOpenAI(
                temperature=0,
                openai_api_key=st.session_state.openai_key
            )
            summary = llm.predict(
                f"Summarize this customer support question in one line:\n{st.session_state.ticket_data['original_question']}"
            )
            st.session_state.ticket_data["summary"] = summary
            st.session_state.ticket_data["question_summary"] = summary
            st.session_state.awaiting_ticket_consent = False

            # If user info is already stored, create ticket immediately
            if "default_user_name" in st.session_state and "default_user_email" in st.session_state:
                data = st.session_state.ticket_data
                body = (
                    f"**Name:** {st.session_state.default_user_name}\n"
                    f"**Email:** {st.session_state.default_user_email}\n"
                    f"**Original Question:** {data['original_question']}\n\n"
                    f"**Summary:**\n{data['summary']}"
                )
                status, response = create_github_issue(
                    DEFAULT_GITHUB_TOKEN,
                    DEFAULT_GITHUB_USER,
                    DEFAULT_GITHUB_REPO,
                    title=data["question_summary"],
                    body=body
                )
                if status == 201:
                    url = response["html_url"]
                    st.session_state.chat_history.append({
                        "q": query,
                        "a": f"✅ Your support ticket has been submitted! [View it here]({url})",
                        "sources": [],
                        "timestamp": timestamp
                    })
                else:
                    st.session_state.chat_history.append({
                        "q": query,
                        "a": "❌ Failed to create the ticket.",
                        "sources": [],
                        "timestamp": timestamp
                    })
            else:
                # Ask for user name and email
                st.session_state.awaiting_user_info = True
                st.session_state.chat_history.append({
                    "q": query,
                    "a": "Sure! Please provide your name and email so I can create a support ticket for you.",
                    "sources": [],
                    "timestamp": timestamp
                })

        elif intent == "no":
            # ❌ user declined – exit consent mode gracefully
            st.session_state.awaiting_ticket_consent = False
            st.session_state.awaiting_user_info = False
            st.session_state.chat_history.append({
                "q": query,
                "a": "No problem — I won’t create a ticket. How else can I help you?",
                "sources": [],
                "timestamp": timestamp
            })

        else:
            st.session_state.chat_history.append({
                "q": query,
                "a": "Sorry, I didn’t catch that. Would you like me to create a support ticket? (Type 'yes' or 'no'.)",
                "sources": [],
                "timestamp": timestamp
            })

    else:
        # Normal QA flow
        st.session_state.ticket_data["original_question"] = query
        # Pre-populate user info if available
        if "default_user_name" in st.session_state:
            st.session_state.ticket_data["name"] = st.session_state.default_user_name
        if "default_user_email" in st.session_state:
            st.session_state.ticket_data["email"] = st.session_state.default_user_email

        result = st.session_state.qa_chain({
            "question": query,
            "chat_history": [(item["q"], item["a"]) for item in st.session_state.chat_history]
        })

        answer = result["answer"]
        sources = result.get("source_documents", [])
        unique_sources = list({doc.metadata["source"] for doc in sources})

        weak_phrases = [
            "i don't know",
            "couldn't find",
            "not sure",
            "i don't have",  # NEW – catches “I don't have the specific …”
            "i do not have",
            "unfortunately i don't",
            "check with",
            "visit the official",
            "check a reliable",
            "i don't have real-time",
        ]
        # 1) Is the answer weak / uncertain?
        is_weak = any(p in answer.lower() for p in weak_phrases) or len(unique_sources) < 2

        # 2) If it’s weak, force ticket offer and drop sources immediately
        if is_weak:
            final_answer = (
                "I couldn’t find that information. "
                "Would you like me to create a support ticket for you? (Type 'yes' to continue.)"
            )
            unique_sources = []
            st.session_state.awaiting_ticket_consent = True
        else:
            # 3) If it’s a solid answer, decide whether to show sources
            if not should_show_sources(answer, unique_sources):
                unique_sources = []
            final_answer = answer

        # Decide whether to keep or hide sources
        if not should_show_sources(answer, unique_sources):
            unique_sources = []

        if is_weak:
            final_answer = "I couldn't provide a clear answer. Would you like me to create a support ticket for you? (Type 'yes' to continue.)"
            unique_sources = []
            st.session_state.awaiting_ticket_consent = True
        else:
            final_answer = answer

        st.session_state.chat_history.append({
            "q": query,
            "a": final_answer,
            "sources": unique_sources,
            "timestamp": timestamp
        })

# Chat history display
for i, chat in enumerate(st.session_state.chat_history):
    bg_color = "#eeeeee" if i % 2 == 0 else "#f4f4f4"
    block_html = f"""
    <div style='background-color: {bg_color}; padding: 1.5rem; border-radius: 12px; margin-top: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.08);'>
        <p style='color: gray; font-size: 0.85rem;'>🕒 {chat['timestamp']}</p>
        <p><strong>🧑 You:</strong><br>{chat['q']}</p>
        <p><strong>🤖 Bot:</strong><br>{chat['a']}</p>
    """
    if chat["sources"]:
        block_html += "<p><strong>📚 Sources:</strong></p><ul style='margin-top: 0.25rem;'>"
        for src in chat["sources"]:
            block_html += f"<li style='margin-bottom: 0.3rem'>{src}</li>"
        block_html += "</ul>"
    block_html += "</div>"
    st.markdown(block_html, unsafe_allow_html=True)
