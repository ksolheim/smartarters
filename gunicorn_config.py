import os

# Server socket configuration
bind = ['0.0.0.0:6001']

# SSL Configuration
certfile = '/app/certs/cert.pem'
keyfile = '/app/certs/key.pem'
ca_certs = '/app/certs/ca.pem'
server_name = os.getenv('SERVER_NAME')

# Worker processes
workers = 4
timeout = 120
keepalive = 5

# Request handling
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'