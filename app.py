"""
last30days – Simple Streamlit UI

Share the last30days research tool with your team. Enter a topic, run research,
and see Reddit + X results from the last 30 days.
"""

import io
import os
import subprocess
import sys
from pathlib import Path

import streamlit as st


def _offer_docx_download(content: str, base_name: str) -> None:
    """Offer Word (.docx) download if python-docx is available."""
    try:
        from docx import Document
        from docx.shared import Pt
        doc = Document()
        for block in content.split("\n\n"):
            block = block.strip()
            if block:
                doc.add_paragraph(block)
        buf = io.BytesIO()
        doc.save(buf)
        buf.seek(0)
        st.download_button(
            "📘 Word (.docx)",
            data=buf.getvalue(),
            file_name=f"{base_name}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            key="dl_docx",
        )
    except ImportError:
        st.caption("Word: install python-docx")


def _offer_pdf_download(content: str, base_name: str) -> None:
    """Offer PDF download if fpdf2 is available."""
    try:
        from fpdf import FPDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=10)
        for line in content.replace("\r", "").split("\n"):
            line = line.replace("**", "").strip()
            if line:
                pdf.multi_cell(0, 6, line)
        pdf_bytes = pdf.output()
        st.download_button(
            "📕 PDF",
            data=pdf_bytes,
            file_name=f"{base_name}.pdf",
            mime="application/pdf",
            key="dl_pdf",
        )
    except ImportError:
        st.caption("PDF: install fpdf2")

# Project root (directory containing app.py and scripts/)
PROJECT_ROOT = Path(__file__).resolve().parent
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "last30days.py"

# Same path as last30days script
ENV_FILE = Path.home() / ".config" / "last30days" / ".env"


def _load_env_file():
    """Load ~/.config/last30days/.env into os.environ so API keys are available."""
    if not ENV_FILE.exists():
        return
    try:
        with open(ENV_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, _, value = line.partition("=")
                    key = key.strip()
                    value = value.strip()
                    if value and value[0] in ('"', "'") and value[-1] == value[0]:
                        value = value[1:-1]
                    if key and value:
                        os.environ[key] = value
    except Exception:
        pass


# Load .env first so keys from file are available; Streamlit secrets can override
def _inject_secrets_into_env():
    _load_env_file()
    try:
        secrets = st.secrets
        if hasattr(secrets, "get") and callable(secrets.get):
            for key in ("OPENAI_API_KEY", "XAI_API_KEY", "ANTHROPIC_API_KEY"):
                val = secrets.get(key)
                if val:
                    os.environ[key] = str(val)
    except Exception:
        pass


def _generate_with_claude(report_text: str) -> tuple[str | None, str | None]:
    """
    Call Claude to fill in Best Practices and Prompt Pack. Returns (completed_report, error).
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None, "ANTHROPIC_API_KEY not set. Add it in ~/.config/last30days/.env or Streamlit secrets to use Claude."

    try:
        import anthropic
    except ImportError:
        return None, "Install the anthropic package: pip install anthropic"

    prompt = """You are given a research report from Reddit and X (last 30 days). The report may contain placeholder sections "Best Practices" and "Prompt Pack" that say things like "To be synthesized by Claude" or "Use the research above to...".

Your task: Output the **complete** report in markdown, but replace those two sections with real content:

1. **Best Practices** – A concise bullet list of best practices derived from the research (what actually works, what to avoid). Use the threads and posts as evidence.

2. **Prompt Pack** – 2–4 copy-paste-ready prompts that a reader could use (e.g. for an AI tool, a campaign, or the topic at hand), based on the research.

Keep all other content unchanged (headers, Reddit/X items, links, date range, etc.). Output only the full markdown report, no preamble or explanation."""

    try:
        # Valid model IDs per Anthropic docs (claude-3-5-sonnet is deprecated/removed)
        # Use ANTHROPIC_MODEL in .env to override. Examples: claude-sonnet-4-5, claude-3-7-sonnet-latest, claude-3-5-haiku-latest
        default_model = "claude-sonnet-4-5"
        model = os.environ.get("ANTHROPIC_MODEL", default_model)
        client = anthropic.Anthropic(api_key=api_key)
        msg = client.messages.create(
            model=model,
            max_tokens=4096,
            messages=[{"role": "user", "content": f"{prompt}\n\n---\n\n{report_text}"}],
        )
        if msg.content and len(msg.content) > 0:
            block = msg.content[0]
            if hasattr(block, "text"):
                return block.text.strip(), None
            return None, "Unexpected API response format."
        return None, "Claude returned no content."
    except Exception as e:
        err = str(e)
        if "404" in err or "not_found" in err.lower():
            err += " Set ANTHROPIC_MODEL in .env to a valid id, e.g. claude-3-7-sonnet-latest or claude-3-5-haiku-latest."
        return None, err


def run_research(topic: str, quick: bool, deep: bool, sources: str, emit: str) -> tuple[str, str, int]:
    """
    Run last30days.py and return (stdout, stderr, returncode).
    """
    if not SCRIPT_PATH.exists():
        return "", f"Script not found: {SCRIPT_PATH}", -1

    cmd = [
        sys.executable,
        str(SCRIPT_PATH),
        topic,
        "--emit", emit,
        "--sources", sources,
    ]
    if quick:
        cmd.append("--quick")
    if deep:
        cmd.append("--deep")

    env = os.environ.copy()
    _inject_secrets_into_env()
    for key in ("OPENAI_API_KEY", "XAI_API_KEY"):
        if key in os.environ:
            env[key] = os.environ[key]

    try:
        result = subprocess.run(
            cmd,
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=180,
            env=env,
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", "Research timed out (max 3 minutes). Try --quick or a narrower topic.", -1
    except Exception as e:
        return "", str(e), -1


st.set_page_config(
    page_title="last30days – Research from Reddit & X",
    page_icon="🔍",
    layout="centered",
)

st.title("🔍 last30days")
st.caption("Research any topic from Reddit & X over the last 30 days")

topic = st.text_input(
    "Topic to research",
    placeholder="e.g. best Meta ads creatives for hotels, AI tools 2026, ClawdBot setup",
    help="Enter a topic; the tool will search Reddit and X for the last 30 days.",
)

col1, col2, col3 = st.columns(3)
with col1:
    depth = st.radio("Depth", ["Default", "Quick (faster)", "Deep (more sources)"], horizontal=True)
with col2:
    sources = st.selectbox(
        "Sources",
        ["auto", "both", "reddit", "x"],
        format_func=lambda x: {"auto": "Auto (Reddit + X)", "both": "Reddit + X", "reddit": "Reddit only", "x": "X only"}[x],
    )
with col3:
    output_format = st.selectbox(
        "Output",
        ["compact", "md", "json"],
        format_func=lambda x: {"compact": "Compact", "md": "Full report", "json": "JSON"}[x],
    )

quick = depth == "Quick (faster)"
deep = depth == "Deep (more sources)"

generate_with_claude = st.checkbox(
    "Generate Best Practices & Prompt Pack with Claude",
    value=False,
    help="After research, call Claude to fill in the Best Practices and Prompt Pack sections. Requires ANTHROPIC_API_KEY.",
)

if st.button("Run research", type="primary", use_container_width=True):
    if not (topic or "").strip():
        st.warning("Please enter a topic.")
    else:
        with st.spinner("Searching Reddit & X (this may take 30–90 seconds)…"):
            stdout, stderr, code = run_research(
                topic.strip(), quick=quick, deep=deep, sources=sources, emit=output_format
            )

        if stderr:
            st.text_area("Log / errors", value=stderr, height=120, disabled=True)

        if code != 0 and not stdout:
            st.error("Research failed. Check the log above or try a different topic/depth.")
        elif stdout:
            display_content = stdout
            if output_format != "json" and generate_with_claude and stdout.strip():
                _inject_secrets_into_env()
                with st.spinner("Generating Best Practices & Prompt Pack with Claude…"):
                    completed, err = _generate_with_claude(stdout)
                if err:
                    st.warning(f"Claude step failed: {err}. Showing research only.")
                elif completed:
                    display_content = completed
                    st.success("Done. Best Practices & Prompt Pack generated by Claude.")
            else:
                st.success("Done.")
            if output_format == "json":
                st.code(display_content, language="json")
            else:
                st.markdown(display_content)

            # Download options (use display_content so Claude output is included when used)
            if display_content.strip():
                st.divider()
                st.subheader("Download research")
                st.caption("Save as a file to share or paste into an LLM.")
                safe_topic = "".join(c if c.isalnum() or c in " -_" else "_" for c in (topic or "report")[:50]).strip() or "report"
                base_name = f"last30days_{safe_topic}".replace(" ", "_")

                col_dl1, col_dl2, col_dl3, col_dl4 = st.columns(4)
                with col_dl1:
                    st.download_button(
                        "📄 Markdown (.md)" if output_format != "json" else "📄 JSON (.json)",
                        data=display_content,
                        file_name=f"{base_name}.md" if output_format != "json" else f"{base_name}.json",
                        mime="text/markdown" if output_format != "json" else "application/json",
                        key="dl_md",
                    )
                with col_dl2:
                    st.download_button(
                        "📝 Text (.txt)",
                        data=display_content,
                        file_name=f"{base_name}.txt",
                        mime="text/plain",
                        key="dl_txt",
                    )
                with col_dl3:
                    if output_format != "json":
                        _offer_docx_download(display_content, base_name)
                    else:
                        st.caption("Word for .md output")
                with col_dl4:
                    if output_format != "json":
                        _offer_pdf_download(display_content, base_name)
                    else:
                        st.caption("PDF for .md output")

st.divider()
with st.expander("What does this tool do?"):
    st.markdown("""
    **last30days** searches **Reddit** and **X (Twitter)** for the **last 30 days** on your topic, then returns a ranked list of threads and posts with links and short summaries.

    - **Depth:** Quick = fewer sources (~30–50 s). Default = normal. Deep = more sources (~90+ s).
    - **Sources:** Auto uses Reddit + X if API keys are set; you can force Reddit only or X only.
    - **Output:** Compact (summary), Full report (markdown), or JSON.

    API keys are read from `~/.config/last30days/.env` (OPENAI_API_KEY, XAI_API_KEY) or from Streamlit secrets when deployed.

    **"Best Practices" and "Prompt Pack"**  
    Check **Generate Best Practices & Prompt Pack with Claude** to have Claude fill those sections automatically (requires `ANTHROPIC_API_KEY` in `.env` or Streamlit secrets). Otherwise, download the report and paste it into any LLM and ask it to synthesize those sections.
    """)
