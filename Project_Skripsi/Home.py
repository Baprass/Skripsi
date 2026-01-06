import streamlit as st
import os

st.set_page_config(
    page_title="Sistem Prediksi Beras",
    page_icon="🌾",
    layout="wide"
)

st.title("🌾 Dashboard Sistem Prediksi Harga Beras")
st.markdown("""
### Selamat Datang
Aplikasi ini dirancang untuk memprediksi harga beras menggunakan metode **Long Short-Term Memory (LSTM)**.

**Struktur Aplikasi:**
1. **Data Historis**: Melihat tren data asli (Hasil Imputasi KNN).
2. **Analisis Grid Search**: Melihat hasil pencarian hyperparameter terbaik.
3. **Evaluasi Model**: Menguji akurasi model (RMSE, MAPE, R2).
4. **Prediksi Masa Depan**: Meramal harga beras 10 hari ke depan.
""")

# Cek Ketersediaan File
files_needed = {
    "Model LSTM": "data_model/prediksi_beras.keras",
    "Scaler": "data_model/minmax_scaler.pkl",
    "Data Utama (KNN)": "data_model/data paling fix.csv", 
}

col1, col2 = st.columns(2)
with col1:
    st.info("Status File Sistem:")
    for name, path in files_needed.items():
        if os.path.exists(path):
            st.success(f"✅ {name} ditemukan")
        else:
            st.error(f"❌ {name} TIDAK DITEMUKAN! ({path})")

st.write("---")
st.info("👈 Silakan pilih menu di Sidebar sebelah kiri untuk memulai.")