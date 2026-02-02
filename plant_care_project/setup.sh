#!/usr/bin/env bash
set -e

VENV_DIR="venv"

echo "🔧 Setting up virtual environment and installing dependencies..."

# 1. Create venv if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
  echo "📦 Creating virtual environment in ./$VENV_DIR"
  python -m venv "$VENV_DIR"
else
  echo "✅ Virtual environment already exists at ./$VENV_DIR"
fi

# 2. Activate venv
# shellcheck disable=SC1090
source "$VENV_DIR/bin/activate"

# 3. Upgrade pip (optional but nice)
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# 4. Install requirements
if [ -f "requirements.txt" ]; then
  echo "📥 Installing dependencies from requirements.txt..."
  pip install -r requirements.txt
else
  echo "⚠️  requirements.txt not found. Installing Streamlit directly..."
  pip install streamlit
fi

echo "✅ Setup complete."

echo
echo "To activate this environment later, run:"
echo "  source $VENV_DIR/bin/activate"
echo
echo "To start the app, run:"
echo "  streamlit run plant_agent_streamlit.py"
