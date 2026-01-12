# Load environment variables from .env file
Get-Content .env | ForEach-Object {
    if ($_ -match '^([^=]+)=(.*)$') {
        $key = $matches[1]
        $value = $matches[2]
        [Environment]::SetEnvironmentVariable($key, $value, "Process")
    }
}

# Start Flask application
& "C:/Users/shrin/Desktop/SWoC/AgriTechSwoc/.venv/Scripts/python.exe" -W ignore::FutureWarning app.py
