from pwdlib import PasswordHash

password_hasher = PasswordHash.recommended()


def hashing_password(password: str) -> str:
    return password_hasher.hash(password)


def checking_password(password: str, hashed_password: str) -> bool:
    return password_hasher.verify(password, hashed_password)
