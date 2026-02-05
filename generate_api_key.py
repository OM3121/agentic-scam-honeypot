#!/usr/bin/env python3
"""Generate a secure random API key for the hackathon backend API."""

import secrets
import string


def generate_api_key(length: int = 36) -> str:
    """
    Generate a secure random API key in the format: sk_honeypot_live_xxxxxxxxxxxxxxxxx
    
    Args:
        length: Length of the random suffix (default: 36 characters, making total 53 chars)
    
    Returns:
        A secure random string with prefix sk_honeypot_live_ followed by random chars
    """
    # Use only lowercase letters and numbers for the random part
    alphabet = string.ascii_lowercase + string.digits
    # Generate random suffix
    random_suffix = ''.join(secrets.choice(alphabet) for _ in range(length))
    # Combine with prefix to create final key
    return f"sk_honeypot_live_{random_suffix}"


if __name__ == "__main__":
    # Generate API key with 36-character random suffix
    # Total length will be 53 characters (17 char prefix + 36 random)
    api_key = generate_api_key(36)
    
    print(api_key)
    print()
    print("# .env file")
    print(f"API_KEY={api_key}")
    print()
    print("# HTTP request header")
    print(f"X-API-Key: {api_key}")
