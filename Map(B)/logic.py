import sqlite3
import matplotlib

matplotlib.use('Agg')  # Menginstal backend Matplotlib untuk menyimpan file dalam memori tanpa menampilkan jendela
import matplotlib.pyplot as plt
import cartopy.crs as ccrs  # Mengimpor modul yang akan memungkinkan kita bekerja dengan proyeksi peta
import math

class DB_Map():
    def __init__(self, database):
        self.database = database  # Menginisiasi jalur database

    def create_user_table(self):
        conn = sqlite3.connect(self.database)  # Menghubungkan ke database
        with conn:
            # Membuat tabel, jika tidak ada, untuk menyimpan kota pengguna
            conn.execute('''CREATE TABLE IF NOT EXISTS users_cities (
                                user_id INTEGER,
                                city_id TEXT,
                                FOREIGN KEY(city_id) REFERENCES cities(id)
                            )''')
            conn.commit()  # Menyimpan perubahan

    def add_city(self, user_id, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            # Mencari kota dalam database berdasarkan nama
            cursor.execute("SELECT id FROM cities WHERE city=?", (city_name,))
            city_data = cursor.fetchone()
            if city_data:
                city_id = city_data[0]
                # Menambahkan kota ke daftar kota pengguna
                conn.execute('INSERT INTO users_cities VALUES (?, ?)', (user_id, city_id))
                conn.commit()
                return 1  # Menunjukkan bahwa operasi berhasil
            else:
                return 0  # Menunjukkan bahwa kota tidak ditemukan

    def select_cities(self, user_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            # Memilih semua kota pengguna
            cursor.execute('''SELECT cities.city 
                            FROM users_cities  
                            JOIN cities ON users_cities.city_id = cities.id
                            WHERE users_cities.user_id = ?''', (user_id,))
            cities = [row[0] for row in cursor.fetchall()]
            return cities  # Mengembalikan daftar kota pengguna

    def get_coordinates(self, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            # Mendapatkan koordinat kota berdasarkan nama
            cursor.execute('''SELECT lat, lng
                            FROM cities  
                            WHERE city = ?''', (city_name,))
            coordinates = cursor.fetchone()
            return coordinates  # Mengembalikan koordinat kota

    def create_graph(self, path, cities):
        if not cities:
            return False

        # Membersihkan plot lama agar tidak menumpuk
        plt.clf()

        # Menginisialisasi peta bumi baru dengan proyeksi PlateCarree
        fig = plt.figure(figsize=(10, 6))
        ax = plt.axes(projection=ccrs.PlateCarree())
        
        # Menambahkan gambar latar geografi bumi
        ax.stock_img()
        ax.coastlines(resolution='110m', color='black', linewidth=1)

        longitudes = []
        latitudes = []
        valid_cities = []

        # Ambil koordinat untuk tiap nama kota di list
        for city in cities:
            coord = self.get_coordinates(city)
            if coord:
                latitudes.append(coord[0])
                longitudes.append(coord[1])
                valid_cities.append(city)

        if not valid_cities:
            plt.close()
            return False

        # Plot titik lokasi kota (marker bulat)
        ax.scatter(longitudes, latitudes, color='blue', edgecolors='black', s=80, 
                   transform=ccrs.PlateCarree(), zorder=6)

        # Tambahkan label teks nama kota
        for i, name in enumerate(valid_cities):
            ax.text(longitudes[i] + 1.0, latitudes[i] + 1.0, name, color='black', fontsize=9, 
                    weight='bold', transform=ccrs.PlateCarree(),
                    bbox=dict(boxstyle='square,pad=0.1', facecolor='white', alpha=0.7, edgecolor='none'),
                    zorder=7)

        # Menghubungkan kota secara berurutan jika jumlah kota > 1
        if len(valid_cities) > 1:
            for i in range(len(valid_cities) - 1):
                self.draw_distance(valid_cities[i], valid_cities[i+1])

        plt.title('Peta Rute Lokasi dan Jarak Kota Pengguna', fontsize=12, weight='bold', pad=10)
        
        # Simpan grafik peta ke file path tujuan
        plt.savefig(path, bbox_inches='tight', dpi=150)
        plt.close()
        return True

    def draw_distance(self, city1, city2):
        # Menggambar garis antara dua kota untuk menampilkan jarak
        coord1 = self.get_coordinates(city1)
        coord2 = self.get_coordinates(city2)

        if not coord1 or not coord2:
            return

        lat1, lng1 = coord1[0], coord1[1]
        lat2, lng2 = coord2[0], coord2[1]

        # Mengambil objek sumbu (axis) Cartopy yang aktif saat ini
        ax = plt.gca()

        # Gambar garis lintasan melengkung (Geodetic) yang menghubungkan kedua koordinat kota
        ax.plot([lng1, lng2], [lat1, lat2], color='red', linewidth=2, 
                linestyle='--', transform=ccrs.Geodetic(), zorder=4)

        # Hitung jarak nyata menggunakan rumus matematika Haversine (km)
        R = 6371.0  # Radius rata-rata bumi dalam Km
        
        lat1_rad = math.radians(lat1)
        lng1_rad = math.radians(lng1)
        lat2_rad = math.radians(lat2)
        lng2_rad = math.radians(lng2)
        
        dlat = lat2_rad - lat1_rad
        dlng = lng2_rad - lng1_rad
        
        a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c

        # Taruh box teks informasi jarak tepat di tengah garis lintasan rute
        mid_lng = (lng1 + lng2) / 2
        mid_lat = (lat1 + lat2) / 2
        ax.text(mid_lng, mid_lat, f"{distance:.1f} km", color='darkred', fontsize=8, weight='bold',
                transform=ccrs.PlateCarree(),
                bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor='red', alpha=0.7),
                zorder=5)


if __name__ == "__main__":
    m = DB_Map("database.db")  # Membuat objek yang akan berinteraksi dengan database
    m.create_user_table()   # Membuat tabel dengan kota pengguna, jika tidak sudah ada