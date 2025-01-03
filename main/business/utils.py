import secrets
import string


def generate_random_string(length=10):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(secrets.choice(characters) for i in range(length))
    return random_string
