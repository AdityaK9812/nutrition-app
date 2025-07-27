import os

# Bind to the port Render provides
port = int(os.environ.get("PORT", 10000))
bind = f"0.0.0.0:{port}"

# Worker configuration
workers = 4
worker_class = "sync"
threads = 2

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Timeout configuration
timeout = 120
keepalive = 5 