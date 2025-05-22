# Product Viewer Frontend

This is the frontend component of the 3-tier Product Viewer application. It's a responsive web interface built with HTML, CSS, and JavaScript that fetches and displays product data from the backend API.

## Features

- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Modern UI**: Clean, modern interface with gradient backgrounds and smooth animations
- **API Configuration**: Allows users to input/configure the backend API URL
- **Error Handling**: Comprehensive error handling with user-friendly messages
- **Loading States**: Visual feedback during API calls
- **Product Grid**: Displays products in an attractive card layout
- **Image Handling**: Graceful fallback for missing product images
- **CORS Support**: Nginx configuration includes proper CORS headers

## File Structure

```
frontend/
├── index.html          # Main HTML file with embedded CSS and JavaScript
├── Dockerfile          # Docker configuration for containerization
├── nginx.conf          # Nginx server configuration
└── README.md          # This file
```

## Local Development

### Option 1: Direct File Opening
1. Simply open `index.html` in your web browser
2. Enter your backend API URL (e.g., `http://localhost:5000`)
3. Click "Load Products"

### Option 2: Local HTTP Server
```bash
# Using Python
python -m http.server 8080

# Using Node.js
npx serve .

# Using PHP
php -S localhost:8080
```

Then visit `http://localhost:8080`

## Docker Deployment

### Build the Docker Image
```bash
# Navigate to the frontend directory
cd frontend

# Build the Docker image
docker build -t gcr.io/YOUR_PROJECT_ID/product-frontend:v1 .

# Test locally
docker run -p 8080:80 gcr.io/YOUR_PROJECT_ID/product-frontend:v1
```

### Push to Google Container Registry
```bash
# Configure Docker to use gcloud as credential helper
gcloud auth configure-docker

# Push the image
docker push gcr.io/YOUR_PROJECT_ID/product-frontend:v1
```

## Configuration

### API URL Configuration
The frontend allows users to configure the backend API URL through the web interface. Default configurations include:

- **Local Development**: `http://localhost:5000`
- **Cloud Run**: `https://your-backend-service-url`
- **GKE**: `http://your-load-balancer-ip`

### Environment-Specific Settings

For production deployments, you might want to pre-configure the API URL. You can modify the default value in `index.html`:

```javascript
<input type="text" id="apiUrl" value="https://your-production-api-url" placeholder="Enter backend API URL">
```

## API Integration

The frontend expects the backend API to provide:

### Products Endpoint
- **URL**: `/api/products`
- **Method**: GET
- **Response**: JSON array of products

```json
[
  {
    "id": 1,
    "name": "Product Name",
    "description": "Product description",
    "price": 29.99,
    "image_url": "https://example.com/image.jpg"
  }
]
```

### Health Check (Optional)
- **URL**: `/health`
- **Method**: GET
- **Response**: Simple health status

## Nginx Configuration

The included `nginx.conf` provides:

- **CORS Support**: Allows cross-origin requests
- **Gzip Compression**: Reduces bandwidth usage
- **Security Headers**: Basic security enhancements
- **Caching**: Optimizes static asset delivery
- **Health Check**: `/health` endpoint for load balancers

## Troubleshooting

### Common Issues

1. **CORS Errors**
   - Ensure backend includes proper CORS headers
   - Check if API URL is correct and accessible

2. **Network Errors**
   - Verify backend server is running
   - Check firewall settings
   - Confirm API URL format (include http:// or https://)

3. **Empty Product List**
   - Check backend API response format
   - Verify database has sample data
   - Check browser console for JavaScript errors

### Browser Console Debugging

Open browser developer tools (F12) and check the Console tab for detailed error messages and network request information.

## Production Considerations

1. **HTTPS**: Use HTTPS in production environments
2. **API URL**: Configure production API URL as default
3. **CDN**: Consider using a CDN for static asset delivery
4. **Monitoring**: Add application monitoring and analytics
5. **Error Tracking**: Implement error tracking (e.g., Sentry)

## Browser Compatibility

This frontend supports all modern browsers:
- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

## Performance Features

- **Lazy Loading**: Images load on demand
- **Animations**: Smooth CSS transitions and transforms
- **Responsive Images**: Optimized for different screen sizes
- **Minimal Dependencies**: No external JavaScript libraries required