import passlib.context

PASSWORD_CONTEXT = passlib.context.CryptContext(
    schemes=["pbkdf2_sha256"],
    default="pbkdf2_sha256",
    all__vary_rounds=0.1,
    pbkdf2_sha256__default_rounds=10000,
)


def encrypt_password(raw_password):
    return PASSWORD_CONTEXT.encrypt(raw_password)


def check_password(raw_password, encrypted_password):
    return PASSWORD_CONTEXT.verify(raw_password, encrypted_password)
