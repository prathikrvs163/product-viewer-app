#!/usr/bin/env python3
"""
Product Viewer Backend API
A Flask application that provides RESTful endpoints for product data.
"""

import os
import logging
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import psycopg2.pool
from contextlib import contextmanager
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Database configuration from environment variables
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'product_db'),
    'user': os.getenv('DB_USER', 'pguser'),
    'password': os.getenv('DB_PASSWORD', 'password'),
    'port': os.getenv('DB_PORT', '5432')
}

# Application configuration
APP_PORT = int(os.getenv('PORT', 5000))
DEBUG_MODE = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

# Database connection pool
connection_pool = None

def initialize_db_pool():
    """Initialize database connection pool"""
    global connection_pool
    try:
        connection_pool = psycopg2.pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=20,
            **DB_CONFIG
        )
        logger.info("Database connection pool initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize database connection pool: {str(e)}")
        return False

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    connection = None
    try:
        connection = connection_pool.getconn()
        yield connection
    except Exception as e:
        if connection:
            connection.rollback()
        logger.error(f"Database operation failed: {str(e)}")
        raise
    finally:
        if connection:
            connection_pool.putconn(connection)

def test_db_connection():
    """Test database connectivity"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                logger.info("Database connection test successful")
                return True
    except Exception as e:
        logger.error(f"Database connection test failed: {str(e)}")
        return False

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring and load balancers"""
    try:
        # Check database connectivity
        db_status = test_db_connection()
        
        health_data = {
            'status': 'healthy' if db_status else 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0',
            'database': 'connected' if db_status else 'disconnected',
            'uptime': time.time() - start_time
        }
        
        status_code = 200 if db_status else 503
        return jsonify(health_data), status_code
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Health check failed',
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@app.route('/api/products', methods=['GET'])
def get_products():
    """Get all products from the database"""
    try:
        # Get query parameters for pagination (optional)
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', default=0, type=int)
        
        # Build query
        query = "SELECT id, name, description, price, image_url FROM products ORDER BY id"
        params = []
        
        if limit:
            query += " LIMIT %s OFFSET %s"
            params.extend([limit, offset])
        
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                products = cursor.fetchall()
                
                # Convert to list of dictionaries
                products_list = []
                for product in products:
                    product_dict = dict(product)
                    # Ensure price is a float
                    if product_dict.get('price'):
                        product_dict['price'] = float(product_dict['price'])
                    products_list.append(product_dict)
                
                logger.info(f"Retrieved {len(products_list)} products from database")
                
                return jsonify(products_list), 200
                
    except psycopg2.Error as e:
        logger.error(f"Database error in get_products: {str(e)}")
        return jsonify({
            'error': 'Database error',
            'message': 'Failed to retrieve products from database'
        }), 500
        
    except Exception as e:
        logger.error(f"Unexpected error in get_products: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        }), 500

@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get a specific product by ID"""
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    "SELECT id, name, description, price, image_url FROM products WHERE id = %s",
                    (product_id,)
                )
                product = cursor.fetchone()
                
                if not product:
                    return jsonify({
                        'error': 'Product not found',
                        'message': f'Product with ID {product_id} does not exist'
                    }), 404
                
                product_dict = dict(product)
                if product_dict.get('price'):
                    product_dict['price'] = float(product_dict['price'])
                
                logger.info(f"Retrieved product {product_id} from database")
                return jsonify(product_dict), 200
                
    except psycopg2.Error as e:
        logger.error(f"Database error in get_product: {str(e)}")
        return jsonify({
            'error': 'Database error',
            'message': 'Failed to retrieve product from database'
        }), 500
        
    except Exception as e:
        logger.error(f"Unexpected error in get_product: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        }), 500

@app.route('/api/products/search', methods=['GET'])
def search_products():
    """Search products by name or description"""
    try:
        search_term = request.args.get('q', '').strip()
        if not search_term:
            return jsonify({
                'error': 'Missing search term',
                'message': 'Please provide a search term using the "q" parameter'
            }), 400
        
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT id, name, description, price, image_url 
                    FROM products 
                    WHERE name ILIKE %s OR description ILIKE %s 
                    ORDER BY name
                    """,
                    (f'%{search_term}%', f'%{search_term}%')
                )
                products = cursor.fetchall()
                
                products_list = []
                for product in products:
                    product_dict = dict(product)
                    if product_dict.get('price'):
                        product_dict['price'] = float(product_dict['price'])
                    products_list.append(product_dict)
                
                logger.info(f"Search for '{search_term}' returned {len(products_list)} products")
                return jsonify(products_list), 200
                
    except psycopg2.Error as e:
        logger.error(f"Database error in search_products: {str(e)}")
        return jsonify({
            'error': 'Database error',
            'message': 'Failed to search products in database'
        }), 500
        
    except Exception as e:
        logger.error(f"Unexpected error in search_products: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Not found',
        'message': 'The requested resource was not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500

# Store start time for uptime calculation
start_time = time.time()

# Initialize database pool when module is imported
def setup_application():
    """Initialize database connection pool"""
    if not initialize_db_pool():
        logger.error("Failed to initialize database pool. Application may not work correctly.")
        return False
    return True

if __name__ == '__main__':
    logger.info("Starting Product Viewer Backend API...")
    logger.info(f"Database Host: {DB_CONFIG['host']}")
    logger.info(f"Database Name: {DB_CONFIG['database']}")
    logger.info(f"Application Port: {APP_PORT}")
    
    # Initialize database pool
    if setup_application():
        logger.info("Application started successfully")
        app.run(
            host='0.0.0.0',
            port=APP_PORT,
            debug=DEBUG_MODE
        )
    else:
        logger.error("Failed to start application due to database connection issues")
        exit(1)
else:
    # When running with WSGI server (like gunicorn), initialize here
    setup_application()