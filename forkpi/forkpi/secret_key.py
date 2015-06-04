from django.utils.crypto import get_random_string
import os

chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'

def random_key():
    return get_random_string(50, chars)

def write_to_path(path, text):
    with open(path, 'w') as f:
        f.write(text)
        os.chmod(path, 600)

def regenerate_secret_key(path):
    new_key = random_key()
    write_to_path(path, new_key)
    return new_key

def read_secret_key(path):
    try:
        with open(path) as f:
            key = f.read().strip()
            return key
    except IOError: # file does not exist; return default
        return regenerate_secret_key(path)