import pytest
import string
from generate_api_key import generate_api_key


def test_api_key_length():
    """Test that generated API key has correct length (prefix + random suffix)"""
    prefix = "sk_honeypot_live_"
    
    key = generate_api_key(36)
    assert len(key) == len(prefix) + 36
    assert key.startswith(prefix)
    
    # Test with minimum length
    key_min = generate_api_key(32)
    assert len(key_min) == len(prefix) + 32
    
    # Test with maximum length
    key_max = generate_api_key(40)
    assert len(key_max) == len(prefix) + 40


def test_api_key_contains_only_lowercase_and_numbers():
    """Test that API key random suffix contains only lowercase letters and numbers"""
    prefix = "sk_honeypot_live_"
    allowed_chars = set(string.ascii_lowercase + string.digits)
    
    # Test multiple generations to ensure consistency
    for _ in range(10):
        key = generate_api_key(36)
        assert key.startswith(prefix), f"Key doesn't start with expected prefix: {prefix}"
        # Check only the random suffix (after the prefix)
        suffix = key[len(prefix):]
        suffix_chars = set(suffix)
        assert suffix_chars.issubset(allowed_chars), f"Suffix contains invalid characters: {suffix_chars - allowed_chars}"


def test_api_key_no_special_characters():
    """Test that API key suffix contains no invalid special characters"""
    prefix = "sk_honeypot_live_"
    # Underscore is valid in the prefix, so we only check the suffix
    invalid_chars = set(string.punctuation + string.whitespace) - {'_'}
    
    for _ in range(10):
        key = generate_api_key(36)
        assert key.startswith(prefix), f"Key doesn't start with expected prefix: {prefix}"
        # Check only the random suffix (after the prefix)
        suffix = key[len(prefix):]
        suffix_chars = set(suffix)
        assert suffix_chars.isdisjoint(invalid_chars), f"Suffix contains invalid special characters: {suffix_chars & invalid_chars}"


def test_api_key_no_uppercase():
    """Test that API key contains no uppercase letters"""
    for _ in range(10):
        key = generate_api_key(36)
        assert key == key.lower(), "Key contains uppercase letters"


def test_api_key_randomness():
    """Test that generated keys are different (high entropy)"""
    keys = [generate_api_key(36) for _ in range(100)]
    # All keys should be unique
    assert len(set(keys)) == 100, "Generated keys are not sufficiently random"


def test_api_key_suitable_for_http_header():
    """Test that API key is suitable for HTTP header value"""
    key = generate_api_key(36)
    
    # Should not contain whitespace
    assert ' ' not in key
    assert '\t' not in key
    assert '\n' not in key
    assert '\r' not in key
    
    # Should not contain special characters that could cause issues
    invalid_header_chars = ['\0', '\r', '\n', ':']
    for char in invalid_header_chars:
        assert char not in key
