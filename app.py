import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Data Anak Cluster de Laladon", page_icon="🏡", layout="wide")

# --- 2. FUNGSI-FUNGSI PENTING ---
@st.cache_resource
def init_connection():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    try:
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    except Exception:
        creds = Credentials.from_service_account_file("credentials.json", scopes=scope)
    return gspread.authorize(creds)

def load_data(sheet_obj):
    data = sheet_obj.get_all_records()
    if not data:
        return pd.DataFrame(columns=["Nomor", "Nama Anak", "Umur", "Blok Rumah"])
    return pd.DataFrame(data)

# --- 3. EKSEKUSI UTAMA ---
try:
    client = init_connection()
    sheet = client.open("Data Anak").sheet1
except Exception as e:
    st.error(f"Gagal terhubung ke Google Sheets: {e}")
    st.stop()

st.title("🏡 Aplikasi Pendataan Anak Cluster de Laladon")

# Memanggil data
df = load_data(sheet)

# Daftar Pilihan Blok Rumah (C1/4 sudah ditambahkan)
LIST_BLOK = [
    "A3", "A4", "A5", "A6", "B2/1", "B3/1", "B3/3", "B3/4", "B3/5", 
    "C1/1", "C1/2", "C1/3", "C1/4", "C2/1", "C2/2", "C2/3", "C2/4", "C2/5", "C3/2", 
    "D1", "D2", "D3", "D5", "D6", "D8", "D10", 
    "E1", "E2", "E4", "E5", "E8", "E9", "E10", "E11", "E12a", "E14", "E15", "E19", 
    "F1/2", "F2/2", "F2/4", "F2/5", "F2/6", 
    "G1/1", "G1/2", "G1/3", "G1/4", "G1/7", "G2/1", "G2/2"
]

# --- 4. UI / FORM INPUT ---
jumlah_input = st.selectbox("Pilih jumlah data anak yang ingin dimasukkan sekaligus:", options=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

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
    blok_rumah_utama = st.selectbox("Pilih Blok Rumah (Berlaku untuk semua anak di atas):", options=LIST_BLOK)
    submitted = st.form_submit_button("🚀 Simpan Semua Data")
    
    if submitted:
        # Cek apakah ada kolom nama yang kosong
        invalid_empty = any(not item["nama"].strip() for item in inputs)
        if invalid_empty:
            st.warning("⚠️ Harap isi nama anak pada semua baris yang aktif!")
        else:
            current_df = load_data(sheet)
            
            # Cek duplikasi nama
            existing_names = [str(n).strip().lower() for n in current_df["Nama Anak"].tolist()] if not current_df.empty else []
            batch_names = [str(item["nama"]).strip().lower() for item in inputs]
            
            if len(batch_names) != len(set(batch_names)):
                st.error("❌ Gagal: Ada nama anak yang sama di dalam daftar input saat ini!")
            elif any(name in existing_names for name in batch_names):
                st.error("❌ Gagal: Nama anak sudah terdaftar di database!")
            else:
                # Simpan ke Sheets
                start_num = len(current_df) + 1
                for idx, item in enumerate(inputs):
                    current_number = start_num + idx
                    sheet.append_row([str(current_number), str(item["nama"]).strip(), int(item["umur"]), str(blok_rumah_utama).strip()])
                st.success(f"✅ Berhasil menyimpan {len(inputs)} data anak ke Blok {blok_rumah_utama}!")
                st.rerun()

# --- 5. TAMPILAN TABEL ---
st.markdown("---")
st.subheader("📋 Database Data Anak")
if df.empty:
    st.info("Belum ada data.")
else:
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.caption(f"Total anak terdaftar: {len(df)} orang")