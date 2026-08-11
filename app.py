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

# Daftar Pilihan Blok Rumah
LIST_BLOK = [
    "A3", "A4", "A5", "A6", "B2/1", "B3/1", "B3/3", "B3/4", "B3/5", 
    "C1/1", "C1/2", "C1/3", "C2/1", "C2/2", "C2/3", "C2/4", "C2/5", "C3/2", 
    "D1", "D2", "D3", "D5", "D6", "D8", "D10", 
    "E1", "E2", "E4", "E5", "E8", "E9", "E10", "E11", "E12a", "E14", "E15", "E19", 
    "F1/2", "F2/2", "F2/4", "F2/5", "F2/6", 
    "G1/1", "G1/2", "G1/3", "G1/4", "G1/7", "G2/1", "G2/2"
]

# KONEKSI PINTAR
@st.cache_resource
def init_connection():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    try:
        # Coba baca dari Streamlit Secrets
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    except Exception:
        # Jika lokal
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

# Pengatur jumlah input di LUAR form
jumlah_input = st.selectbox(
    "Pilih jumlah data anak yang ingin dimasukkan sekaligus:", 
    options=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    index=0
)

# Form Input Data
with st.form("form_batch_input"):
    inputs = []
    for i in range(int(jumlah_input)):
        col1, col2 = st.columns([3, 1])
        with col1:
            nama_anak = st.text_input(f"Nama Anak {i+1}", key=f"nama_{i}")
        with col2:
            umur = st.selectbox(f"Umur {i+1}", options=list(range(0, 19)), index=7, key=f"umur_{i}")
        
        inputs.append({"nama": nama_anak, "umur": umur})
    
    st.markdown("---")
    # Blok Rumah diletakkan di akhir dan berlaku untuk semua
    blok_rumah_utama = st.selectbox("Pilih Blok Rumah (Berlaku untuk semua anak di atas):", options=LIST_BLOK)
    
    submitted = st.form_submit_button("🚀 Simpan Semua Data")
    
    if submitted:
        # Validasi nama (karena blok sudah pasti terisi)
        invalid = False
        for item in inputs:
            if not item["nama"].strip():
                invalid = True
                break
        
        if invalid:
            st.warning("⚠️ Harap isi nama anak pada semua baris yang aktif!")
        else:
            current_df = load_data()
            start_num = len(current_df) + 1
            
            rows_to_append = []
            for idx, item in enumerate(inputs):
                current_number = start_num + idx
                rows_to_append.append([
                    str(current_number), 
                    str(item["nama"]).strip(), 
                    int(item["umur"]), 
                    str(blok_rumah_utama).strip()
                ])
            
            for row in rows_to_append:
                sheet.append_row(row)
                
            st.success(f"✅ Berhasil menyimpan {len(inputs)} data anak ke Blok {blok_rumah_utama}!")
            st.rerun()

# Tabel Database
st.markdown("---")
st.subheader("📋 Database Data Anak")
df = load_data()
if df.empty:
    st.info("Belum ada data.")
else:
    st.dataframe(df, use_container_width=True)
    st.caption(f"Total anak terdaftar: {len(df)} orang")