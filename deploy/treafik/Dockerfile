FROM traefik:v3.0

# Configure Traefik to listen on port 80 for HTTP and port 443 for HTTPS
EXPOSE 80 443

# Configure Traefik to read the static configuration file
COPY traefik.yaml /etc/traefik
