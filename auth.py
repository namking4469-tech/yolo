"""회원가입 · 로그인 · 비밀번호 관리."""

import hashlib
import hmac
import re
import secrets
import sqlite3

import streamlit as st

import db

USERNAME_RE = re.compile(r"^[A-Za-z0-9_가-힣]{3,20}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_PASSWORD = 8


def _hash(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), 200_000).hex()


def validate_password(password: str, confirm: str) -> list[str]:
    errors = []
    if len(password) < MIN_PASSWORD:
        errors.append(f"비밀번호는 {MIN_PASSWORD}자 이상이어야 합니다.")
    if password != confirm:
        errors.append("비밀번호 확인이 일치하지 않습니다.")
    return errors


def validate_signup(username: str, email: str, password: str, confirm: str) -> list[str]:
    errors = []
    if not USERNAME_RE.match(username):
        errors.append("아이디는 3~20자의 한글, 영문, 숫자, 밑줄(_)만 쓸 수 있습니다.")
    if not EMAIL_RE.match(email):
        errors.append("이메일 형식이 올바르지 않습니다.")
    return errors + validate_password(password, confirm)


def signup(username: str, email: str, password: str, confirm: str) -> list[str]:
    """회원을 만든다. 성공하면 빈 목록, 실패하면 오류 메시지 목록을 돌려준다."""
    username, email = username.strip(), email.strip()
    errors = validate_signup(username, email, password, confirm)
    if errors:
        return errors
    salt = secrets.token_hex(16)
    try:
        db.execute(
            "INSERT INTO users (username, email, password_hash, salt, created_at) VALUES (?, ?, ?, ?, ?)",
            (username, email, _hash(password, salt), salt, db.now()),
        )
    except sqlite3.IntegrityError:
        return ["이미 사용 중인 아이디 또는 이메일입니다."]
    return []


def _check(username: str, password: str) -> dict | None:
    rows = db.query("SELECT * FROM users WHERE username = ?", (username.strip(),))
    if rows and hmac.compare_digest(rows[0]["password_hash"], _hash(password, rows[0]["salt"])):
        return rows[0]
    return None


def login(username: str, password: str) -> bool:
    row = _check(username, password)
    if row is None:
        return False
    st.session_state.user = {k: row[k] for k in ("id", "username", "email", "created_at")}
    return True


def logout() -> None:
    st.session_state.pop("user", None)


def current_user() -> dict | None:
    return st.session_state.get("user")


def change_password(user: dict, old: str, new: str, confirm: str) -> list[str]:
    if _check(user["username"], old) is None:
        return ["현재 비밀번호가 올바르지 않습니다."]
    errors = validate_password(new, confirm)
    if errors:
        return errors
    salt = secrets.token_hex(16)
    db.execute("UPDATE users SET password_hash = ?, salt = ? WHERE id = ?", (_hash(new, salt), salt, user["id"]))
    return []


def delete_account(user: dict) -> None:
    """회원을 지운다. 그 회원이 쓴 게시글도 함께 지워진다(ON DELETE CASCADE)."""
    db.execute("DELETE FROM users WHERE id = ?", (user["id"],))
    logout()
