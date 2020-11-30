from flask import current_app
import hashlib


def encrypt_string(s):
    s = s.lower().strip()
    s += current_app.config["SECRET_KEY"]
    return hashlib.sha512(str.encode(s)).hexdigest()
