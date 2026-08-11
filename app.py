import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# Konfigurasi Halaman Web
st.set_page_config(
    page_title="Data Anak Cluster de Laladon",
    page_icon="🏡",
    layout="wide"
)

# KONEKSI PINTAR
@st.cache_resource
def init_connection():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    try:
        # Coba baca dari Streamlit Secrets (Jika diakses online/Cloud)
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    except Exception:
        # Jika gagal (dijalankan di laptop lokal), pakai file credentials.json
        creds = Credentials.from_service_account_file("credentials.json", scopes=scope)
        
    client = gspread.authorize(creds)
    return client

try:
    client = init_connection()
    # Membuka file Google Sheet dengan nama "Data Anak"
    sheet = client.open("Data Anak").sheet1
except Exception as e:
    st.error(f"Gagal terhubung ke Google Sheets: {e}")
    st.stop()

st.title("🏡 Aplikasi Pendataan Anak Cluster de Laladon")
st.markdown("Pencatatan data anak terpusat pada database Google Sheets **Data Anak**.")

# Fungsi untuk memuat ulang data otomatis
def load_data():
    data = sheet.get_all_records()
    if not data:
        return pd.DataFrame(columns=["Nomor", "Nama Anak", "Umur", "Blok Rumah"])
    return pd.DataFrame(data)

# Load data awal
df = load_data()

st.subheader("➕ Input Banyak Data Anak Sekaligus")

# Pengatur jumlah input di LUAR form (Begitu diklik, halaman langsung menyesuaikan otomatis tanpa Enter)
jumlah_input = st.selectbox(
    "Pilih jumlah data anak yang ingin dimasukkan sekaligus:", 
    options=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    index=0
)

st.markdown("---")

# Form Input Data
with st.form("form_batch_input"):
    inputs = []
    for i in range(int(jumlah_input)):
        st.markdown(f"**Anak ke-{i+1}**")
        col1, col2, col3 = st.columns([3, 1, 2])
        
        with col1:
            nama_anak = st.text_input(f"Nama Lengkap Anak {i+1}", key=f"nama_{i}")
        with col2:
            # Umur menggunakan selectbox (pilih langsung tap tanpa ketik/enter)
            umur = st.selectbox(
                f"Umur {i+1} (Thn)", 
                options=list(range(0, 19)), 
                index=7, # Default umur 7 tahun
                key=f"umur_{i}"
            )
        with col3:
            blok_rumah = st.text_input(f"Blok Rumah {i+1}", key=f"blok_{i}")
        
        st.markdown("")
        inputs.append({"nama": nama_anak, "umur": umur, "blok": blok_rumah})
    
    submitted = st.form_submit_button("🚀 Simpan Semua Data ke Database")
    
    if submitted:
        # Validasi apakah ada kolom nama atau blok yang kosong
        invalid = False
        for item in inputs:
            if not item["nama"].strip() or not item["blok"].strip():
                invalid = True
                break
        
        if invalid:
            st.warning("⚠️ Semua kolom Nama dan Blok Rumah wajib diisi!")
        else:
            # Ambil data terbaru untuk menghitung nomor urut kelanjutan
            current_df = load_data()
            start_num = len(current_df) + 1
            
            # Proses penyimpanan semua baris sekaligus ke Google Sheets
            rows_to_append = []
            for idx, item in enumerate(inputs):
                current_number = start_num + idx
                rows_to_append.append([
                    str(current_number), 
                    str(item["nama"]).strip(), 
                    int(item["umur"]), 
                    str(item["blok"]).strip()
                ])
            
            # Kirim semua data ke Google Sheets
            for row in rows_to_append:
                sheet.append_row(row)
                
            st.success(f"✅ Berhasil menyimpan {len(inputs)} data anak sekaligus ke database!")
            
            # Load database otomatis dan refresh tampilan
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