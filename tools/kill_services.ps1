Write-Host "Killing SJ-DAS Services..."

# Kill Node/Next.js
$node = Get-Process node -ErrorAction SilentlyContinue
if ($node) {
    Write-Host "Stopping Node.js processes..."
    Stop-Process -Name node -Force
}

# Kill Python (Uvicorn/FastAPI)
# Be careful not to kill the agent itself if it's running as python.
# We will look for uvicorn specifically or python processes running from our venv.
# For simplicity in this environment, we'll try to identify by command line but Powershell Get-Process doesn't show CLI easily without WMI.
# We'll rely on the user or the agent's wrapper managing the main process, but we can try to kill specific python instances if we knew PIDs.
# For now, let's just warn or try to kill uvicorn if possible. 
# Attempting to kill python might take down the agent interaction if not careful.
# Actually, the agent usually runs in a separate process/container, but let's be safe.
# We will assume 'uvicorn' might appear if installed as shim, but usually it's 'python -m uvicorn'.

# Safe approach: Kill common ports
Write-Host "Clearing ports 3000, 3001, 8000..."

# Helper to kill by port
function Kill-Port($port) {
    $tcp = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($tcp) {
        foreach ($conn in $tcp) {
            $pid_val = $conn.OwningProcess
            Write-Host "Killing PID $pid_val on port $port"
            Stop-Process -Id $pid_val -Force -ErrorAction SilentlyContinue
        }
    }
}

Kill-Port 3000
Kill-Port 3001
Kill-Port 8000

Write-Host "Ports cleared."
