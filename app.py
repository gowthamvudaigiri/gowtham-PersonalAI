from html import escape

from markdown_it import MarkdownIt
import streamlit as st

from graph import ProfileAssistantGraph


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Gowtham Vudaigiri - AI Profile",
    page_icon=":briefcase:",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# STYLES
# =========================================================

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

:root {
    --navy: #101827;
    --navy-soft: #1f2a44;
    --accent: #2f6fed;
    --accent-soft: #e8f0ff;
    --teal: #0f766e;
    --teal-soft: #e6f6f4;
    --ink-900: #0f172a;
    --ink-700: #334155;
    --ink-500: #64748b;
    --line: #e2e8f0;
    --line-strong: #cbd5e1;
    --surface: #ffffff;
    --surface-muted: #f8fafc;
    --page: #f3f6fb;
}

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: var(--page);
    color: var(--ink-900);
}

#MainMenu, footer { visibility: hidden; }

.block-container {
    padding: 1.2rem 2rem 6.5rem;
    max-width: 1180px;
}

[data-testid="stAppViewContainer"] {
    background: #eef2f7;
}

[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid var(--line);
    box-shadow: 8px 0 30px rgba(15, 23, 42, 0.04);
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label {
    color: var(--ink-700) !important;
}

[data-testid="stSidebar"] hr {
    border: 0;
    border-top: 1px solid var(--line);
    margin: 16px 0;
}

.sidebar-brand {
    padding: 10px 0 2px;
}

.sidebar-title {
    font-size: 17px;
    font-weight: 700;
    color: var(--ink-900);
    letter-spacing: 0;
}

.sidebar-subtitle {
    font-size: 12.5px;
    color: var(--ink-500);
    margin-top: 4px;
}

.sidebar-label {
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    color: var(--ink-500);
    margin-bottom: 9px;
    letter-spacing: 0;
}

.sidebar-note {
    font-size: 12.5px;
    color: var(--ink-500);
    padding: 2px 2px 0;
    line-height: 1.55;
}

.app-hero {
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto;
    gap: 22px;
    align-items: end;
    padding: 28px 30px;
    background: var(--navy);
    border: 1px solid rgba(255, 255, 255, 0.10);
    border-radius: 10px;
    box-shadow: 0 18px 48px rgba(15, 23, 42, 0.16);
    margin-bottom: 18px;
}

.app-kicker {
    color: #8bd2c9;
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0;
    margin-bottom: 9px;
}

.app-title {
    color: #ffffff;
    font-size: 34px;
    font-weight: 700;
    line-height: 1.08;
    margin: 0;
}

.app-copy {
    color: #cbd5e1;
    font-size: 14.5px;
    line-height: 1.65;
    max-width: 680px;
    margin-top: 12px;
}

.hero-badge {
    min-width: 210px;
    padding: 16px;
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.14);
    border-radius: 8px;
}

.hero-badge-label {
    color: #94a3b8;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0;
}

.hero-badge-value {
    color: #ffffff;
    font-size: 24px;
    font-weight: 700;
    margin-top: 6px;
}

.hero-badge-note {
    color: #cbd5e1;
    font-size: 12.5px;
    margin-top: 4px;
}

.insight-strip {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 12px;
    margin-bottom: 22px;
}

.insight-card {
    background: #ffffff;
    border: 1px solid var(--line);
    border-radius: 8px;
    padding: 14px 15px;
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.045);
}

.insight-label {
    color: var(--ink-500);
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0;
}

.insight-value {
    color: var(--ink-900);
    font-size: 17px;
    font-weight: 700;
    margin-top: 6px;
}

.profile-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 10px;
}

.profile-pill {
    display: inline-flex;
    align-items: center;
    min-height: 26px;
    padding: 4px 9px;
    border: 1px solid var(--line);
    border-radius: 999px;
    background: var(--surface-muted);
    color: var(--ink-500);
    font-size: 12px;
    font-weight: 500;
}

.profile-header {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 16px 18px;
    background: rgba(255, 255, 255, 0.94);
    border: 1px solid var(--line);
    border-radius: 8px;
    box-shadow: 0 12px 28px rgba(15, 23, 42, 0.06);
    margin-bottom: 22px;
}

.avatar {
    width: 46px;
    height: 46px;
    border-radius: 50%;
    background: var(--navy);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 15px;
    font-weight: 700;
    color: #ffffff;
    flex-shrink: 0;
    box-shadow: 0 8px 18px rgba(23, 32, 51, 0.18);
}

.profile-name {
    font-size: 22px;
    font-weight: 700;
    color: var(--ink-900);
    margin: 0;
    line-height: 1.2;
}

.profile-role {
    font-size: 13px;
    color: var(--ink-500);
    margin: 4px 0 0;
}

.status-dot {
    width: 8px;
    height: 8px;
    background: var(--teal);
    border-radius: 50%;
    display: inline-block;
    margin-right: 7px;
    box-shadow: 0 0 0 4px rgba(15, 118, 110, 0.12);
}

.welcome-panel {
    text-align: left;
    padding: 12px 4px 18px;
    color: var(--ink-900);
}

.welcome-title {
    font-size: 22px;
    font-weight: 700;
    margin-bottom: 8px;
}

.welcome-copy {
    font-size: 15px;
    color: var(--ink-500);
    max-width: 560px;
    margin: 0;
    line-height: 1.65;
}

.starter-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 12px;
    margin: 14px 0 24px;
}

.starter-item {
    min-height: 86px;
    padding: 13px 14px;
    background: #ffffff;
    border: 1px solid var(--line);
    border-radius: 8px;
    color: var(--ink-700);
    font-size: 13px;
    line-height: 1.45;
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.04);
}

@media (max-width: 900px) {
    .app-hero {
        grid-template-columns: 1fr;
        padding: 24px;
    }

    .insight-strip,
    .starter-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}

@media (max-width: 640px) {
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .app-title {
        font-size: 28px;
    }

    .insight-strip,
    .starter-grid {
        grid-template-columns: 1fr;
    }

    .profile-header {
        align-items: flex-start;
    }

    .profile-name {
        font-size: 20px;
    }

    .msg-bubble {
        max-width: 90%;
    }
}

.msg-wrapper {
    display: flex;
    gap: 12px;
    margin-bottom: 16px;
    animation: fadeUp 0.18s ease;
}

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
}

.msg-wrapper.user { flex-direction: row-reverse; }

.msg-icon {
    width: 34px;
    height: 34px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: 700;
    flex-shrink: 0;
    margin-top: 2px;
}

.msg-icon.assistant {
    background: var(--navy);
    color: #ffffff;
}

.msg-icon.user {
    background: var(--accent-soft);
    color: var(--accent);
}

.msg-bubble {
    max-width: min(86%, 720px);
    padding: 13px 15px;
    border-radius: 8px;
    font-size: 14.5px;
    line-height: 1.62;
    box-shadow: 0 6px 18px rgba(15, 23, 42, 0.045);
}

.msg-bubble.assistant {
    background: var(--surface);
    border: 1px solid var(--line);
    border-top-left-radius: 3px;
    color: var(--ink-900);
}

.msg-bubble.assistant p {
    margin: 0 0 10px;
}

.msg-bubble.assistant p:last-child {
    margin-bottom: 0;
}

.msg-bubble.assistant ul,
.msg-bubble.assistant ol {
    margin: 8px 0 10px 20px;
    padding: 0;
}

.msg-bubble.assistant li {
    margin: 4px 0;
}

.msg-bubble.assistant strong {
    font-weight: 700;
    color: var(--ink-900);
}

.msg-bubble.assistant a {
    color: var(--accent);
    font-weight: 600;
    text-decoration: none;
}

.msg-bubble.assistant a:hover {
    text-decoration: underline;
}

.msg-bubble.assistant code {
    background: var(--surface-muted);
    border: 1px solid var(--line);
    border-radius: 4px;
    padding: 1px 5px;
    font-size: 13px;
}

.msg-bubble.user {
    background: var(--accent);
    color: #ffffff;
    border-top-right-radius: 3px;
    font-weight: 500;
}

.thinking {
    display: flex;
    gap: 5px;
    align-items: center;
    padding: 4px 2px;
}

.thinking span {
    width: 7px;
    height: 7px;
    background: var(--accent);
    border-radius: 50%;
    animation: pulse 1.2s ease-in-out infinite;
}

.thinking span:nth-child(2) { animation-delay: 0.2s; }
.thinking span:nth-child(3) { animation-delay: 0.4s; }

@keyframes pulse {
    0%, 60%, 100% { opacity: 0.2; transform: scale(0.85); }
    30% { opacity: 1; transform: scale(1); }
}

[data-testid="stChatInput"] textarea {
    background: #ffffff !important;
    border: 1px solid var(--line-strong) !important;
    border-radius: 8px !important;
    color: var(--ink-900) !important;
    font-family: 'Inter', sans-serif !important;
    box-shadow: 0 10px 28px rgba(15, 23, 42, 0.08) !important;
}

[data-testid="stChatInput"] textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.14) !important;
}

.stButton > button {
    width: 100%;
    background: transparent !important;
    border: 1px solid transparent !important;
    border-radius: 8px !important;
    color: var(--ink-700) !important;
    font-size: 13px !important;
    font-family: 'Inter', sans-serif !important;
    padding: 9px 10px !important;
    text-align: left !important;
    line-height: 1.38 !important;
    transition: all 0.2s !important;
    white-space: normal !important;
    height: auto !important;
    margin-bottom: 4px !important;
    box-shadow: none !important;
}

.stButton > button:hover {
    background: var(--surface-muted) !important;
    border-color: var(--line) !important;
    color: var(--ink-900) !important;
}

[data-testid="stSidebar"] .stButton > button:hover *,
[data-testid="stSidebar"] .stButton > button:focus *,
[data-testid="stSidebar"] .stButton > button:active * {
    color: var(--ink-900) !important;
}

.stButton > button:active {
    background: var(--accent-soft) !important;
}

hr { border-color: var(--line) !important; }
</style>
""",
    unsafe_allow_html=True,
)


# =========================================================
# SUGGESTED QUESTIONS
# =========================================================

SUGGESTED_QUESTIONS = [
    "List all the projects Gowtham has worked on",
    "What certifications does Gowtham hold?",
    "Describe Gowtham's leadership experience",
    "What is Gowtham's technical expertise?",
    "Walk me through Gowtham's career timeline",
    "What makes Gowtham a strong engineering leader?",
    "Has Gowtham worked with AI or LLM technologies?",
]


# =========================================================
# SESSION STATE
# =========================================================

MARKDOWN_RENDERER = MarkdownIt(
    "commonmark",
    {
        "breaks": True,
        "html": False,
    },
)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "graph" not in st.session_state:
    st.session_state.graph = ProfileAssistantGraph(
        persist_directory="./chroma_db",
        collection_name="gowtham_profile",
        embedding_model="text-embedding-3-small",
        llm_model="gpt-4o-mini",
    )

if "pending_question" not in st.session_state:
    st.session_state.pending_question = None


def queue_sidebar_question(question: str) -> None:
    st.session_state.pending_question = question


def render_message(role: str, content: str) -> None:
    if role == "user":
        safe_content = escape(content).replace("\n", "<br>")
        st.markdown(
            f"""
            <div class="msg-wrapper user">
                <div class="msg-icon user">You</div>
                <div class="msg-bubble user">{safe_content}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    rendered_content = MARKDOWN_RENDERER.render(content)

    st.markdown(
        f"""
        <div class="msg-wrapper assistant">
            <div class="msg-icon assistant">GV</div>
            <div class="msg-bubble assistant">{rendered_content}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="sidebar-title">Gowtham AI Assistant</div>
            <div class="sidebar-subtitle">Professional profile Q&A</div>
        </div>
        <hr/>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sidebar-label">Suggested questions</div>',
        unsafe_allow_html=True,
    )

    for index, question in enumerate(SUGGESTED_QUESTIONS):
        st.button(
            question,
            key=f"suggested_question_{index}",
            on_click=queue_sidebar_question,
            args=(question,),
        )

    st.markdown("<hr/>", unsafe_allow_html=True)

    if st.button("Clear conversation", key="clear_conversation"):
        st.session_state.messages = []
        st.session_state.pending_question = None
        st.rerun()

    st.markdown(
        """
        <div class="sidebar-note">
            Answers are grounded in Gowtham Vudaigiri's professional profile,
            project history, leadership background, and experience documents.
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# HEADER
# =========================================================

st.markdown(
    """
    <div class="app-hero">
        <div>
            <div class="app-kicker">Executive Profile Intelligence</div>
            <div class="app-title">Gowtham Vudaigiri</div>
            <div class="app-copy">
                Ask focused questions across leadership, BI delivery, data engineering,
                cloud migration, certifications, and project history.
            </div>
            <div class="profile-meta">
                <span class="profile-pill">Executive Profile</span>
                <span class="profile-pill">RAG Assistant</span>
                <span class="profile-pill">Chennai, India</span>
            </div>
        </div>
        <div class="hero-badge">
            <div class="hero-badge-label">Experience</div>
            <div class="hero-badge-value">19+ years</div>
            <div class="hero-badge-note">Data, BI, engineering leadership</div>
        </div>
    </div>
    <div class="insight-strip">
        <div class="insight-card">
            <div class="insight-label">Current Role</div>
            <div class="insight-value">VP Engineering</div>
        </div>
        <div class="insight-card">
            <div class="insight-label">Core Domain</div>
            <div class="insight-value">Data & BI</div>
        </div>
        <div class="insight-card">
            <div class="insight-label">Platforms</div>
            <div class="insight-value">Azure, Snowflake</div>
        </div>
        <div class="insight-card">
            <div class="insight-label">Assistant Mode</div>
            <div class="insight-value">Grounded Q&A</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# WELCOME STATE
# =========================================================

STARTER_QUESTIONS = [
    "Compare Gowtham's leadership experience with his technical delivery depth.",
    "Summarize Gowtham's major BI, data platform, and AI projects.",
    "Identify Gowtham's certifications and domain strengths.",
    "Create a concise executive profile narrative for Gowtham.",
]

if not st.session_state.messages:
    st.markdown(
        """
        <div class="welcome-panel">
            <div class="welcome-title">How can I help you today?</div>
            <div class="welcome-copy">
                Ask about Gowtham's projects, technical expertise, leadership
                experience, certifications, or career journey.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    starter_cols = st.columns(4)
    for col, question in zip(starter_cols, STARTER_QUESTIONS):
        with col:
            st.button(
                question,
                key=f"starter_{question[:30]}",
                on_click=queue_sidebar_question,
                args=(question,),
                use_container_width=True,
            )


# =========================================================
# RENDER CHAT HISTORY
# =========================================================

for message in st.session_state.messages:
    render_message(message["role"], message["content"])


# =========================================================
# HANDLE INPUT - chat input or sidebar button
# =========================================================

user_input = st.chat_input("Ask about Gowtham's experience, skills, projects...")
question = user_input or st.session_state.pending_question

if question:
    question = question.strip()

    if not question:
        st.warning("Please enter a question.")
    elif len(question) > 1000:
        st.warning("Please keep your question under 1000 characters.")
    else:
        st.session_state.pending_question = None

        st.session_state.messages.append({"role": "user", "content": question})
        render_message("user", question)

        answer = None
        try:
            answer_container = st.empty()
            answer_container.markdown(
                """
                <div class="msg-wrapper assistant">
                    <div class="msg-icon assistant">GV</div>
                    <div class="msg-bubble assistant">
                        <div class="thinking">
                            <span></span><span></span><span></span>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            chunks = []
            for chunk in st.session_state.graph.stream(question):
                chunks.append(chunk)
                partial = "".join(chunks)
                rendered = MARKDOWN_RENDERER.render(partial)
                answer_container.markdown(
                    f"""
                    <div class="msg-wrapper assistant">
                        <div class="msg-icon assistant">GV</div>
                        <div class="msg-bubble assistant">{rendered}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            answer = "".join(chunks)
        except Exception:
            answer_container.empty()
            st.session_state.messages.pop()
            st.error("Something went wrong. Please try again in a moment.")

        if answer:
            st.session_state.messages.append({"role": "assistant", "content": answer})
