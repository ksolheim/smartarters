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
keepalive = 65

# Request handling
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Proxy and security settings
forwarded_allow_ips = '*'  # Trust forwarded headers from Application Proxy
secure_scheme_headers = {
    'X-FORWARDED-PROTOCOL': 'ssl',
    'X-FORWARDED-PROTO': 'https',
    'X-FORWARDED-SSL': 'on'
}
proxy_protocol = True
proxy_allow_ips = '*'