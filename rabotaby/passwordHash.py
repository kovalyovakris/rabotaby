import bcrypt
import re

def generate_password_hash(password: str) -> str:
    if not re.match(r'^(?=.*[A-Za-z])(?=.*\d).{6,}$', password):
        raise ValueError("Пароль должен содержать минимум 6 символов, буквы и цифры")
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def check_password_hash(password: str, stored_hash: str) -> bool:
    try:
        return bcrypt.checkpw(
            password.encode('utf-8'),
            stored_hash.encode('utf-8')
        )
    except:
        return False
