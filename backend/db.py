import firebase_admin
from firebase_admin import credentials, firestore
import pyrebase

cred = credentials.Certificate("firebase.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

firebaseConfig = {
    "apiKey": "AIzaSyD50RuWHYwR5f72rGu1RnfDOyTuv3YkLms",
    "authDomain": "sistembarang.firebaseapp.com",
    "databaseURL": "https://sistembarang-default-rtdb.asia-southeast1.firebasedatabase.app",
    "projectId": "sistembarang",
    "storageBucket": "sistembarang.appspot.com",
    "messagingSenderId": "879068795181",
    "appId": "1:879068795181:web:c8ad7a63390fe1880343a4"
};

firebase = pyrebase.initialize_app(firebaseConfig)
storage = firebase.storage()

def get_all_collection(collection, orderBy=None, direction=None):
    if orderBy:
        collects_ref = db.collection(collection).order_by(
            orderBy, direction=direction)
    else:
        collects_ref = db.collection(collection)
    collects = collects_ref.stream()
    RETURN = []
    for collect in collects:
        ret = collect.to_dict()
        ret['id'] = collect.id
        RETURN.append(ret)
    return RETURN





items = [
    {
        "id": 1,
        "nama_barang": "Samsung J3",
        "merk": "Samsung",
        "kategori": "Smarphone",
        "stok": 2,
        "harga": 10000
    },
    {
        "id": 2,
        "nama_barang": "Apple Iphone 13 ",
        "merk": "Apple",
        "kategori": "Smarphone",
        "stok": 3,
        "harga": 10000
    },
    {
        "id": 3,
        "nama_barang": "JBL Aura",
        "merk": "JBL",
        "kategori": "Speaker",
        "stok": 1,
        "harga": 10000
    },
    {
        "id": 4,
        "nama_barang": "Rexus",
        "merk": "Rexus",
        "kategori": "Keyboard",
        "stok": 1,
        "harga": 10000
    },
    {
        "id": 5,
        "nama_barang": "Kursi Gaming",
        "merk": "Fantech",
        "kategori": "Kursi",
        "stok": 1,
        "harga": 10000
    }
]
