import random
import string
import re


def generate_verification_code(length=4):
    """Генерируем случайную строку чисел указанной длины"""
    code = ''.join(random.choices(string.digits, k=length))
    return code
