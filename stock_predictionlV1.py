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

# Agent configurations for stock prediction
agent_configs = {
    "stock_agent_1": {
        "label": "Stock Market Trends Analysis",
        "filename": "stock_agent1.txt",
        "instructions": "Analyze recent stock market trends and provide insights."
    },
    "stock_agent_2": {
        "label": "Sector Performance Analysis",
        "filename": "stock_agent2.txt",
        "instructions": "Analyze the performance of different market sectors and provide a summary."
    },
    "stock_agent_3": {
        "label": "Enterprise Stock Analysis",
        "filename": "stock_agent3.txt",
        "instructions": "Analyze the stock performance of specific enterprises and provide detailed insights."
    },
    "stock_agent_context": {
        "label": "Stock Prediction Context",
        "filename": "stock_agent_context.txt",
        "instructions": "Provide additional context for stock predictions based on historical data and market conditions."
    },
    "final_stock_agent": {
        "label": "Final Stock Prediction and Summary",
        "filename": "final_stock_prediction.txt",
        "instructions": "Summarize the stock market trends and predict future performance based on the analysis of other agents."
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
    print("=== Stock Prediction Assistant ===")
    input_data = {}

    # Collect inputs for agents
    for key, cfg in agent_configs.items():
        if key == "final_stock_agent":
            continue
        input_path = os.path.join(input_dir, cfg['filename'])
        print(f"\nEnter input for {cfg['label']} (or leave blank to use existing content):")
        existing_content = read_text(input_path)
        if existing_content:
            print(f"Existing content:\n{existing_content}\n")
        user_input = input("Your input: ").strip()
        input_data[key] = user_input if user_input else existing_content
        save_text(input_path, input_data[key])

    # Generate predictions
    print("\nGenerating stock predictions...")
    section_outputs = {}
    for key, cfg in agent_configs.items():
        if key == "final_stock_agent":
            continue
        agent = Agent(instructions=cfg.get('instructions', ''))
        response = agent.chat(prompt=input_data[key])
        section_outputs[key] = response or "[No response]"
        save_text(os.path.join(output_dir, f'agent_{key}.txt'), response)

    # Final stock prediction agent
    combined_prompt = "\n\n".join(
        f"[{cfg['label']}]\n{section_outputs[key]}" for key, cfg in agent_configs.items() if key != "final_stock_agent"
    )
    context_text = read_text(os.path.join(input_dir, agent_configs['stock_agent_context']['filename']))
    combined_prompt = f"{context_text}\n\n{combined_prompt}"
    final_agent = Agent(instructions=agent_configs['final_stock_agent']['instructions'])
    final_prediction = final_agent.chat(prompt=combined_prompt) or "[No prediction response]"
    save_text(os.path.join(output_dir, agent_configs['final_stock_agent']['filename']), final_prediction)

    # Generate files
    txt_path = os.path.join(output_dir, 'final_stock_prediction.txt')
    pdf_path = os.path.join(output_dir, 'final_stock_prediction.pdf')
    save_text(txt_path, final_prediction)
    generate_pdf(final_prediction, pdf_path)

    # Display outputs
    print("\n=== Final Stock Prediction Summary ===")
    print(final_prediction)
    print(f"\nPrediction saved as:\n- TXT: {txt_path}\n- PDF: {pdf_path}")

if __name__ == "__main__":
    main()