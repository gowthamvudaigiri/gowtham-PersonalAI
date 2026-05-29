import streamlit as st
from graph import ProfileAssistantGraph


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Gowtham Vudaigiri — AI Profile",
    page_icon="✦",
    layout="centered",
    initial_sidebar_state="expanded"
)


# =========================================================
# STYLES
# =========================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500&family=DM+Serif+Display&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0f0f11;
    color: #e8e6e1;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 1.5rem 6rem; max-width: 780px; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #151518;
    border-right: 1px solid #2a2a2f;
}
[data-testid="stSidebar"] * { color: #e8e6e1 !important; }

/* ── Header ── */
.profile-header {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 24px 0 20px;
    border-bottom: 1px solid #2a2a2f;
    margin-bottom: 28px;
}
.avatar {
    width: 48px; height: 48px;
    border-radius: 50%;
    background: linear-gradient(135deg, #c8a96e 0%, #8b6914 100%);
    display: flex; align-items: center; justify-content: center;
    font-family: 'DM Serif Display', serif;
    font-size: 20px; color: #0f0f11;
    flex-shrink: 0;
}
.profile-name {
    font-family: 'DM Serif Display', serif;
    font-size: 22px;
    color: #e8e6e1;
    margin: 0;
    line-height: 1.2;
}
.profile-role {
    font-size: 13px;
    color: #888;
    margin: 2px 0 0;
    font-weight: 300;
}
.status-dot {
    width: 8px; height: 8px;
    background: #4caf82;
    border-radius: 50%;
    display: inline-block;
    margin-right: 6px;
}

/* ── Chat messages ── */
.msg-wrapper {
    display: flex;
    gap: 12px;
    margin-bottom: 24px;
    animation: fadeUp 0.3s ease;
}
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
}
.msg-wrapper.user { flex-direction: row-reverse; }

.msg-icon {
    width: 34px; height: 34px;
    border-radius: 50%;
    display: flex; align-items: center;
    justify-content: center;
    font-size: 14px;
    flex-shrink: 0;
    margin-top: 2px;
}
.msg-icon.assistant {
    background: linear-gradient(135deg, #c8a96e, #8b6914);
    color: #0f0f11;
    font-family: 'DM Serif Display', serif;
}
.msg-icon.user {
    background: #2a2a2f;
    color: #888;
}

.msg-bubble {
    max-width: 88%;
    padding: 14px 18px;
    border-radius: 16px;
    font-size: 14.5px;
    line-height: 1.7;
}
.msg-bubble.assistant {
    background: #1a1a1f;
    border: 1px solid #2a2a2f;
    border-top-left-radius: 4px;
    color: #ddd9d2;
}
.msg-bubble.user {
    background: #c8a96e;
    color: #0f0f11;
    border-top-right-radius: 4px;
    font-weight: 500;
}

/* ── Thinking indicator ── */
.thinking {
    display: flex; gap: 5px;
    align-items: center;
    padding: 4px 2px;
}
.thinking span {
    width: 7px; height: 7px;
    background: #c8a96e;
    border-radius: 50%;
    animation: pulse 1.2s ease-in-out infinite;
}
.thinking span:nth-child(2) { animation-delay: 0.2s; }
.thinking span:nth-child(3) { animation-delay: 0.4s; }
@keyframes pulse {
    0%, 60%, 100% { opacity: 0.2; transform: scale(0.85); }
    30%            { opacity: 1;   transform: scale(1);    }
}

/* ── Input area ── */
[data-testid="stChatInput"] textarea {
    background: #1a1a1f !important;
    border: 1px solid #2a2a2f !important;
    border-radius: 14px !important;
    color: #e8e6e1 !important;
    font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: #c8a96e !important;
    box-shadow: 0 0 0 3px rgba(200,169,110,0.1) !important;
}

/* ── Sidebar suggestion buttons ── */
.stButton > button {
    width: 100%;
    background: #1e1e23 !important;
    border: 1px solid #2a2a2f !important;
    border-radius: 10px !important;
    color: #c5c0b8 !important;
    font-size: 13px !important;
    font-family: 'DM Sans', sans-serif !important;
    padding: 10px 14px !important;
    text-align: left !important;
    line-height: 1.4 !important;
    transition: all 0.2s !important;
    white-space: normal !important;
    height: auto !important;
    margin-bottom: 6px !important;
}
.stButton > button:hover {
    background: #252530 !important;
    border-color: #c8a96e !important;
    color: #e8e6e1 !important;
}

/* ── Divider ── */
hr { border-color: #2a2a2f !important; }
</style>
""", unsafe_allow_html=True)


# =========================================================
# SUGGESTED QUESTIONS
# =========================================================

SUGGESTED_QUESTIONS = [
    "List all the projects Gowtham has worked on",
    "What certifications does Gowtham hold?",
    "Describe Gowtham's leadership experience",
    "What is Gowtham's technical expertise?",
    "Walk me through Gowtham's career timeline",
    "What are Gowtham's future goals and vision?",
    "What makes Gowtham a strong engineering leader?",
    "Has Gowtham worked with AI or LLM technologies?",
]


# =========================================================
# SESSION STATE
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "graph" not in st.session_state:
    st.session_state.graph = ProfileAssistantGraph(
        persist_directory="./chroma_db",
        collection_name="gowtham_profile",
        embedding_model="text-embedding-3-small",
        llm_model="gpt-4o-mini"
    )

if "pending_question" not in st.session_state:
    st.session_state.pending_question = None


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("""
        <div style="padding: 24px 0 8px;">
            <div style="font-family:'DM Serif Display',serif; font-size:18px; color:#e8e6e1;">
                ✦ Ask Gowtham's AI
            </div>
            <div style="font-size:12px; color:#555; margin-top:4px;">
                Powered by RAG + GPT-4o mini
            </div>
        </div>
        <hr/>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div style="font-size:10px; font-weight:500; letter-spacing:0.1em;
                    text-transform:uppercase; color:#444; margin-bottom:10px;">
            Suggested Questions
        </div>
    """, unsafe_allow_html=True)

    for question in SUGGESTED_QUESTIONS:
        if st.button(question, key=f"btn_{question}"):
            st.session_state.pending_question = question

    st.markdown("<hr/>", unsafe_allow_html=True)

    if st.button("🗑  Clear conversation", key="clear"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("""
        <div style="font-size:11px; color:#444; padding-top:16px; line-height:1.6;">
            This AI assistant represents Gowtham Vudaigiri's professional profile.
            Answers are grounded in his resume and experience documents.
        </div>
    """, unsafe_allow_html=True)


# =========================================================
# HEADER
# =========================================================

st.markdown("""
    <div class="profile-header">
        <div class="avatar">G</div>
        <div>
            <div class="profile-name">Gowtham Vudaigiri</div>
            <div class="profile-role">
                <span class="status-dot"></span>
                VP Engineering &nbsp;·&nbsp; Data &amp; BI &nbsp;·&nbsp; 19+ Years
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)


# =========================================================
# WELCOME STATE
# =========================================================

if not st.session_state.messages:
    st.markdown("""
        <div style="text-align:center; padding: 48px 24px 32px;">
            <div style="font-family:'DM Serif Display',serif; font-size:28px;
                        color:#e8e6e1; margin-bottom:12px;">
                How can I help you today?
            </div>
            <div style="font-size:14px; color:#666; max-width:420px;
                        margin:0 auto; line-height:1.7;">
                Ask me anything about Gowtham's projects, technical expertise,
                leadership experience, certifications, or career journey.
            </div>
        </div>
    """, unsafe_allow_html=True)


# =========================================================
# RENDER CHAT HISTORY
# =========================================================

for message in st.session_state.messages:

    role    = message["role"]
    content = message["content"]

    if role == "user":
        st.markdown(f"""
            <div class="msg-wrapper user">
                <div class="msg-icon user">↑</div>
                <div class="msg-bubble user">{content}</div>
            </div>
        """, unsafe_allow_html=True)

    else:
        st.markdown(f"""
            <div class="msg-wrapper assistant">
                <div class="msg-icon assistant">G</div>
                <div class="msg-bubble assistant">{content}</div>
            </div>
        """, unsafe_allow_html=True)


# =========================================================
# HANDLE INPUT — chat input or sidebar button
# =========================================================

user_input = st.chat_input("Ask about Gowtham's experience, skills, projects...")

question = user_input or st.session_state.pending_question

if st.session_state.pending_question:
    st.session_state.pending_question = None

if question:

    # Add user message to history
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    # Render user bubble immediately
    st.markdown(f"""
        <div class="msg-wrapper user">
            <div class="msg-icon user">↑</div>
            <div class="msg-bubble user">{question}</div>
        </div>
    """, unsafe_allow_html=True)

    # Thinking indicator while waiting
    thinking_placeholder = st.empty()
    thinking_placeholder.markdown("""
        <div class="msg-wrapper assistant">
            <div class="msg-icon assistant">G</div>
            <div class="msg-bubble assistant">
                <div class="thinking">
                    <span></span><span></span><span></span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Run the RAG graph
    answer = st.session_state.graph.run(question)

    # Swap thinking for real answer
    thinking_placeholder.empty()

    st.markdown(f"""
        <div class="msg-wrapper assistant">
            <div class="msg-icon assistant">G</div>
            <div class="msg-bubble assistant">{answer}</div>
        </div>
    """, unsafe_allow_html=True)

    # Persist to history
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })