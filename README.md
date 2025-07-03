# Groq API Chatv1

A blazing-fast, context-aware chatbot built with Python, Streamlit, and Groq-hosted LLMs. Designed for rapid, multi-model experimentation and professional chat UX.

## Features

- **Multi-model support:**
  - meta-llama/llama-4-maverick-17b-128e-instruct
  - meta-llama/llama-4-scout-17b-16e-instruct
  - gemma2-9b-it
  - llama-3.1-8b-instant
- **Streaming responses** for real-time, token-by-token output
- **Per-model chat history** (switch models, keep your context)
- **Temperature adjuster** (slider, 0.0–1.5) for creative vs. focused responses
- **Download chat as JSON** (user + assistant turns)
- **Average response time** tracker
- **Modern, dark-themed UI** with avatars, chat bubbles, and sidebar controls
- **Clear all chat histories** button
- **Persistent context** (history is saved and restored per model)
- **Error handling** for API, rate limits, and timeouts

---

## Setup & Installation

1. **Clone the repo:**
   ```bash
   git clone https://github.com/0xnomy/groq_chatbot
   cd groq_chatbot
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Add your Groq API key:**
   - Create a `.env` file in the project root:
     ```env
     GROQ_API_KEY=your-groq-api-key-here
     ```
4. **Run the app:**
   ```bash
   streamlit run app.py
   ```

---

## Usage

- **Select a model** from the sidebar (each model has its own chat history)
- **Adjust temperature** (creativity) with the slider
- **Type your message** and press Enter
- **See responses stream in real time**
- **Download your conversation** as JSON with the download button
- **Clear all chat histories** with the sidebar button
- **Switch models** to compare answers or continue previous chats

---

## Supported Models

- **meta-llama/llama-4-maverick-17b-128e-instruct** – Balanced, strong generalization (Meta)
- **meta-llama/llama-4-scout-17b-16e-instruct** – Fast, low-latency (Meta)
- **gemma2-9b-it** – Safe, helpful, instruction-tuned (Google DeepMind)
- **llama-3.1-8b-instant** – Compact, high-speed (Meta)

---

## UI/UX Highlights

- **Sidebar:** Model selector, temperature slider, clear all button
- **Main area:** Chat bubbles, avatars, welcome message, model description
- **Streaming:** See responses as they're generated
- **Download:** Export your chat in one click
- **Average response time:** See how fast your model is

---

##  How Context & History Work

- **All chat context is managed by the app** (not the model)
- **Each model has its own chat history** (saved as `chat_history_<model>.json`)
- **When you send a message, the full history is sent to the model** for context-aware replies
- **Switching models** loads the last conversation for that model

---

## Advanced Controls

- **Temperature:**
  - Lower = more focused, deterministic
  - Higher = more creative, varied
- **Export:**
  - Download your current conversation as a JSON file (`groqchatv1_history.json`)

---

## Links

- [Groq API] (https://console.groq.com/docs/)
