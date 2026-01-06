import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
from pathlib import Path

st.set_page_config(page_title="Evaluasi Model", layout="wide")

st.title("📈 Evaluasi Akurasi Model Default")

# 1. KONFIGURASI PATH (Auto-Detect)
# Mencari lokasi file Excel secara otomatis
current_file_path = Path(__file__).resolve()
project_root = current_file_path.parent.parent 
data_folder = project_root / "data_model"
EXCEL_PATH = data_folder / "Evaluasi_Model_Default_With_Error.xlsx"

# Cek apakah file Excel ada
if not EXCEL_PATH.exists():
    st.error(f"❌ File Excel tidak ditemukan di: {EXCEL_PATH}")
    st.info("Harap masukkan file 'Evaluasi_Model_Default_With_Error.xlsx' (dari Colab) ke folder 'data_model'.")
    st.stop()

# 2. LOAD DATA DARI EXCEL
@st.cache_data
def load_evaluation_data(path):
    # Load Sheet Data Perbandingan
    df_eval = pd.read_excel(path, sheet_name="Data Perbandingan")
    
    # Load Sheet Ringkasan Metrik
    df_summary = pd.read_excel(path, sheet_name="Ringkasan Metrik")
    
    # Pastikan format tanggal benar
    df_eval["Tanggal"] = pd.to_datetime(df_eval["Tanggal"])
    # Buat string tanggal untuk tampilan tabel
    df_eval["Tanggal_Str"] = df_eval["Tanggal"].dt.strftime("%d-%m-%Y")
    
    return df_eval, df_summary

# 3. TAMPILAN DASHBOARD
try:
    df_eval, df_summary = load_evaluation_data(EXCEL_PATH)

    # --- A. METRIK UTAMA (Score) ---
    st.subheader("📊 Performa Model (Metrik)")
    
    # Ambil nilai dari Excel
    # Mencari baris yang mengandung kata 'RMSE', 'MAPE', 'R2'
    rmse_row = df_summary[df_summary['Metrik Evaluasi'].astype(str).str.contains("RMSE")]
    mape_row = df_summary[df_summary['Metrik Evaluasi'].astype(str).str.contains("MAPE")]
    r2_row   = df_summary[df_summary['Metrik Evaluasi'].astype(str).str.contains("R2")]

    # Ambil nilainya (jika ada)
    val_rmse = rmse_row.iloc[0]['Nilai Terformat'] if not rmse_row.empty else "-"
    val_mape = mape_row.iloc[0]['Nilai Terformat'] if not mape_row.empty else "-"
    val_r2   = r2_row.iloc[0]['Nilai Terformat']   if not r2_row.empty else "-"
    
    # Tampilkan di kartu
    col1, col2, col3 = st.columns(3)
    col1.metric("RMSE (terkecil)", f"{val_rmse}".replace('.', ',')) # Format indo
    col2.metric("MAPE (Error)", f"{val_mape}")
    col3.metric("R2 Score", f"{val_r2}")

    st.divider()

    # C. TABEL DATA
    st.subheader("📋 Rincian Data Tabel")
    
    # Format tabel untuk tampilan (Rp dan %)
    df_show = df_eval[["Tanggal_Str", "Harga Aktual", "Harga Prediksi", "Selisih (Rp)", "Error (%)"]].copy()
    
    # Kita pisah jadi 2 kolom: 10 Awal dan 10 Akhir
    c_table1, c_table2 = st.columns(2)
    
    with c_table1:
        st.write("🔹 **10 Data Pertama**")
        st.dataframe(df_show.head(10).style.format({
            "Harga Aktual": "Rp {:,.0f}",
            "Harga Prediksi": "Rp {:,.0f}",
            "Selisih (Rp)": "Rp {:,.0f}",
            "Error (%)": "{:.2f}%"
        }))
        
    with c_table2:
        st.write("🔹 **10 Data Terakhir**")
        st.dataframe(df_show.tail(10).style.format({
            "Harga Aktual": "Rp {:,.0f}",
            "Harga Prediksi": "Rp {:,.0f}",
            "Selisih (Rp)": "Rp {:,.0f}",
            "Error (%)": "{:.2f}%"
        }))

    # B. GRAFIK (Menggunakan Plotly agar Interaktif)
    st.subheader("📉 Grafik Perbandingan: Aktual vs Prediksi")
    
    fig = go.Figure()
    
    # Garis Harga Aktual
    fig.add_trace(go.Scatter(
        x=df_eval['Tanggal'], 
        y=df_eval['Harga Aktual'], 
        mode='lines', 
        name='Harga Aktual', 
        line=dict(color='blue', width=2)
    ))
    
    # Garis Harga Prediksi
    fig.add_trace(go.Scatter(
        x=df_eval['Tanggal'], 
        y=df_eval['Harga Prediksi'], 
        mode='lines', 
        name='Prediksi LSTM', 
        line=dict(color='red', width=2, dash='dash')
    ))

    fig.update_layout(
        title="Visualisasi Hasil Prediksi (Rupiah)",
        xaxis_title="Tanggal",
        yaxis_title="Harga (Rp)",
        hovermode="x unified",
        legend=dict(orientation="h", y=1.1)
    )
    st.plotly_chart(fig, use_container_width=True)

    # Expander untuk melihat semua data
    with st.expander("Lihat Semua Data (Full Table)"):
        st.dataframe(df_show.style.format({
            "Harga Aktual": "Rp {:,.0f}",
            "Harga Prediksi": "Rp {:,.0f}",
            "Selisih (Rp)": "Rp {:,.0f}",
            "Error (%)": "{:.2f}%"
        }))

except Exception as e:
    st.error(f"Terjadi kesalahan saat membaca Excel: {e}")
    st.write("Tips: Pastikan file Excel tidak sedang dibuka di aplikasi lain.")