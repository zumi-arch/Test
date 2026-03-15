class Superhero:
    def __init__(self, real_name, superhero_name):
        self.__real_name = real_name  # Properti private (tersembunyi dari akses eksternal)
        self.superhero_name = superhero_name  # Properti publik

    # Metode getter untuk mengakses nama sebenarnya (identitas rahasia)
    @property
    def get_real_name(self):
        return self.__real_name

    # Metode setter untuk mengubah nama sebenarnya (identitas rahasia)
    @get_real_name.setter
    def set_real_name(self, new_real_name):
        if len(new_real_name) > 3:  # Menambahkan pengecekan panjang
            self.__real_name = new_real_name
        else:
            print("Nama sebenarnya harus terdiri dari setidaknya 4 karakter.")

    def reveal_identity(self):
        print(f"Saya adalah - {self.superhero_name}, identitas sebenarnya saya adalah - {self.__real_name}.")

# Membuat objek superhero
hulk = Superhero("Bruce Banner", "Hulk")

# Mengakses properti publik
print(hulk.superhero_name)

# Mengakses properti private (identitas rahasia) secara langsung akan menghasilkan error
# print(hulk.__real_name)

# Mengakses properti private dengan metode getter
#### Task 1. Gunakan metode getter untuk mengakses properti private dari objek hulk
print(hulk.get_real_name)

#### Task 2. Gunakan metode setter untuk mengubah nama sebenarnya Hulk menjadi "Doctor Bruce Banner"

hulk.reveal_identity()