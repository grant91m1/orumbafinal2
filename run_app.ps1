# Create virtual environment
python -m venv venv

# Activate virtual environment
if (Test-Path .\venv\Scripts\Activate.ps1) {
    . .\venv\Scripts\Activate.ps1
} else {
    Write-Host "Virtual environment activation script not found."
}

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Run the Flask app
python run.py

# After running, open browser at http://127.0.0.1:5000 manually
Write-Host "Open your browser and navigate to http://127.0.0.1:5000 to view the app."
