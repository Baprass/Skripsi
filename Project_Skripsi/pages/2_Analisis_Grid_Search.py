import streamlit as st
import pandas as pd
import numpy as np
import pickle
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from tensorflow.keras.models import load_model

# KONFIGURASI
st.set_page_config(
    page_title="Prediksi Harga Beras - LSTM",
    layout="wide"
)

WINDOW_SIZE = 10

# LOAD MODEL & DATA
@st.cache_resource
def load_all():
    results_df = pd.read_csv("data_model/hasil_evaluasi_grid_search.csv", sep=";", decimal=",")
    results_df.columns = results_df.columns.str.strip().str.upper()

    return  results_df


results_df = load_all()

# JUDUL
st.title("📈 Prediksi Harga Beras Menggunakan LSTM")
st.markdown("Model **LSTM terbaik** hasil Grid Search Hyperparameter")


# 📊 HALAMAN GRID SEARCH
st.subheader("Rekapitulasi Hasil Grid Search")
st.dataframe(results_df.sort_values("RMSE"), use_container_width=True)

#RMSE
st.subheader("📊 Perbandingan RMSE")
fig1, ax1 = plt.subplots(figsize=(12, 6))
chart1 = sns.barplot(
    data=results_df,
    x="BATCH_SIZE",
    y="RMSE",
    hue="LEARNING_RATE",
    ax=ax1
)
ax1.set_title("Perbandingan RMSE (Semakin Rendah Semakin Baik)")
for c in chart1.containers:
    chart1.bar_label(c, fmt="%.5f")
st.pyplot(fig1)

#R2
st.subheader("📊 Perbandingan R² Score")
fig2, ax2 = plt.subplots(figsize=(12, 6))
chart2 = sns.barplot(
    data=results_df,
    x="BATCH_SIZE",
    y="R2",
    hue="LEARNING_RATE",
    ax=ax2
)
ax2.set_title("Perbandingan R² Score (Semakin Tinggi Semakin Baik)")
for c in chart2.containers:
    chart2.bar_label(c, fmt="%.5f")
st.pyplot(fig2)

#MAPE
st.subheader("📊 Perbandingan MAPE")
fig3, ax3 = plt.subplots(figsize=(12, 6))
chart3 = sns.barplot(
    data=results_df,
    x="BATCH_SIZE",
    y="MAPE",
    hue="LEARNING_RATE",
    ax=ax3
)
ax3.set_title("Perbandingan MAPE (Semakin Rendah Semakin Baik)")
for c in chart3.containers:
    chart3.bar_label(c, fmt="%.5f")
st.pyplot(fig3)

best = results_df.loc[results_df["RMSE"].idxmin()]
st.success(
        f"""
🏆 **Model Terbaik**
- Batch Size : {int(best['BATCH_SIZE'])}
- Learning Rate : {best['LEARNING_RATE']}
- RMSE : {best['RMSE']:.5f}
- MAPE : {best['MAPE']:.5f}
- R² : {best['R2']:.5f}
"""
    )
