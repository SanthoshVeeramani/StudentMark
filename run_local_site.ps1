# run_local_site.ps1
# Usage: Open PowerShell in the project root (folder containing manage.py) and run:
#    .\run_local_site.ps1
# or with a custom port:
#    .\run_local_site.ps1 -Port 8001

param(
    [string]$Port = "8000"
)

function FailExit($msg) {
    Write-Error $msg
    exit 1
}

# Ensure manage.py exists
if (-not (Test-Path .\manage.py)) {
    FailExit "manage.py not found in the current folder: $(Get-Location). Change to the Django project root and re-run this script."
}

# Create virtualenv if missing
if (-not (Test-Path .\venv\Scripts\Activate.ps1)) {
    Write-Host "Creating virtual environment..."
    python -m venv venv
}

# Activate venv
Write-Host "Activating virtual environment..."
. .\venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "Upgrading pip..."
python -m pip install --upgrade pip

# Install requirements (retry policy)
$req = "requirements.txt"
if (-not (Test-Path $req)) {
    FailExit "requirements.txt not found in project root."
}

Write-Host "Installing Python dependencies from $req (this may take a while)..."
$maxAttempts = 2
$attempt = 0
$ok = $false
while (-not $ok -and $attempt -lt $maxAttempts) {
    try {
        $attempt++
        pip install -r $req
        $ok = $true
    }
    catch {
        Write-Warning "pip install failed on attempt $attempt. Retrying..."
        Start-Sleep -Seconds 3
    }
}
if (-not $ok) { FailExit "Failed to install required Python packages. Check your network or run 'pip install -r requirements.txt' manually." }

# Create .env from example if not present
if (-not (Test-Path .\.env)) {
    if (Test-Path .\.env.example) {
        Copy-Item .\.env.example .\.env -Force
        Write-Host "Copied .env.example to .env. Please edit .env if you need custom settings (SECRET_KEY, DEBUG, DATABASE_URL)."
    } else {
        Write-Warning ".env.example not found; make sure environment variables are set as needed." 
    }
}

# Ensure minimal sqlite DATABASE_URL if not set
$envFile = Get-Content .\.env -ErrorAction SilentlyContinue | Out-String
if ($envFile -and ($envFile -notmatch "DATABASE_URL")) {
    Add-Content .\.env "`nDATABASE_URL=sqlite:///db.sqlite3"
    Write-Host "Added DATABASE_URL=sqlite:///db.sqlite3 to .env"
}

# Run migrations and seed data
Write-Host "Running makemigrations (no-op if none)..."
python manage.py makemigrations --noinput

Write-Host "Applying migrations..."
python manage.py migrate --noinput

Write-Host "Seeding data (seed_data) if available..."
try {
    python manage.py seed_data
}
catch {
    Write-Warning "seed_data failed or not present; you can run 'python manage.py seed_data' manually. Continuing..."
}

# Start the development server bound to localhost
$bind = "127.0.0.1:$Port"
Write-Host "Starting development server at http://$bind"
Write-Host "Quit the server with CONTROL-C in this terminal."

# Start runserver in the current process so we see output
python manage.py runserver $bind
