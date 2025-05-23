FROM nginx:alpine

# Remove default NGINX static files
RUN rm -rf /usr/share/nginx/html/*

# Copy HTML to NGINX root
COPY index.html /usr/share/nginx/html/

# Copy NGINX config (template uses $PORT)
COPY default.conf.template /etc/nginx/templates/default.conf.template

EXPOSE 8080

# Use envsubst to dynamically inject $PORT at runtime
CMD ["sh", "-c", "envsubst < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf && exec nginx -g 'daemon off;'"]
