# Server socket configuration
bind = ['0.0.0.0:6001']
certfile = '/certs/cert.pem'
keyfile = '/certs/key.pem'
ca_certs = '/certs/ca.pem'
ssl_version = 'TLS'

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