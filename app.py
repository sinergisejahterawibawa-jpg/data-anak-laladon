import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(
    page_title="Data Anak Cluster de Laladon",
    page_icon="🏡",
    layout="wide"
)

# Koneksi Pintar (Bisa di Cloud maupun Lokal)
@st.cache_resource
def init_connection():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    try:
        # 1. Coba baca dari Streamlit Secrets (Jika diakses online/Cloud)
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    except Exception:
        # 2. Jika gagal (artinya dijalankan di laptop lokal), pakai file credentials.json
        creds = Credentials.from_service_account_file("credentials.json", scopes=scope)
        
    client = gspread.authorize(creds)
    return client

try:
    client = init_connection()
    sheet = client.open("Data Anak").sheet1
except Exception as e:
    st.error(f"Gagal terhubung ke Google Sheets: {e}")
    st.stop()

st.title("🏡 Aplikasi Pendataan Anak Cluster de Laladon")
st.markdown("Pencatatan data anak terpusat pada database Google Sheets **Data Anak**.")

# Fungsi untuk memuat ulang data otomatis dari database
def load_data():
    data = sheet.get_all_records()
    if not data:
        return pd.DataFrame(columns=["Nomor", "Nama Anak", "Umur", "Blok Rumah"])
    return pd.DataFrame(data)

# Load data awal
df = load_data()

# Form Input Data
with st.form("form_input_anak", clear_on_submit=True):
    st.subheader("➕ Tambah Data Anak Baru")
    
    col1, col2 = st.columns(2)
    with col1:
        nomor = st.text_input("Nomor Urut / ID")
        nama_anak = st.text_input("Nama Lengkap Anak")
    with col2:
        umur = st.number_input("Umur (Tahun)", min_value=0, max_value=18, step=1)
        blok_rumah = st.text_input("Blok Rumah (Kunci Unik, Cth: A1/12)")
    
    submitted = st.form_submit_button("Simpan Data")
    
    if submitted:
        # Validasi field kosong
        if not nomor or not nama_anak or not blok_rumah:
            st.warning("⚠️ Semua kolom wajib diisi!")
        else:
            # Cek duplikasi berdasarkan Blok Rumah (Kunci Unik)
            existing_blocks = df["Blok Rumah"].astype(str).str.strip().tolist() if not df.empty else []
            
            if blok_rumah.strip() in existing_blocks:
                st.error(f"❌ Gagal: Blok Rumah '{blok_rumah}' sudah terdaftar! Pengisian tidak boleh dobel.")
            else:
                # Simpan baris baru ke Google Sheets
                new_row = [str(nomor), str(nama_anak), int(umur), str(blok_rumah).strip()]
                sheet.append_row(new_row)
                st.success(f"✅ Data anak untuk Blok '{blok_rumah}' berhasil disimpan ke database!")
                
                # Load database otomatis setelah simpan
                df = load_data()
                st.rerun()

# Tampilkan Database / Tabel Data Anak secara Real-Time
st.markdown("---")
st.subheader("📋 Database Data Anak")

if df.empty:
    st.info("Belum ada data tersimpan di database.")
else:
    st.dataframe(df, use_container_width=True)
    st.caption(f"Total anak terdaftar: **{len(df)}** orang")
