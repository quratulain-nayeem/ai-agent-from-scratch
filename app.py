import json
import re
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain_core.output_parsers import PydanticOutputParser
from langgraph.prebuilt import create_react_agent
from tools import search_tool, wiki_tool, save_tool

load_dotenv()

st.set_page_config(
    page_title="Qurotz.ai",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="collapsed",
)
def is_research_query(query: str) -> bool:
    keywords = [
        "research", "analyze", "explain", "compare",
        "impact", "history", "statistics", "data",
        "sources", "study", "causes", "effects"
    ]
    return any(k in query.lower() for k in keywords)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700;900&family=Rajdhani:wght@300;400;600&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background: #080810 !important;
    color: #e8e0d0 !important;
    font-family: 'Rajdhani', sans-serif;
    overflow-x: hidden !important;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse 70% 50% at 15% 20%, rgba(139,40,100,0.22) 0%, transparent 65%),
        radial-gradient(ellipse 50% 40% at 85% 15%, rgba(107,142,35,0.16) 0%, transparent 60%),
        radial-gradient(ellipse 60% 45% at 90% 75%, rgba(139,40,100,0.14) 0%, transparent 60%),
        radial-gradient(ellipse 55% 40% at 10% 80%, rgba(107,142,35,0.12) 0%, transparent 55%),
        radial-gradient(ellipse 80% 30% at 50% 50%, rgba(100,20,80,0.08) 0%, transparent 70%),
        #080810 !important;
    animation: halo-breathe 8s ease-in-out infinite;
}

@keyframes halo-breathe {
    0%, 100% { filter: brightness(1); }
    50%       { filter: brightness(1.08); }
}

#MainMenu, footer, header, [data-testid="stToolbar"] { visibility: hidden; }
[data-testid="stSidebar"] { display: none; }

.block-container {
    padding: 2rem 3rem !important;
    max-width: 920px !important;
    margin: auto;
}

/* Title wrapper — centers the inline-block span so cursor sits right after text */
.title-wrapper {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-bottom: 0.2rem;
}

.qurotz-title {
    font-family: 'Cinzel', serif;
    font-size: clamp(2.2rem, 5vw, 3.8rem);
    font-weight: 900;
    letter-spacing: 0.15em;
    background: linear-gradient(135deg, #c9547a 0%, #8b2864 35%, #6b8e23 70%, #a0b040 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    filter: drop-shadow(0 0 32px rgba(139,40,100,0.7));
    display: inline-block;
    opacity: 0; /* JS controls reveal — prevents blank-flash on first load */
}

.qurotz-sub {
    font-size: 0.9rem; font-weight: 300; text-align: center;
    color: #7a6e8a; letter-spacing: 0.35em; text-transform: uppercase; margin-bottom: 2rem;
}

.page-halo {
    position: fixed;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%) scale(1);
    width: 100vw; height: 100vh;
    pointer-events: none;
    z-index: 0;
    background: radial-gradient(ellipse 45% 45% at 50% 50%,
        rgba(139,40,100,0.22) 0%,
        rgba(107,142,35,0.07) 45%,
        transparent 70%);
    opacity: 0;
    transition: opacity 1.4s ease;
    will-change: opacity, transform;
}
.page-halo.thinking {
    opacity: 1;
    animation: halo-cinematic 4s ease-in-out infinite;
}
@keyframes halo-cinematic {
    0%, 100% {
        transform: translate(-50%, -50%) scale(1);
        opacity: 0.45;
        filter: blur(0px);
    }
    50% {
        transform: translate(-50%, -50%) scale(1.025);
        opacity: 0.65;
        filter: blur(0.5px);
    }
}

/* ── Strip ALL Streamlit/BaseWeb focus chrome from every wrapper layer ── */
.stTextInput,
.stTextInput > div,
.stTextInput > div > div,
[data-baseweb="input"],
[data-baseweb="base-input"] {
    border: none !important;
    box-shadow: none !important;
    outline: none !important;
    background: transparent !important;
}
[data-baseweb="input"]:focus-within,
.stTextInput > div:focus-within,
.stTextInput > div > div:focus-within {
    border: none !important;
    box-shadow: none !important;
    outline: none !important;
}

/* ── The actual input element ── */
.stTextInput > div > div > input,
[data-baseweb="base-input"] input {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(160,50,90,0.35) !important;
    border-radius: 12px !important;
    color: #e8e0d0 !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 1.05rem !important;
    padding: 0.8rem 1.2rem !important;
    outline: none !important;
    transition: border-color 0.4s ease, box-shadow 0.4s ease !important;
}
.stTextInput > div > div > input:focus,
.stTextInput > div > div > input:focus-visible,
[data-baseweb="base-input"] input:focus,
[data-baseweb="base-input"] input:focus-visible {
    border-color: rgba(200,70,110,0.55) !important;
    box-shadow:
        0 0 0 2px rgba(180,55,100,0.12),
        0 0 20px rgba(180,55,100,0.22),
        0 0 45px rgba(139,40,100,0.14) !important;
    outline: none !important;
}
.stTextInput > div > div > input::placeholder { color: #5a506a !important; }
.stTextInput label { display: none !important; }

.stButton > button {
    background: linear-gradient(135deg, #8b2864, #6b2050) !important;
    color: #f0e8f0 !important;
    border: 1px solid rgba(201,84,122,0.4) !important;
    border-radius: 10px !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 1rem !important; font-weight: 600 !important;
    letter-spacing: 0.12em !important; padding: 0.6rem 2rem !important;
    transition: all 0.25s; text-transform: uppercase;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #c9547a, #8b2864) !important;
    box-shadow: 0 0 25px rgba(139,40,100,0.6) !important;
    transform: translateY(-1px);
}

.chat-human {
    background: rgba(139,40,100,0.12); border: 1px solid rgba(139,40,100,0.25);
    border-radius: 14px 14px 4px 14px; padding: 1rem 1.3rem;
    margin: 1rem 0 1rem 2.5rem; font-size: 1rem; color: #e8d8f0;
    line-height: 1.6;
}
.chat-human::before {
    content: '▸ YOU'; font-size: 0.65rem; font-weight: 700;
    letter-spacing: 0.2em; color: #c9547a; display: block; margin-bottom: 0.45rem;
}
.chat-agent {
    background: rgba(107,142,35,0.08); border: 1px solid rgba(107,142,35,0.2);
    border-radius: 14px 14px 14px 4px; padding: 1rem 1.3rem;
    margin: 1rem 2.5rem 1rem 0; font-size: 1rem; color: #dce8c0;
    line-height: 1.6;
}
.chat-agent::before {
    content: '◈ Q.AI'; font-size: 0.65rem; font-weight: 700;
    letter-spacing: 0.2em; color: #8aaa30; display: block; margin-bottom: 0.45rem;
}

.struct-card {
    background: rgba(255,255,255,0.03); border: 1px solid rgba(139,40,100,0.2);
    border-left: 3px solid #8b2864; border-radius: 10px;
    padding: 1rem 1.3rem; margin-top: 0.6rem; font-size: 0.9rem;
}
.struct-label {
    font-size: 0.65rem; font-weight: 700; letter-spacing: 0.25em;
    text-transform: uppercase; color: #8b2864; margin-bottom: 0.25rem;
}
.struct-value { color: #c8d8a8; margin-bottom: 0.7rem; }
.struct-tag {
    display: inline-block; background: rgba(107,142,35,0.15);
    border: 1px solid rgba(107,142,35,0.3); border-radius: 20px;
    padding: 0.15rem 0.7rem; font-size: 0.78rem; color: #a0b840; margin: 0.15rem 0.2rem;
}

.qdivider {
    border: none; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(139,40,100,0.3), rgba(107,142,35,0.3), transparent);
    margin: 1.5rem 0;
}

.status-thinking {
    text-align: center; font-size: 0.8rem; letter-spacing: 0.3em;
    text-transform: uppercase; color: #c9547a;
    animation: blink 1s ease-in-out infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.2} }
</style>
""", unsafe_allow_html=True)

# ── Enter key support via form ────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "thinking" not in st.session_state:
    st.session_state.thinking = False
if "pending_query" not in st.session_state:
    st.session_state.pending_query = None

class ResearchResponse(BaseModel):
    topic: str
    summary: str
    sources: list[str]
    tools_used: list[str]

@st.cache_resource
def get_agent():
    llm = ChatGroq(model="llama-3.3-70b-versatile")
    return create_react_agent(llm, [search_tool, wiki_tool, save_tool])

parser = PydanticOutputParser(pydantic_object=ResearchResponse)

def _try_parse(raw_text: str) -> ResearchResponse | None:
    """Attempt to extract and parse a ResearchResponse from raw model output."""
    try:
        return parser.parse(raw_text)
    except Exception:
        pass
    stripped = re.sub(r"```(?:json)?", "", raw_text).strip().rstrip("`").strip()
    try:
        return parser.parse(stripped)
    except Exception:
        pass
    try:
        match = re.search(r"\{[\s\S]*\}", raw_text)
        if match:
            data = json.loads(match.group(0))
            return ResearchResponse(
                topic=str(data.get("topic", "")),
                summary=str(data.get("summary", "")),
                sources=[str(s) for s in data.get("sources", [])],
                tools_used=[str(t) for t in data.get("tools_used", [])],
            )
    except Exception:
        pass
    return None

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="title-wrapper"><span class="qurotz-title">QUROTZ.AI</span></div>', unsafe_allow_html=True)
st.markdown('<div class="qurotz-sub">AI Research Intelligence</div>', unsafe_allow_html=True)
if st.session_state.thinking:
    st.markdown('<div class="status-thinking">◈ &nbsp; Researching &nbsp; ◈</div>', unsafe_allow_html=True)

halo_class = "page-halo thinking" if st.session_state.thinking else "page-halo"
st.markdown(f'<div class="{halo_class}"></div>', unsafe_allow_html=True)

st.markdown('<hr class="qdivider">', unsafe_allow_html=True)

# ── Chat history ──────────────────────────────────────────────────────────────
for entry in st.session_state.history:
    st.markdown(f'<div class="chat-human">{entry["query"]}</div>', unsafe_allow_html=True)
    if entry.get("structured"):
        r = entry["structured"]
        tags_sources = "".join(f'<span class="struct-tag">{s}</span>' for s in r.sources)
        tags_tools   = "".join(f'<span class="struct-tag">{t}</span>' for t in r.tools_used)
        st.markdown(f"""
        <div class="chat-agent">
            <div class="struct-card">
                <div class="struct-label">Topic</div>
                <div class="struct-value">{r.topic}</div>
                <div class="struct-label">Summary</div>
                <div class="struct-value">{r.summary}</div>
                <div class="struct-label">Sources</div>
                <div>{tags_sources}</div><br>
                <div class="struct-label">Tools Used</div>
                <div>{tags_tools}</div>
            </div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-agent">{entry["response"]}</div>', unsafe_allow_html=True)

# ── Input (form enables Enter key) ───────────────────────────────────────────
with st.form(key="query_form", clear_on_submit=True):
    col1, col2 = st.columns([5, 1])
    with col1:
        query = st.text_input("query", placeholder="Ask me anything to research...", key="query_input")
    with col2:
        submit = st.form_submit_button("ASK", use_container_width=True)

# ── Typewriter intro + autocomplete-off + smooth open ────────────────────────
components.html("""
<script>
(function () {
    var doc  = window.parent.document;
    var TYPED_KEY = 'qurotz_typed_v3';

    /* ══ 1. SPLASH OVERLAY — hides any white flash on first load ══ */
    var SPLASH_ID = 'qurotz-splash';
    var splash = doc.getElementById(SPLASH_ID);
    var firstLoad = !sessionStorage.getItem(TYPED_KEY);

    if (!splash) {
        splash = doc.createElement('div');
        splash.id = SPLASH_ID;
        Object.assign(splash.style, {
            position: 'fixed', inset: '0',
            background: '#080810',
            zIndex: '99999',
            pointerEvents: 'none',
            opacity: firstLoad ? '1' : '0',
            transition: 'opacity 0.75s ease'
        });
        doc.body.appendChild(splash);
    }

    /* ══ 2. AUTOCOMPLETE OFF — targets input + every parent form ══ */
    function killAutocomplete() {
        doc.querySelectorAll('input[type="text"], .stTextInput input').forEach(function (el) {
            el.setAttribute('autocomplete', 'off');
            el.setAttribute('name', 'qurotz_nac');
        });
        doc.querySelectorAll('form').forEach(function (f) {
            f.setAttribute('autocomplete', 'off');
        });
    }
    killAutocomplete();
    setTimeout(killAutocomplete, 500);
    setTimeout(killAutocomplete, 1500);

    /* ══ 3. TITLE REVEAL — instant on re-renders, typed on first load ══ */
    function revealTitle() {
        var el = doc.querySelector('.qurotz-title');
        if (!el) { setTimeout(revealTitle, 60); return; }

        if (!firstLoad) {
            /* Re-render: show title immediately, keep splash gone */
            el.style.opacity = '1';
            splash.style.opacity = '0';
            return;
        }

        /* ── First load: full typewriter sequence ── */
        sessionStorage.setItem(TYPED_KEY, '1');

        var full        = 'QUROTZ.AI';
        var speed       = 110;
        var cursorColor = 'rgba(201,84,122,0.95)';

        el.textContent    = '';
        el.style.opacity  = '1';
        el.style.borderRight  = '3px solid ' + cursorColor;
        el.style.paddingRight = '3px';

        /* Fade splash out just before first character appears */
        setTimeout(function () { splash.style.opacity = '0'; }, 80);

        /* Blinking cursor during typing */
        var cursorOn = true;
        var cursorTimer = setInterval(function () {
            cursorOn = !cursorOn;
            el.style.borderRightColor = cursorOn ? cursorColor : 'transparent';
        }, 520);

        var i = 0;
        var typeTimer = setInterval(function () {
            el.textContent = full.slice(0, ++i);
            if (i === full.length) {
                clearInterval(typeTimer);
                /* Blink for 3.5 s, then slowly dissolve over 2 s */
                setTimeout(function () {
                    clearInterval(cursorTimer);
                    el.style.borderRightColor = 'rgba(201,84,122,0.95)'; /* solid before fade */
                    el.style.transition = 'border-right-color 2s ease';
                    el.style.borderRightColor = 'transparent';
                    setTimeout(function () {
                        el.style.borderRight  = 'none';
                        el.style.paddingRight = '0';
                    }, 2100);
                }, 3500);
            }
        }, speed);
    }

    setTimeout(revealTitle, 180);
})();
</script>
""", height=0)

# ── Run agent ─────────────────────────────────────────────────────────────────
if submit and query.strip():
    st.session_state.pending_query = query
    st.session_state.thinking = True
    st.rerun()

if st.session_state.thinking and st.session_state.pending_query:
    last_query = st.session_state.pending_query

    with st.spinner(""):
        try:
            if is_research_query(last_query):
                # Research mode
                agent = get_agent()
                system_prompt = (
                    "You are Q.AI, an elite research intelligence.\n"
                    "If the query requires research:\n"
                    "- Use tools if needed.\n"
                    "- Return ONLY valid JSON matching this schema.\n"
                    f"{parser.get_format_instructions()}\n"
                    "Do not include any extra text."
                )

                raw = agent.invoke({
                    "messages": [
                        ("system", system_prompt),
                        ("human", last_query)
                    ]
                })

                final_msg = None
                for msg in reversed(raw["messages"]):
                    if msg.type == "ai":
                        final_msg = msg.content
                        break

                structured = _try_parse(final_msg)

                if structured:
                    st.session_state.history.append({
                        "query": last_query,
                        "structured": structured,
                        "response": None
                    })
                else:
                    st.session_state.history.append({
                        "query": last_query,
                        "structured": None,
                        "response": "I could not structure the research response. Please try again."
                    })

            else:
                # Conversational mode
                llm = ChatGroq(model="llama-3.3-70b-versatile")
                response = llm.invoke(last_query)

                st.session_state.history.append({
                    "query": last_query,
                    "structured": None,
                    "response": response.content
                })

        except Exception as e:
            st.session_state.history.append({
                "query": last_query,
                "structured": None,
                "response": f"Error: {str(e)}"
            })

    st.session_state.thinking = False
    st.session_state.pending_query = None
    st.rerun()
