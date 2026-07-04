def calculate(num1, num2, operation):
    if operation == '+':
        return num1 + num2
    elif operation == '-':
        return num1 - num2
    elif operation == '*':
        return num1 * num2
    elif operation == '/':
        if num2 != 0:
            return num1 / num2
        else:
            return "Error: Pembagian dengan nol."
    else:
        return "Operasi tidak diketahui."


def main():
    print("Kalkulator sederhana. Masukkan dua angka dan pilih operasi.")
    num1 = float(input("Masukkan angka pertama: "))
    num2 = float(input("Masukkan angka kedua: "))
    operation = input("Pilih operasi (+, -, *, /): ")
    result = calculate(num1, num2, operation)
    print(f"Hasil: {result}")


if __name__ == "__main__":
    main()
