FROM caddy:2.4.5-alpine as caddy

# Copy the HTML files to the Caddy web directory
COPY . /usr/share/caddy/html

# Copy the Caddy configuration file
COPY ./caddy/Caddyfile /etc/caddy/Caddyfile

# Start Caddy
CMD ["caddy", "run", "--config", "/etc/caddy/Caddyfile"]
