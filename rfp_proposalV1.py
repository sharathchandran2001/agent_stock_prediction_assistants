import os
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

# Utility to read text
def read_text(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

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

# Main function
def main():
    print("=== RFP Proposal Generator ===")
    input_data = {}

    # Collect inputs for agents
    for key, cfg in agent_configs.items():
        if key == "proposal_summarizer":
            continue
        input_path = os.path.join(input_dir, cfg['filename'])
        print(f"\nEnter input for {cfg['label']} (or leave blank to use existing content):")
        existing_content = read_text(input_path)
        if existing_content:
            print(f"Existing content:\n{existing_content}\n")
        user_input = input("Your input: ").strip()
        input_data[key] = user_input if user_input else existing_content
        save_text(input_path, input_data[key])

    # Generate proposal
    print("\nGenerating proposal...")
    section_outputs = {}
    for key, cfg in agent_configs.items():
        if key == "proposal_summarizer":
            continue
        agent = Agent(instructions=cfg.get('instructions', ''))
        response = agent.chat(prompt=input_data[key])
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
    print("\n=== Proposal Summary ===")
    print(proposal_summary)
    print(f"\nProposal saved as:\n- TXT: {txt_path}\n- PDF: {pdf_path}")

if __name__ == "__main__":
    main()