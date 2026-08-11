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

# Form Input Data (Kolom Nomor dihapus)
with st.form("form_input_anak", clear_on_submit=True):
    st.subheader("➕ Tambah Data Anak Baru")
    
    col1, col2 = st.columns(2)
    with col1:
        nama_anak = st.text_input("Nama Lengkap Anak")
    with col2:
        umur = st.number_input("Umur (Tahun)", min_value=0, max_value=18, step=1)
        blok_rumah = st.text_input("Blok Rumah (Kunci Unik, Cth: A1/12)")
    
    submitted = st.form_submit_button("Simpan Data")
    
    if submitted:
        # Validasi field kosong
        if not nama_anak or not blok_rumah:
            st.warning("⚠️ Harap isi Nama dan Blok Rumah!")
        else:
            # Cek duplikasi
            existing_blocks = df["Blok Rumah"].astype(str).str.strip().tolist() if not df.empty else []
            
            if blok_rumah.strip() in existing_blocks:
                st.error(f"❌ Gagal: Blok Rumah '{blok_rumah}' sudah terdaftar!")
            else:
                # LOGIKA PENOMORAN OTOMATIS: Jumlah data saat ini + 1
                next_number = len(df) + 1
                
                # Simpan baris baru (Nomor diisi otomatis oleh variabel next_number)
                new_row = [str(next_number), str(nama_anak), int(umur), str(blok_rumah).strip()]
                sheet.append_row(new_row)
                st.success(f"✅ Data anak berhasil disimpan sebagai nomor {next_number}!")
                
                # Load database otomatis setelah simpan
                df = load_data()
                st.rerun()

# Tampilkan Database
st.markdown("---")
st.subheader("📋 Database Data Anak")

if df.empty:
    st.info("Belum ada data tersimpan di database.")
else:
    st.dataframe(df, use_container_width=True)
    st.caption(f"Total anak terdaftar: **{len(df)}** orang")