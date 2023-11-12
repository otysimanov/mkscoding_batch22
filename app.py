from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from backend.db import db, storage, get_all_collection
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)

app.secret_key = '1n1Ad4lahs3cr3tke7'

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user' in session:
            return f(*args, **kwargs)
        else:
            flash('Anda harus login', 'danger')
            return redirect(url_for('login'))
    return wrapper


# Halaman Utama
@app.route('/')
def index():
    title = 'Halaman Login'
    return render_template('index.html', title=title)

# Register
@app.route('/register/', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        # ambil data dari form
        data = {}
        # cek password tidak sama dengan password_1
        if request.form['password'] != request.form['password_1']:
            flash('Password Tidak Sama', 'danger') 
            return redirect(url_for('register'))
        elif len(request.form['password']) <= 3:
            flash('Password Tidak Aman', 'danger') 
            return redirect(url_for('register'))
        
        # cek ke dalam database
        username = request.form['username'].lower()
        user = db.collection('users').document(username).get().to_dict()
        # cek apakah username sudah terdaftar?
        if user:
            # kalau terdaftar kembali ke halaman register
            flash('Username Sudah Terdaftar', 'danger') 
            return redirect(url_for('register'))
        # password di enkripsi
        # from werkzeug.security import generate_password_hash
        data['password'] = generate_password_hash(request.form['password'], 'sha256')
        data['username'] = username

        # simpan ke dalam collection users
        db.collection('users').document(username).set(data)
        # redirect ke halaman login
        flash('Berhasil Register', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

# halaman login
@app.route('/login/', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        # ambil data dari form
        data = {
            'username' : request.form['username'].lower(),
            'password' : request.form['password']

        }
        # cek data users ada atau tidak
        # ambil data dari database
        user = db.collection('users').document(data['username']).get().to_dict()
        # jika ada
        if user:
            # cek password
            if check_password_hash(user['password'], data['password']):
                session['user'] = user
                flash('Berhasil Login', 'success')
                return redirect(url_for('barang'))
            else:
                flash('Username / Password Salah', 'danger')
                return redirect(url_for('login'))
        # jika tidak ada
        else:

            # redirect
            flash('Username / Password Salah', 'danger')
            return redirect(url_for('login'))

    if 'user' in session:
        return redirect(url_for('barang'))
    return render_template('login.html')



@app.route('/logout')
def logout():
    session.clear()
    flash('Berhasil Logout', 'danger')
    return redirect(url_for('login'))

# Halaman Barang
@app.route('/barang')
@login_required
def barang():

    # ini adalah mengambil semua document yang ada di collection
    docs = db.collection('barang').stream()
    # selanjutnya buat variable tipe data list kosong
    items = []
    # lakukan pengulangan terhadap data 
    for doc in docs:
        # konversi data snapshoot jadi dictonary dengan to_dict()
        d = doc.to_dict()
        # mengambil ID dokumen
        d['id'] = doc.id
        # memasukkan document ke dalam list items
        items.append(d)
    return render_template('barang/barang.html', items=items)

# Tambah Barang
@app.route('/barang/tambah', methods=['GET', 'POST'])
def tambah_barang():
    if request.method == 'POST':
        # tangkap dulu data dari form
        data = {
            'nama_barang' : request.form['nama_barang'],
            'merk' : request.form['merk'],
            'kategori' : request.form['kategori'],
            'stok' : request.form['stok'],
            'harga' : request.form['harga'],
        }

        # upload gambar
        if 'gambar' in request.files and request.files['gambar']:
            gambar = request.files['gambar']
            ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
            filename = gambar.filename
            lokasi = f'barang/{filename}'
            ext = filename.rsplit('.', 1)[1].lower()

            if ext in ALLOWED_EXTENSIONS:
                # ini adalah untuk upload ke storage firebase
                storage.child(lokasi).put(gambar)
                # menyimpan URL gambar
                data['gambar'] = storage.child(lokasi).get_url(None)
            else:
                flash('File Tidak Di perbolehkan', 'danger')
                return redirect(url_for('barang'))

        # gamBar.JPG
        # ['gambar', 'JPG']

        # simpan ke database
        # cara tambah data dari backend ke firestore
        db.collection('barang').document().set(data)
        flash('Berhasil Tambah Barang', 'success')
        
        # kembali ke halaman barang
        return redirect('/barang')
    

    kategori = get_all_collection('kategori')

    return render_template('barang/tambah.html', kategori=kategori)

@app.route('/barang/edit/<uid>', methods=['POST', 'GET'])
@login_required
def edit_barang(uid):
    if request.method == 'POST':
        # tangkap dulu data dari form
        data = {
            'nama_barang' : request.form['nama_barang'],
            'merk' : request.form['merk'],
            'kategori' : request.form['kategori'],
            'stok' : request.form['stok'],
            'harga' : request.form['harga'],
        }

        # simpan ke database
        # cara tambah data dari backend ke firestore
        db.collection('barang').document(uid).update(data)
        flash('Berhasil Edit Barang', 'success')
        # kembali ke halaman barang
        return redirect('/barang')


    barang = db.collection('barang').document(uid).get().to_dict()
    return render_template('barang/edit.html', data=barang)

# Lihat Barang
@app.route('/barang/lihat/<uid>')
@login_required
def lihat_barang(uid):
    # memanggil data berdasarkan ID
    data = db.collection('barang').document(uid).get().to_dict()
    # return jsonify(data)
    return render_template('barang/lihat.html', data=data)

# Hapus Barang
@app.route('/barang/hapus/<uid>')
@login_required
def hapus_barang(uid):
    db.collection('barang').document(uid).delete()
    flash('Berhasil Hapus Barang', 'danger')
    return redirect(url_for('barang'))


# KATEGORI
@app.route('/kategori', methods=['POST', 'GET'])
@login_required
def kategori():
    if request.method == 'POST':
        data = {
            'nama_kategori' : request.form['nama_kategori']
        }

        db.collection('kategori').document().set(data)
        flash('Berhasil Menambah Kategori', 'success')
        return redirect(url_for('kategori'))
    
    # ini adalah mengambil semua document yang ada di collection
    docs = db.collection('kategori').stream()
    # selanjutnya buat variable tipe data list kosong
    items = []
    # lakukan pengulangan terhadap data 
    for doc in docs:
        # konversi data snapshoot jadi dictonary dengan to_dict()
        d = doc.to_dict()
        # mengambil ID dokumen
        d['id'] = doc.id
        # memasukkan document ke dalam list items
        items.append(d)
    return render_template('kategori/kategori.html', items=items)




if __name__ == '__main__':
    app.run(debug=True, port=5005)