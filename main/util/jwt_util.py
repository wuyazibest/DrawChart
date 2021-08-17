#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @File    : jwt_util.py
# @Time    : 2020/9/19 18:20
# @Author  : wuyazibest
# @Email   : wuyazibest@163.com
# @Desc   :
from datetime import timedelta, datetime

import jwt
from flask import current_app

CONFIG_DEFAULTS = {
    "JWT_DEFAULT_REALM": "Login Required",
    "JWT_AUTH_ENDPOINT": "jwt",
    "JWT_AUTH_USERNAME_KEY": "username",
    "JWT_AUTH_PASSWORD_KEY": "password",
    "JWT_ALGORITHM": "HS256",
    "JWT_LEEWAY": 10,
    "JWT_AUTH_HEADER_PREFIX": "JWT",
    "JWT_EXPIRATION_DELTA": 60 * 60 * 3,
    "JWT_NOT_BEFORE_DELTA": 0,
    "JWT_VERIFY_CLAIMS": ["signature", "exp", "nbf", "iat"],
    "JWT_REQUIRED_CLAIMS": ["exp", "iat", "nbf"]
    }


def config(name):
    return current_app.config.get(name) or CONFIG_DEFAULTS[name]


def jwt_encode_handler(identity):
    return _default_jwt_encode_handler(identity).decode("utf-8")


def jwt_decode_handler(token):
    payload = _default_jwt_decode_handler(token)
    return payload["identity"]


def _default_jwt_headers_handler(identity):
    return None


def _default_jwt_payload_handler(identity):
    iat = datetime.utcnow()
    exp = iat + timedelta(seconds=int(config("JWT_EXPIRATION_DELTA")))
    nbf = iat + timedelta(seconds=int(config("JWT_NOT_BEFORE_DELTA")))
    identity = getattr(identity, "id") or identity["id"]
    return {"exp": exp, "iat": iat, "nbf": nbf, "identity": identity}


def _default_jwt_encode_handler(identity):
    secret = config("SECRET_KEY")
    algorithm = config("JWT_ALGORITHM")
    required_claims = config("JWT_REQUIRED_CLAIMS")
    
    payload = _default_jwt_payload_handler(identity)
    missing_claims = list(set(required_claims) - set(payload.keys()))
    
    if missing_claims:
        raise RuntimeError("Payload is missing required claims: %s" % ", ".join(missing_claims))
    
    headers = _default_jwt_headers_handler(identity)
    
    return jwt.encode(payload, secret, algorithm=algorithm, headers=headers)


def _default_jwt_decode_handler(token):
    secret = config("SECRET_KEY")
    algorithm = config("JWT_ALGORITHM")
    leeway = timedelta(seconds=int(config("JWT_LEEWAY")))
    
    verify_claims = config("JWT_VERIFY_CLAIMS")
    required_claims = config("JWT_REQUIRED_CLAIMS")
    
    options = {
        "verify_" + claim: True
        for claim in verify_claims
        }
    
    options.update({
        "require_" + claim: True
        for claim in required_claims
        })
    
    return jwt.decode(token, secret, options=options, algorithms=[algorithm], leeway=leeway)
