import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

st.set_page_config(page_title="Data Historis", layout="wide")

# NAMA FILE YANG BENAR
DATA_PATH = "data_model/data paling fix.csv"

st.title("📁 Data Historis (Hasil KNN)")

if os.path.exists(DATA_PATH):
    # Load Data dengan delimiter titik koma (;)
    df = pd.read_csv(DATA_PATH, delimiter=';')
    
    # Cleaning Format Tanggal
    if 'Date' in df.columns:
        df['Tanggal'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
        df = df.drop(columns=['Date'])
    
    # Fungsi Bersihkan Angka (Koma ke Titik)
    def clean_decimal(val):
        if isinstance(val, str):
            # Hapus Rp dan titik ribuan, ganti koma desimal jadi titik
            val = val.replace('Rp.', '').replace('Rp', '').replace('.', '') 
            return float(val.replace(',', '.'))
        return float(val)
    
    # Terapkan Cleaning pada kolom numerik (kecuali Tanggal)
    for col in df.columns:
        if col != 'Tanggal' and df[col].dtype == 'object':
            df[col] = df[col].apply(clean_decimal)

    # VISUALISASI
    st.subheader("Grafik Tren Harga & Cuaca")
    
    # Multiselect
    default_col = ['Price'] if 'Price' in df.columns else []
    pilihan = st.multiselect("Pilih Data:", df.columns.tolist(), default=default_col)
    
    if pilihan:
        fig = go.Figure()
        x_axis = df['Tanggal'] if 'Tanggal' in df.columns else df.index
        
        for col in pilihan:
            fig.add_trace(go.Scatter(x=x_axis, y=df[col], mode='lines', name=col))
            
        fig.update_layout(title="Visualisasi Data", xaxis_title="Waktu", hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)
    
    # Tabel
    with st.expander("Lihat Data Tabel"):
        st.dataframe(df)

else:
    st.error(f"File tidak ditemukan: {DATA_PATH}. Harap masukkan file 'data paling fix.csv' ke folder data_model.")