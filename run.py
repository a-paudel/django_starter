import waitress
from config.wsgi import application
import os
import sys

args = sys.argv[1:]
port = args[0] if args else os.getenv("PORT", "8000")

if __name__ == "__main__":
    print(f"Starting server on http://localhost:{port}")

    waitress.serve(
        application,
        port=port,
        threads=6,
    )
