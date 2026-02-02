# 🌿 Love Your Garden - Plant Care Assistant

A comprehensive plant care management application that helps you maintain a healthy garden with AI-powered advice, disease diagnosis, and task tracking.

## Overview

Love Your Garden is an interactive web application built to assist both beginner and experienced gardeners. It provides personalized plant care recommendations, helps diagnose plant diseases, and maintains a gardening log to track all your plant care activities.

## Features

### 1. **Plant Care Advisor**
- Get detailed care instructions for various plants
- Includes information on watering, lighting, soil, and fertilizer requirements
- Built-in knowledge base for common plants (Snake Plant, Pothos, Tomato, Basil, Rose, Apple, Strawberry)
- Optional LLM-powered refinement for personalized advice using OpenAI GPT models

### 2. **Disease Diagnosis**
- AI-powered plant disease identification
- Upload images of affected plants or select from sample cases
- Get detailed diagnosis including:
  - Identified disease or pest
  - Severity assessment
  - Treatment recommendations
  - Preventive measures
- Sample disease cases included for testing

### 3. **Gardening Log & Task Management**
- Track all plant care activities with timestamps
- Log watering, fertilizing, pruning, and other maintenance tasks
- View upcoming scheduled tasks
- Automatic next-due date suggestions for recurring tasks
- Persistent storage in JSON format

## Technologies & Frameworks

- **Frontend Framework**: [Streamlit](https://streamlit.io/) - Python web framework for data applications
- **AI/LLM Integration**: [OpenAI API](https://openai.com/) - GPT-4.1-mini for intelligent plant advice and disease diagnosis
- **Image Processing**: [Pillow (PIL)](https://python-pillow.org/) - Python Imaging Library for image handling and thumbnails
- **Environment Management**: [python-dotenv](https://github.com/theskumar/python-dotenv) - Environment variable management
- **Data Storage**: JSON-based logging system for persistent data
- **Language**: Python 3.x

## Prerequisites

- Python 3.8 or higher
- OpenAI API Key (required for LLM features)
- Virtual environment support (venv)

## Installation & Setup

### 1. Clone or Download the Project

```bash
cd plant_care
```

### 2. Run the Setup Script

The project includes an automated setup script that creates a virtual environment and installs all dependencies:

```bash
chmod +x setup.sh  # Make script executable (if needed)
./setup.sh
```

This script will:
- Create a Python virtual environment in `./venv`
- Upgrade pip to the latest version
- Install all required dependencies from `requirements.txt`

### 3. Configure Environment Variables

Create a `.env` file in the project root and add your OpenAI API key:

```bash
OPENAI_API_KEY=your_api_key_here
```

**Note**: Never commit your `.env` file to version control. It should be listed in `.gitignore`.

### 4. Manual Setup (Alternative)

If you prefer manual setup:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

## Running the Application

### 1. Activate the Virtual Environment

```bash
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows
```

### 2. Start the Streamlit Application

```bash
streamlit run plant_agent_streamlit.py
```

The application will automatically open in your default web browser at `http://localhost:8501`.

If it doesn't open automatically, navigate to the URL shown in the terminal.

## Project Structure

```
plant_care/
├── plant_agent_streamlit.py  # Main Streamlit UI application
├── plant_agent_core.py        # Core business logic and OpenAI integration
├── plant_care_agent.py        # Additional agent functionality
├── requirements.txt           # Python dependencies
├── setup.sh                   # Automated setup script
├── .env                       # Environment variables (API keys)
├── garden_log.json           # Persistent gardening log (auto-generated)
├── assets/
│   ├── disease_samples/      # Sample disease images
│   └── plants/               # Plant reference images
└── venv/                     # Virtual environment (auto-generated)
```

## Usage Guide

### Plant Care Advisor Tab
1. Select a plant from the dropdown or search for a specific plant
2. View care recommendations including watering, light, soil, and fertilizer needs
3. Toggle "Use LLM refinement" for AI-enhanced, personalized advice

### Disease Diagnosis Tab
1. Select a sample disease case or upload your own plant image
2. Describe the symptoms you're observing
3. Click "Diagnose" to get AI-powered diagnosis and treatment recommendations
4. Follow the suggested treatment and prevention measures

### Log & Tasks Tab
1. View your recent gardening activities
2. Add new log entries with plant name, action, and notes
3. The system suggests next due dates for recurring tasks
4. Check upcoming scheduled tasks to stay on top of plant care

## Dependencies

```
streamlit>=1.39.0      # Web framework
openai>=1.51.0         # AI/LLM integration
python-dotenv>=1.0.0   # Environment variable management
pillow>=10.0.0         # Image processing
```

## Configuration

### OpenAI Model Selection

The application uses `gpt-4.1-mini` by default. You can modify the model in `plant_agent_core.py`:

```python
response = client.chat.completions.create(
    model="gpt-4.1-mini",  # Change to gpt-4o, gpt-4-turbo, etc.
    ...
)
```

### Logging

The gardening log is stored in `garden_log.json` and persists across sessions. This file is automatically created and updated as you log activities.

## Troubleshooting

### Common Issues

**Error: "OPENAI_API_KEY is not set"**
- Ensure you have created a `.env` file with your OpenAI API key
- Verify the key is correctly formatted without extra spaces

**Streamlit doesn't start**
- Ensure virtual environment is activated
- Verify all dependencies are installed: `pip list`
- Try reinstalling: `pip install -r requirements.txt --force-reinstall`

**Images not displaying**
- Check that the `assets/` directory exists with subdirectories `disease_samples/` and `plants/`
- Verify image files are in the correct format (PNG recommended)

## Contributing

This is a personal plant care project. Feel free to fork and customize it for your own gardening needs!

## License

This project is provided as-is for personal use.

## Support

For issues or questions about the application, check the code comments or modify the configuration files to suit your needs.

---

**Happy Gardening! 🌱**
