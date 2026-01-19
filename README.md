# Aurelius Backend

A specific backend built with **FastAPI** designed to power the [Aurelius Desktop App](https://github.com/CrisD314159/aurelius). This project serves as a portfolio piece demonstrating the integration of local Large Language Models (LLMs), Speech-to-Text capabilities, and real-time WebSocket communication for a privacy-focused AI assistant.

**Note:** This is a portfolio application showcasing advanced backend development, local AI model integration, and desktop application support.

## Features

### Local LLM Integration
- **Ollama Support:** seamless integration with [Ollama](https://ollama.com/) to run powerful open-source models (like Llama 3, Mistral, etc) locally on the user's machine.
- **Privacy First:** All processing happens locally; no data is sent to external cloud APIs.
- **Streaming Responses:** Real-time text generation capabilities using WebSockets.

### Intelligent Chat System
- **Persistent History:** Uses **SQLite** to store chat history and user interactions locally (`aurelius.db`).
- **Multi-Chat Management:** Users can create, delete, and manage multiple conversation threads.

### Voice & Audio Processing (On development)
- **Speech-to-Text (STT):** Integrated `faster-whisper` models to enable voice commands and interactions.
- **Audio Conversion:** Utilities for handling PCM to WAV conversion for audio processing.

### Backend Architecture
- **FastAPI:** High-performance, easy-to-learn, fast-to-code, ready-for-production web framework.
- **WebSocket Communication:** Enables real-time, bi-directional communication between the frontend (Electron) and backend.
- **Cross-Platform Support:** Handling for Windows and macOS file paths and database locations.
- **Dependency Management:** Optimized build process using PyInstaller for standalone executables.

## 🛠️ Tech Stack

- **Language:** Python 3.10+
- **Framework:** FastAPI
- **Database:** SQLite
- **AI/ML:** Ollama (LLM), Faster-Whisper (STT), Kokoro TTS
- **Packaging:** PyInstaller

## 🔧 Setup & Installation

1. **Prerequisites**
   - Python 3.10 or higher
   - [Ollama](https://ollama.ai/) installed and running
   - An active Ollama model (e.g., `ollama pull llama3`)

2. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd aurelius-backend
   ```

3. **Install Dependencies**
   It is recommended to use a virtual environment.
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Run the Server**
   ```bash
   python -m app.main
   # or with uvicorn directly
   uvicorn app.main:app --reload
   ```

## 📂 Project Structure

```
aurelius-backend/
├── app/
│   ├── api/            # REST & WebSocket endpoints (Chat, User, Text)
│   ├── db/             # Database initialization and management
│   ├── services/       # Core business logic (LLM, Chats, User)
│   ├── utils/          # Helper functions (Audio conversion, Model loading)
│   └── main.py         # Application entry point
├── stt_models/         # Local Speech-to-Text models
└── requirements.txt    # Project dependencies
```
