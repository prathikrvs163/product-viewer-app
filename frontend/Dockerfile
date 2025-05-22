# Use the official Nginx image as base
FROM nginx:alpine

# Remove default Nginx static assets
RUN rm -rf /usr/share/nginx/html/*

# Copy our static files to Nginx html directory
COPY index.html /usr/share/nginx/html/

# Copy custom Nginx configuration (optional - for CORS and other settings)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start Nginx server
CMD ["nginx", "-g", "daemon off;"]