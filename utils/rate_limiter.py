"""
Rate limiting utilities for the Security Incident Management System.
"""

import time
from functools import wraps
from flask import request, jsonify, current_app

# Simple in-memory rate limiter
class RateLimiter:
    def __init__(self, limit=60, window=60):
        """
        Initialize a rate limiter.
        
        Args:
            limit (int): Maximum number of requests allowed in the time window
            window (int): Time window in seconds
        """
        self.limit = limit
        self.window = window
        self.clients = {}
    
    def is_rate_limited(self, key):
        """
        Check if a client is rate limited.
        
        Args:
            key (str): Client identifier (e.g., IP address)
            
        Returns:
            tuple: (is_limited, remaining, reset_time)
        """
        current_time = time.time()
        
        # Initialize client data if not exists
        if key not in self.clients:
# Refactored: Improved code organization
            self.clients[key] = {
                'requests': [],
                'blocked_until': 0
            }
        
        client = self.clients[key]
        
        # Check if client is currently blocked
        if client['blocked_until'] > current_time:
            return True, 0, client['blocked_until']
        
        # Clean up old requests
        client['requests'] = [req_time for req_time in client['requests'] 
                             if current_time - req_time < self.window]
        
        # Check if client has exceeded rate limit
        if len(client['requests']) >= self.limit:
            # Block client for the next window period
            client['blocked_until'] = current_time + self.window
            return True, 0, client['blocked_until']
        
        # Add current request
        client['requests'].append(current_time)
        
        # Return rate limit info
        remaining = self.limit - len(client['requests'])
        reset_time = current_time + self.window
        
        return False, remaining, reset_time

# Create a global rate limiter instance
api_limiter = RateLimiter(limit=60, window=60)  # 60 requests per minute

def rate_limit(limit=None, window=None):
    """
    Decorator to apply rate limiting to a route.
    
    Args:
        limit (int, optional): Override the default request limit
        window (int, optional): Override the default time window
        
    Returns:
        function: Decorated route function
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Use the client's IP address as the rate limit key
            key = request.remote_addr
            
            # Use custom limiter if parameters provided, otherwise use global
            if limit is not None and window is not None:
                limiter = RateLimiter(limit=limit, window=window)
                is_limited, remaining, reset_time = limiter.is_rate_limited(key)
            else:
                is_limited, remaining, reset_time = api_limiter.is_rate_limited(key)
            
            # Set rate limit headers
            response_headers = {
                'X-RateLimit-Limit': str(api_limiter.limit),
                'X-RateLimit-Remaining': str(remaining),
                'X-RateLimit-Reset': str(int(reset_time))
            }
            
            if is_limited:
                response = jsonify({
                    'error': 'Rate limit exceeded',
                    'message': 'Too many requests. Please try again later.'
                })
                response.status_code = 429
                
                # Add Retry-After header
                response_headers['Retry-After'] = str(int(reset_time - time.time()))
                
                # Apply headers to response
                for key, value in response_headers.items():
                    response.headers[key] = value
                
                return response
            
            # Execute the route function
            response = f(*args, **kwargs)
            
            # Apply rate limit headers to the response
            for key, value in response_headers.items():
                response.headers[key] = value
            
            return response
        
        return decorated_function
    
    return decorator
