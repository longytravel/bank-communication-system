 # Bank Communication System

Professional AI-powered banking communication platform for personalized customer engagement.

## Features

### 1. Customer Analysis
- Upload CSV/Excel customer data
- AI-powered segmentation using Claude
- Identifies vulnerable customers and upsell opportunities

### 2. Letter Management
- Upload and classify letters (REGULATORY, PROMOTIONAL, INFORMATION)
- Supports TXT, DOCX, PDF formats
- AI classification with confidence scores

### 3. Customer Communication Plans
- Generate personalized communication strategies
- Multi-channel support (Email, SMS, In-app, Letter, Voice)
- Real-time cost analysis
- Voice note generation via OpenAI

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt

Create .env file with API keys:
CLAUDE_API_KEY=your-claude-key
OPENAI_API_KEY=your-openai-key

Run the application:
bashpython -m streamlit run src/main.py


Architecture

Frontend: Streamlit
AI: Claude (Anthropic) + OpenAI
Styling: Professional banking theme (no emojis)
Architecture: Modular design with separate modules per feature

License
Private - Bank Internal Use Only

