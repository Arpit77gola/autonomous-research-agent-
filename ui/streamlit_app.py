import os
import sys
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Research Agent",
    page_icon="🔭",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Fira+Code:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif;
}

.stApp {
    background: #07090f;
    color: #e2e8f0;
}

/* hide streamlit default chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem; padding-bottom: 4rem; max-width: 700px; }

/* top gold line */
.stApp::before {
    content: '';
    position: fixed; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, #f5c842, transparent);
    z-index: 999;
}

/* header */
.ra-header {
    text-align: center;
    padding: 2rem 0 2.5rem;
}
.ra-logo {
    width: 64px; height: 64px;
    border-radius: 50%;
    border: 1.5px solid #c49a1a;
    display: flex; align-items: center; justify-content: center;
    margin: 0 auto 1rem;
    font-size: 26px;
    background: #0c101a;
}
.ra-title {
    font-size: 30px; font-weight: 700;
    color: #e2e8f0; margin-bottom: 6px;
}
.ra-title span { color: #f5c842; }
.ra-tag {
    font-family: 'Fira Code', monospace;
    font-size: 12px; color: #64748b;
    letter-spacing: .08em;
}

/* section label */
.sec-lbl {
    font-family: 'Fira Code', monospace;
    font-size: 10px; font-weight: 500;
    letter-spacing: .14em; text-transform: uppercase;
    color: #c49a1a; margin-bottom: 8px; margin-top: 24px;
}

/* pipeline */
.pipeline {
    display: flex; gap: 8px;
    margin: 1.5rem 0;
}
.pip {
    flex: 1; text-align: center;
    background: #111827;
    border: 1px solid rgba(255,255,255,.07);
    border-radius: 10px;
    padding: 10px 4px;
    font-size: 11px; font-weight: 600;
    color: #64748b;
    transition: all .3s;
}
.pip.active { border-color: rgba(245,200,66,.5); color: #f5c842; background: rgba(245,200,66,.05); }
.pip.done   { border-color: rgba(34,211,165,.4);  color: #22d3a5; background: rgba(34,211,165,.05); }
.pip-icon   { font-size: 16px; display: block; margin-bottom: 4px; }

/* log box */
.log-box {
    background: #111827;
    border: 1px solid rgba(255,255,255,.07);
    border-radius: 14px;
    padding: 14px 18px;
    font-family: 'Fira Code', monospace;
    font-size: 12px; line-height: 2;
    max-height: 220px; overflow-y: auto;
    margin-bottom: 1rem;
}

/* report box */
.report-box {
    background: #111827;
    border: 1px solid rgba(255,255,255,.15);
    border-radius: 14px;
    padding: 24px;
    margin-bottom: 1rem;
    line-height: 1.8;
}
.report-box h1 { font-size: 22px; font-weight: 700; color: #e2e8f0; border-bottom: 1px solid rgba(255,255,255,.07); padding-bottom: 12px; margin-bottom: 16px; }
.report-box h2 { font-size: 15px; font-weight: 600; color: #f5c842; margin: 20px 0 8px; padding-left: 10px; border-left: 2px solid #c49a1a; }
.report-box h3 { font-size: 13px; font-weight: 600; color: #e2e8f0; margin: 14px 0 6px; }
.report-box p  { color: #94a3b8; font-size: 14px; margin-bottom: 8px; }
.report-box li { color: #94a3b8; font-size: 14px; margin-bottom: 4px; }
.report-box a  { color: #f5c842; text-decoration: none; }

/* pdf card */
.pdf-card {
    background: #111827;
    border: 1px solid rgba(255,255,255,.07);
    border-radius: 14px;
    padding: 18px 20px;
    display: flex; align-items: center; gap: 16px;
    margin-bottom: 1rem;
}
.pdf-icon {
    width: 44px; height: 44px; border-radius: 10px;
    background: rgba(245,200,66,.1);
    border: 1px solid rgba(245,200,66,.2);
    display: flex; align-items: center; justify-content: center;
    font-size: 22px; flex-shrink: 0;
}

/* streamlit widget overrides */
.stTextArea textarea {
    background: #111827 !important;
    border: 1px solid rgba(255,255,255,.15) !important;
    border-radius: 14px !important;
    color: #e2e8f0 !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 15px !important;
}
.stTextArea textarea:focus {
    border-color: rgba(245,200,66,.5) !important;
    box-shadow: none !important;
}
.stTextInput input {
    background: #111827 !important;
    border: 1px solid rgba(255,255,255,.15) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    font-family: 'Space Grotesk', sans-serif !important;
}
.stTextInput input:focus {
    border-color: rgba(245,200,66,.5) !important;
    box-shadow: none !important;
}
.stButton > button {
    width: 100%;
    background: #f5c842 !important;
    color: #0a0700 !important;
    border: none !important;
    border-radius: 12px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 700 !important;
    font-size: 15px !important;
    padding: 14px !important;
    transition: opacity .2s !important;
}
.stButton > button:hover { opacity: .88 !important; }

.stDownloadButton > button {
    background: #f5c842 !important;
    color: #0a0700 !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 700 !important;
}

div[data-testid="stExpander"] {
    background: #111827 !important;
    border: 1px solid rgba(255,255,255,.15) !important;
    border-radius: 14px !important;
}
div[data-testid="stExpander"] summary {
    color: #22d3a5 !important;
    font-weight: 600 !important;
}

.stSuccess { background: rgba(34,211,165,.08) !important; border: 1px solid rgba(34,211,165,.3) !important; color: #22d3a5 !important; border-radius: 10px !important; }
.stError   { background: rgba(248,113,113,.08) !important; border: 1px solid rgba(248,113,113,.3) !important; border-radius: 10px !important; }
</style>
""", unsafe_allow_html=True)


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="ra-header">
  <div class="ra-logo">🔭</div>
  <div class="ra-title">Research <span>Agent</span></div>
  <div class="ra-tag">// autonomous · multi-step · self-critiquing</div>
</div>
""", unsafe_allow_html=True)


# ── Session state ─────────────────────────────────────────────────────────────
for k, v in [("report",""), ("pdf_bytes",None), ("pdf_name",""), ("logs",[]), ("ran",False)]:
    if k not in st.session_state:
        st.session_state[k] = v


# ── Ask anything ──────────────────────────────────────────────────────────────
st.markdown('<div class="sec-lbl">Ask anything</div>', unsafe_allow_html=True)
query = st.text_area("", placeholder="e.g. What is the future of AI in healthcare?",
                     height=100, label_visibility="collapsed")

run_clicked = st.button("▶  Run Research")


# ── Pipeline display ──────────────────────────────────────────────────────────
def pipeline_html(states):
    steps = [("🗺","Planner"),("🔍","Researcher"),("🧠","Critic"),("✍","Writer")]
    cols = ""
    for i,(icon,label) in enumerate(steps):
        cls = "pip " + states.get(label.lower(), "")
        cols += f'<div class="{cls}"><span class="pip-icon">{icon}</span>{label}</div>'
    return f'<div class="pipeline">{cols}</div>'

pip_placeholder = st.empty()
pip_placeholder.markdown(pipeline_html({}), unsafe_allow_html=True)


# ── Run research ──────────────────────────────────────────────────────────────
if run_clicked and query.strip():
    st.session_state.report   = ""
    st.session_state.pdf_bytes = None
    st.session_state.logs     = []
    st.session_state.ran      = False

    from graph.state import ResearchState
    from graph.graph import research_graph

    log_placeholder = st.empty()
    pip_states      = {}

    class LogCapture:
        def __init__(self):
            self.buf = []
        def write(self, text):
            if text.strip():
                t = text.strip()
                self.buf.append(t)
                tl = t.lower()
                if "[planner]"    in tl: pip_states.update({"planner":"active"})
                if "[researcher]" in tl: pip_states.update({"planner":"done","researcher":"active"})
                if "[critic]"     in tl: pip_states.update({"researcher":"done","critic":"active"})
                if "[writer]"     in tl: pip_states.update({"critic":"done","writer":"active"})

                pip_placeholder.markdown(pipeline_html(pip_states), unsafe_allow_html=True)

                log_html = "<div class='log-box'>" + "<br>".join(
                    f"<span style='color:#94a3b8'>{l}</span>" for l in self.buf[-30:]
                ) + "</div>"
                log_placeholder.markdown(log_html, unsafe_allow_html=True)
        def flush(self): pass

    capture = LogCapture()
    old_stdout = sys.stdout
    sys.stdout = capture

    try:
        initial_state = ResearchState(query=query)
        result = research_graph.invoke(initial_state, {"recursion_limit": 50})
        st.session_state.report = result.get("final_report", "")
        st.session_state.ran    = True

        # Mark all done
        pip_states = {"planner":"done","researcher":"done","critic":"done","writer":"done"}
        pip_placeholder.markdown(pipeline_html(pip_states), unsafe_allow_html=True)

        # Load PDF bytes for download
        safe_name = "".join(c if c.isalnum() or c in " _-" else "_" for c in query[:50])
        pdf_path  = os.path.join(os.getenv("OUTPUT_DIR","output"), f"{safe_name}.pdf")
        if os.path.exists(pdf_path):
            with open(pdf_path,"rb") as f:
                st.session_state.pdf_bytes = f.read()
            st.session_state.pdf_name = f"{safe_name}.pdf"

    except Exception as e:
        st.error(f"Error: {e}")
    finally:
        sys.stdout = old_stdout

elif run_clicked:
    st.warning("Please enter a research question.")


# ── Results ───────────────────────────────────────────────────────────────────
if st.session_state.ran and st.session_state.report:

    st.markdown('<div class="sec-lbl">Report</div>', unsafe_allow_html=True)
    with st.expander("✅ Research complete — click to view", expanded=False):
        import re
        def md2html(md):
            h = md
            h = re.sub(r'^### (.+)$', r'<h3>\1</h3>', h, flags=re.MULTILINE)
            h = re.sub(r'^## (.+)$',  r'<h2>\1</h2>', h, flags=re.MULTILINE)
            h = re.sub(r'^# (.+)$',   r'<h1>\1</h1>', h, flags=re.MULTILINE)
            h = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', h)
            h = re.sub(r'^\* (.+)$',  r'<li>\1</li>', h, flags=re.MULTILINE)
            h = re.sub(r'^- (.+)$',   r'<li>\1</li>', h, flags=re.MULTILINE)
            h = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2" target="_blank">\1</a>', h)
            h = re.sub(r'(<li>.*?</li>\n?)+', lambda m: f'<ul>{m.group(0)}</ul>', h, flags=re.DOTALL)
            lines = []
            for line in h.split('\n'):
                line = line.strip()
                if not line: continue
                if line.startswith('<'): lines.append(line)
                else: lines.append(f'<p>{line}</p>')
            return '\n'.join(lines)

        st.markdown(f'<div class="report-box">{md2html(st.session_state.report)}</div>',
                    unsafe_allow_html=True)

    # PDF download
    if st.session_state.pdf_bytes:
        st.markdown('<div class="sec-lbl">PDF Report</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="pdf-card">
          <div class="pdf-icon">📄</div>
          <div><div style="font-size:13px;font-weight:600;color:#e2e8f0">Report ready</div>
          <div style="font-size:11px;font-family:monospace;color:#64748b;margin-top:2px">Click to download PDF</div></div>
        </div>""", unsafe_allow_html=True)
        st.download_button(
            label="⬇  Download PDF",
            data=st.session_state.pdf_bytes,
            file_name=st.session_state.pdf_name,
            mime="application/pdf",
        )

    # Email
    st.markdown('<div class="sec-lbl">Send via Email</div>', unsafe_allow_html=True)
    with st.container():
        st.markdown("""
        <div style="background:#111827;border:1px solid rgba(255,255,255,.07);
             border-radius:14px;padding:18px 20px;margin-bottom:8px">
          <div style="font-size:13px;font-weight:600;color:#e2e8f0;margin-bottom:4px">Email this report</div>
          <div style="font-family:monospace;font-size:11px;color:#64748b">PDF will be attached automatically</div>
        </div>""", unsafe_allow_html=True)

        email_to = st.text_input("", placeholder="recipient@example.com",
                                 label_visibility="collapsed")
        if st.button("✉  Send Report"):
            if not email_to:
                st.error("Enter an email address")
            else:
                from utils.email_sender import send_report_email
                safe_name = "".join(c if c.isalnum() or c in " _-" else "_" for c in query[:50])
                pdf_path  = os.path.join(os.getenv("OUTPUT_DIR","output"), f"{safe_name}.pdf")
                ok = send_report_email(
                    to_email  = email_to,
                    subject   = f"Research Report: {query}",
                    report_md = st.session_state.report,
                    pdf_path  = pdf_path if os.path.exists(pdf_path) else None,
                )
                if ok:
                    st.success(f"✅ Report sent to {email_to}")
                else:
                    st.error("Failed — check GMAIL credentials in .env")