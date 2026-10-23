import os
import sys

# Environment guard: Warn if running with global Python instead of project .venv
if sys.prefix == sys.base_prefix:
    venv_python = os.path.join(os.path.dirname(__file__), '.venv', 'Scripts', 'python.exe')
    if os.path.exists(venv_python):
        print(f"[CortexGrid Notice] Running with global Python. For best reliability, activate the virtual environment or run:")
        print(f"  .\\.venv\\Scripts\\python.exe run.py\n")

from app import create_app
from app.extensions import db

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting CortexGrid Backend on http://127.0.0.1:{port} ...")
    app.run(host='0.0.0.0', port=port, debug=True)
