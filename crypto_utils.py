import base64
import hashlib
import re
from cryptography.fernet import Fernet
from werkzeug.security import generate_password_hash, check_password_hash

SECRET_PHRASE = b"SaepClinicaVet2026LGPDSecretKey!"
FERNET_KEY = base64.urlsafe_b64encode(hashlib.sha256(SECRET_PHRASE).digest())
cipher = Fernet(FERNET_KEY)

def format_cpf(cpf: str) -> str:
    """Padroniza o formato do CPF para 000.000.000-00."""
    if not cpf:
        return ""
    digits = re.sub(r"\D", "", cpf)
    if len(digits) == 11:
        return f"{digits[0:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:11]}"
    return cpf.strip()

def mask_cpf(cpf: str) -> str:
    """Mascara o CPF para exibição segura em conformidade com a LGPD (ex: 123.***.***-01)."""
    formatted = format_cpf(cpf)
    if len(formatted) == 14 and formatted[3] == '.' and formatted[7] == '.' and formatted[11] == '-':
        return f"{formatted[0:3]}.***.***-{formatted[12:14]}"
    return formatted

def encrypt_cpf(cpf: str) -> str:
    """Criptografa o CPF do tutor utilizando algoritmo AES-128 via Fernet (CBC + HMAC)."""
    if not cpf:
        return ""
    clean_cpf = format_cpf(cpf)
    encrypted_bytes = cipher.encrypt(clean_cpf.encode("utf-8"))
    return encrypted_bytes.decode("utf-8")

def decrypt_cpf(encrypted_token: str) -> str:
    """Descriptografa o CPF do tutor armazenado no banco de dados."""
    if not encrypted_token:
        return ""
    try:
        decrypted_bytes = cipher.decrypt(encrypted_token.strip().encode("utf-8"))
        return decrypted_bytes.decode("utf-8")
    except Exception:
        # Caso o dado não esteja criptografado (legado/fallback)
        return encrypted_token

def hash_user_password(password: str) -> str:
    """Gera hash seguro da senha do usuário."""
    return generate_password_hash(password)

def verify_user_password(password_hash: str, password: str) -> bool:
    """Valida a senha fornecida contra o hash armazenado."""
    return check_password_hash(password_hash, password)
