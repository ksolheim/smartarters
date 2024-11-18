# Server socket configuration
BIND = '0.0.0.0:6001'
CERTFILE = '/certs/cert.pem'
KEYFILE = '/certs/key.pem'
CA_CERTS = '/certs/ca.pem'

# Worker processes
WORKERS = 4
TIMEOUT = 120
KEEPALIVE = 5

# Request handling
MAX_REQUESTS = 1000
MAX_REQUESTS_JITTER = 50

# Logging
ACCESSLOG = '-'
ERRORLOG = '-'
LOGLEVEL = 'info'

# SSL Configuration
SSL_VERSION = 'TLS'
# Uncomment and modify these if needed:
# CIPHERS = 'TLSv1'
# CERT_REQS = 2  # ssl.CERT_REQUIRED 