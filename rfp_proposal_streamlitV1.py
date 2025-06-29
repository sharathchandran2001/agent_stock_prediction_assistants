import os
import streamlit as st
from datetime import datetime
from praisonaiagents import Agent
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas

# Base paths
base_dir = os.path.dirname(os.path.abspath(__file__))
input_dir = os.path.join(base_dir, 'input')
output_dir = os.path.join(base_dir, 'output')
os.makedirs(input_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

# Agent configurations
agent_configs = {
    "dcs_agent_1": {"label": "DCS Agent 1 Input", "filename": "dcs_agent_1.txt"},
    "dcs_agent_2": {"label": "DCS Agent 2 Input", "filename": "dcs_agent_2.txt"},
    "dce_agent_1": {"label": "DCE Agent 1 Input", "filename": "dce_agent_1.txt"},
    "client_requirements": {
        "label": "Client Requirements Input",
        "filename": "client_requirements.txt",
        "instructions": "Analyze the client requirements and provide a detailed response."
    },
    "vp_context_agent_1": {
        "label": "VP Context Agent Input",
        "filename": "vp_context_agent_1.txt",
        "instructions": "Use the VP context to provide additional insights for the proposal."
    },
    "proposal_summarizer": {
        "label": "Proposal Summarizer Agent",
        "filename": "proposal_summary.txt",
        "instructions": "Summarize the RFP and answer client questions based on the provided inputs."
    }
}

# Utility to save text
def save_text(file_path, content):
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

# PDF generation
def generate_pdf(text, pdf_path):
    c = canvas.Canvas(pdf_path, pagesize=LETTER)
    width, height = LETTER
    text_object = c.beginText(50, height - 50)
    text_object.setFont("Helvetica", 10)
    max_width = width - 100

    for line in text.splitlines():
        while line:
            split_index = len(line)
            while c.stringWidth(line[:split_index], "Helvetica", 10) > max_width:
                split_index -= 1
            text_object.textLine(line[:split_index])
            line = line[split_index:]

        if text_object.getY() < 50:
            c.drawText(text_object)
            c.showPage()
            text_object = c.beginText(50, height - 50)
            text_object.setFont("Helvetica", 10)

    c.drawText(text_object)
    c.save()

# Streamlit App
st.title("📄 RFP Proposal Generator")
st.markdown("Provide RFP details and generate a proposal summary.")

input_data = {}

# Input fields for agents
for key, cfg in agent_configs.items():
    if key == "proposal_summarizer":
        continue
    default_text = ""
    input_path = os.path.join(input_dir, cfg['filename'])
    if os.path.exists(input_path):
        with open(input_path, 'r', encoding='utf-8') as f:
            default_text = f.read()
    input_data[key] = st.text_area(cfg['label'], value=default_text, height=200)

if st.button("Generate Proposal"):
    section_outputs = {}
    for key, cfg in agent_configs.items():
        if key == "proposal_summarizer":
            continue
        input_text = input_data[key]
        save_text(os.path.join(input_dir, cfg['filename']), input_text)
        agent = Agent(instructions=cfg.get('instructions', ''))
        response = agent.chat(prompt=input_text)
        section_outputs[key] = response or "[No response]"
        save_text(os.path.join(output_dir, f'agent_{key}.txt'), response)

    # Proposal summarizer agent
    combined_prompt = "\n\n".join(
        f"[{cfg['label']}]\n{section_outputs[key]}" for key, cfg in agent_configs.items() if key != "proposal_summarizer"
    )
    summarizer_agent = Agent(instructions=agent_configs['proposal_summarizer']['instructions'])
    proposal_summary = summarizer_agent.chat(prompt=combined_prompt) or "[No summary response]"
    save_text(os.path.join(output_dir, agent_configs['proposal_summarizer']['filename']), proposal_summary)

    # Generate files
    txt_path = os.path.join(output_dir, 'proposal_summary.txt')
    pdf_path = os.path.join(output_dir, 'proposal_summary.pdf')
    save_text(txt_path, proposal_summary)
    generate_pdf(proposal_summary, pdf_path)

    # Display outputs
    st.subheader("Proposal Summary")
    st.text_area("Proposal Content", value=proposal_summary, height=400)

    st.success("Proposal generated!")
    with open(txt_path, 'r', encoding='utf-8') as f:
        st.download_button("📄 Download Proposal (TXT)", f, file_name="proposal_summary.txt")
    with open(pdf_path, 'rb') as f:
        st.download_button("🖨️ Download Proposal (PDF)", f, file_name="proposal_summary.pdf")