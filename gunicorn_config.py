# Gunicorn configuration file
import multiprocessing

# Server socket
bind = "0.0.0.0:3200"
backlog = 2048

# Worker processes up to a maximum of 6
workers = multiprocessing.cpu_count() * 2 + 1
if workers > 2:
    workers = 2
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

# Reload
reload = True
reload_engine = 'auto'

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Process naming
proc_name = 'flask-app'

# Development settings
capture_output = True
enable_stdio_inheritance = True 