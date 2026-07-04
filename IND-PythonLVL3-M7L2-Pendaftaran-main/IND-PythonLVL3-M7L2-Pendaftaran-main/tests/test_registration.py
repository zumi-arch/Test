# test_registration.py

import pytest
# Memanggil fungsi dari folder 'registration' dan file 'registration.py'
from registration.registration import add_user, initialize_users

def test_add_new_user():
    users = initialize_users()
    result = add_user(users, "new_user", "new_password")
    assert result == "Pengguna baru new_user berhasil ditambahkan."
    assert "new_user" in users
    assert users["new_user"] == "new_password"

def test_add_existing_user():
    users = initialize_users()
    result = add_user(users, "user1", "password1")
    assert result == "Pengguna dengan username ini sudah terdaftar."
    assert users["user1"] == "password1"