import pytest
from calculate.calculator_program import calculate

def test_calculate_addition():
    assert calculate(1, 1, '+') == 2

def test_calculate_division():
    assert calculate(8, 2, '/') == 4

def test_calculate_subtraction():
    assert calculate(10, 5, '-') == 5

def test_calculate_multiplication():
    assert calculate(3, 4, '*') == 12

def test_calculate_unknown_operation():
    assert calculate(5, 5, 'tidak diketahui') == "Operasi tidak diketahui."

'''
Tugas. Saat ini ada tiga unit-test yang sudah dibuat
Program mengecek apakah kalkulator berfungsi dengan benar untuk operasi penjumlahan, pembagian dan operasi yang tidak dikenal
Kamu perlu menambahkan minimal tes untuk operasi berikut:
1. Pengurangan
2. Perkalian
Akan lebih keren kalau kamu bisa membuat dan menambahkan tes-tes tambahan
'''
