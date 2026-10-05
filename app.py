import streamlit as st
from pathlib import Path
from agents.crew import run_drawing_analysis
from core.config import APP_NAME

st.set_page_config(page_title=APP_NAME, page_icon="⚙️", layout="wide")

st.title("⚙️ AI CNC Programming Copilot")
st.caption("Safety-first CNC drawing analysis and manufacturing planning")

with st.sidebar:
    st.header("Machine Setup")
    controller = st.selectbox("Controller", ["Fanuc", "Haas", "Siemens", "Mitsubishi"])
    machine = st.text_input("Machine", "3-Axis CNC Milling Machine")
    material = st.text_input("Material", "Aluminum 6061")
    units = st.selectbox("Units", ["mm", "inch"])
    stock = st.text_input("Stock size", "100 x 80 x 30 mm")

st.warning(
    "SAFETY: This prototype is decision-support software. "
    "Never run AI-generated CNC code directly on a machine. "
    "A qualified machinist must verify tooling, offsets, workholding, machine limits and simulation."
)

uploaded = st.file_uploader(
    "Upload engineering drawing",
    type=["png", "jpg", "jpeg", "pdf"],
    help="Upload a clear dimensioned drawing."
)

if uploaded:
    if uploaded.type.startswith("image/"):
        st.image(uploaded, caption=uploaded.name, use_container_width=True)
    else:
        st.info(f"PDF uploaded: {uploaded.name}")

    if st.button("🔎 Analyze Drawing", type="primary", use_container_width=True):
        with st.spinner("Running drawing analysis and manufacturing planning..."):
            try:
                result = run_drawing_analysis(
                    file_bytes=uploaded.getvalue(),
                    filename=uploaded.name,
                    controller=controller,
                    machine=machine,
                    material=material,
                    units=units,
                    stock=stock,
                )
                st.session_state["result"] = result
            except Exception as exc:
                st.error(f"Analysis failed: {exc}")

if "result" in st.session_state:
    result = st.session_state["result"]
    st.divider()
    st.subheader("Engineering Analysis")
    st.markdown(result)

    st.error(
        "PROGRAM EXPORT IS BLOCKED in this prototype. "
        "G-code generation will only be enabled after deterministic validation "
        "and simulation layers are implemented."
    )

st.divider()
st.caption("CNC AI Agent — prototype architecture: Streamlit + CrewAI + GPT-120B-compatible API")
