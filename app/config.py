"""
Small central place for config values pulled from the environment.
Currently just BASE_URL, but this is where you'd add more as the app
grows — beats scattering os.getenv() calls across random files.
"""

import os

# In dev this is localhost:8000 (matches docker-compose port mapping).
# In production (Render), set this to your real deployed URL, e.g.
# https://your-app-name.onrender.com — no trailing slash.
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")