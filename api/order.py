from flask import Flask, Blueprint, Response, request, jsonify
import pymysql
import json
from database.config import db_config

# Inisialisasi Flask app
app = Flask(__name__)

# Fungsi Koneksi Database
def connect_db():
    connection = pymysql.connect(**db_config)
    return connection

def close_db(connection, cursor=None):
    if cursor:
        cursor.close()
    connection.close()

# Blueprint API Film
order_api = Blueprint('order_api', __name__)

# Endpoint untuk membaca semua film
@order_api.route('/order', methods=['GET'])
def get_all_films():
    connection = connect_db() 
    
    # Menggunakan cursor untuk melakukan query SQL
    with connection.cursor() as cursor:
        try:
            sql = "SELECT * FROM tbl_order"
            cursor.execute(sql)
            films = cursor.fetchall() #Mengambil data QUERY
            json_data = json.dumps(films, default=str)  # default=str untuk menangani objek datetime
            return Response(json_data, content_type='application/json'), 200
        
        except Exception as e:
            # Memberikan respons kesalahan jika terjadi masalah
            return Response(f'Error: {str(e)}', content_type='text/plain'), 500
        finally:
            # Menutup koneksi ke database
            close_db(connection, cursor)

# Endpoint untuk membuat film baru
@order_api.route('/order', methods=['POST'])
def create_film():
    try:
        # Mendapatkan data film dari form data request
        film_data = request.form
        connection = connect_db() #koneksi database

        # Menggunakan cursor untuk melakukan query SQL
        with connection.cursor() as cursor:
            # Query untuk insert data film baru
            sql = "INSERT INTO tbl_order (kode_transaksi,nama_film,tanggal, jam_film, teater_film, harga_film,tempat_kursi,total_pembayaran) VALUES (%s, %s, %s, %s, %s, %s, %s,%s)"
            # Eksekusi query dengan data yang diterima dari request form
            cursor.execute(sql, (film_data['kode_transaksi'],film_data['nama_film'],film_data['tanggal'], film_data['jam_film'], film_data['teater_film'], film_data['harga_film'],film_data['tempat_kursi'],film_data['total_pembayaran']))
            connection.commit() #Commit Perubahan
        close_db(connection) #tutup koneksi

        # Memberikan respons berhasil
        return Response("Order Berhasil", content_type='text/html'), 201
    except Exception as e:
        # Memberikan respons kesalahan jika terjadi masalah
        return Response(f'Error: {str(e)}', content_type='text/plain'), 500

# Endpoint untuk mengupdate film berdasarkan ID
@order_api.route('/order/<int:id>', methods=['PATCH'])
def update_film(id):
    try:
        # Mendapatkan data film yang akan diupdate dari form data request
        film_data = request.form

        # Koneksi ke database
        connection = connect_db()

        # Menggunakan cursor untuk melakukan query SQL
        with connection.cursor() as cursor:
            # Query untuk mengambil data film berdasarkan ID
            select_sql = "SELECT * FROM tbl_order WHERE id=%s"
            cursor.execute(select_sql, id)
            film = cursor.fetchone()

            if film:
                # Update hanya bidang yang ada dalam form data
                update_fields = []
                update_values = []

                for key, value in film_data.items():
                    if key in film:
                        update_fields.append(f"{key}=%s")
                        update_values.append(value)

                if update_fields:
                    # Query untuk update data film berdasarkan ID
                    update_sql = f"UPDATE tbl_order SET {', '.join(update_fields)} WHERE id=%s"
                    update_values.append(id)

                    # Eksekusi query dengan data yang diterima dari request form dan ID sebagai parameter
                    cursor.execute(update_sql, tuple(update_values))
                    connection.commit()
                    return Response('Order Berhasil diupdate', content_type='text/plain'), 200
                
                else:
                    return Response('Tidak dapat diupdate', content_type='text/plain'), 400
            else:
                return Response('Film tidak ditemukan', content_type='text/plain'), 404
    except Exception as e:
        # Memberikan respons kesalahan jika terjadi masalah
        return Response(f'Error: {str(e)}', content_type='text/plain'), 500
    finally:
        # Menutup koneksi ke database
        close_db(connection)


# Endpoint untuk menghapus film berdasarkan ID
@order_api.route('/order/<int:id>', methods=['DELETE'])
def delete_film(id):
    try:
        # Koneksi ke database
        connection = connect_db()

        # Menggunakan cursor untuk melakukan query SQL
        with connection.cursor() as cursor:
            # Query untuk delete data film berdasarkan ID
            sql = "DELETE FROM tbl_order WHERE id=%s"
            # Eksekusi query dengan ID sebagai parameter
            cursor.execute(sql, id)
            # Commit perubahan ke database
            connection.commit()

        # Menutup koneksi ke database
        close_db(connection)

        # Memberikan respons berhasil
        return Response('Data berhasil dihapus', content_type='text/plain'), 200
    except Exception as e:
        # Memberikan respons kesalahan jika terjadi masalah
        return Response(f'Error: {str(e)}', content_type='text/plain'), 500
    
# Endpoint untuk membaca film berdasarkan ID
@order_api.route('/order/<int:id>', methods=['GET'])
def get_film_by_id(id):
    try:
        # Koneksi ke database
        connection = connect_db()

        # Menggunakan cursor untuk melakukan query SQL
        with connection.cursor() as cursor:
            # Query untuk mengambil data film berdasarkan ID
            sql = "SELECT * FROM tbl_order WHERE id=%s"
            # Eksekusi query dengan ID sebagai parameter
            cursor.execute(sql, id)
            # Mengambil data hasil query
            film = cursor.fetchone()

            # Mengonversi data menjadi format JSON menggunakan json.dumps
            json_data = json.dumps(film, default=str)  # default=str untuk menangani objek datetime

            # Mengembalikan data sebagai respons JSON
            return Response(json_data, content_type='application/json'), 200
    except Exception as e:
        # Memberikan respons kesalahan jika terjadi masalah
        return Response(f'Error: {str(e)}', content_type='text/plain'), 500
    finally:
        # Menutup koneksi ke database
        close_db(connection)

# Endpoint untuk membaca data distinct pada kolom tertentu
@order_api.route('/order/distinct/<column>', methods=['GET'])
def get_distinct_values(column):
    try:
        # Koneksi ke database
        connection = connect_db()

        # Menggunakan cursor untuk melakukan query SQL
        with connection.cursor() as cursor:
            # Query untuk mengambil data distinct pada kolom tertentu
            sql = f"SELECT DISTINCT {column} FROM tbl_film"
            cursor.execute(sql)
            # Mengambil data hasil query
            distinct_values = cursor.fetchall()

        # Menutup koneksi ke database
        close_db(connection)

        # Mengembalikan data sebagai respons JSON
        return jsonify(distinct_values), 200
    except Exception as e:
        # Memberikan respons kesalahan jika terjadi masalah
        return Response(f'Error: {str(e)}', content_type='text/plain'), 500

# Daftarkan Blueprint ke aplikasi Flask
app.register_blueprint(order_api)

# Jalankan aplikasi jika ini adalah file utama
if __name__ == '__main__':
    app.run(debug=True)
