import streamlit as st
import pandas as pd
import numpy as np
import tensorflow as tf
import pickle
import plotly.graph_objects as go
from datetime import timedelta
import os

st.set_page_config(page_title="Forecasting", layout="wide")

MODEL_PATH = "data_model/prediksi_beras_lstm.keras"
SCALER_PATH = "data_model/minmax_scaler.pkl"
DATA_PATH = "data_model/data paling fix.csv" 

st.title("🔮 Prediksi Masa Depan")

@st.cache_resource
def load_assets():
    model = tf.keras.models.load_model(MODEL_PATH)
    with open(SCALER_PATH, "rb") as f:
        scaler = pickle.load(f)
    return model, scaler

def clean_decimal(val):
    if isinstance(val, str):
        val = val.replace('Rp.', '').replace('Rp', '').replace('.', '') 
        return float(val.replace(',', '.'))
    return float(val)

if os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH) and os.path.exists(DATA_PATH):
    
    model, scaler = load_assets()
    
    # Load Data (Pakai delimiter ;)
    df_raw = pd.read_csv(DATA_PATH, delimiter=';')
    df = df_raw.copy()
    
    # Handle Date
    date_col = None
    for col in df.columns:
        if 'date' in col.lower() or 'tanggal' in col.lower():
            date_col = col
            df['Tanggal'] = pd.to_datetime(df[col], dayfirst=True, errors='coerce')
    
    # Clean Numbers
    expected_cols = [
        'Tavg temperatur (oC)', 'RH_avg kelembapan (%)',
        'ss lama penyinaran matahari (jam)', 'ff_avg kecepatan angin (Knot)',
        'RR curah hujan (mm)', 'Price'
    ]
    for col in expected_cols:
        if col in df.columns and df[col].dtype == 'object':
            df[col] = df[col].apply(clean_decimal)
    
    df_final = df[expected_cols]
    
    # Normalize
    data_values = df_final.values
    if df_final['Price'].max() > 1.5:
        data_scaled = scaler.transform(data_values)
    else:
        data_scaled = data_values

    # Button
    if st.button("Mulai Prediksi 10 Hari", type="primary"):
        with st.spinner("Menghitung..."):
            
            window_size = 10
            future_days = 10
            
            last_sequence = data_scaled[-window_size:]
            current_sequence = last_sequence.copy()
            n_features = current_sequence.shape[1]
            
            preds_scaled = []
            
            for i in range(future_days):
                input_data = current_sequence.reshape(1, window_size, n_features)
                pred = model.predict(input_data, verbose=0)[0, 0]
                preds_scaled.append(pred)
                
                next_feat = current_sequence[-1].copy()
                next_feat[-1] = pred 
                current_sequence = np.vstack([current_sequence[1:], next_feat])
            
            dummy = np.zeros((future_days, n_features))
            dummy[:, -1] = preds_scaled
            preds_rupiah = scaler.inverse_transform(dummy)[:, -1]
            
            if date_col:
                last_date = df['Tanggal'].iloc[-1]
                future_dates = [last_date + timedelta(days=i+1) for i in range(future_days)]
            else:
                last_idx = df.index[-1]
                future_dates = np.arange(last_idx+1, last_idx+1+future_days)
            
            df_future = pd.DataFrame({'Tanggal': future_dates, 'Prediksi (Rp)': preds_rupiah})
            
            col1, col2 = st.columns([1, 2])
            with col1:
                st.dataframe(df_future.style.format({'Prediksi (Rp)': 'Rp {:,.0f}'}))
                
            with col2:
                fig = go.Figure()
                if date_col:
                    hist_x = df['Tanggal'].iloc[-30:]
                else:
                    hist_x = df.index[-30:]
                hist_y = df['Price'].iloc[-30:]
                
                fig.add_trace(go.Scatter(x=hist_x, y=hist_y, mode='lines+markers', name='Data Terakhir', line=dict(color='blue')))
                fig.add_trace(go.Scatter(x=future_dates, y=preds_rupiah, mode='lines+markers', name='Forecast', line=dict(color='red')))
                
                st.plotly_chart(fig, use_container_width=True)
else:
    st.error("File tidak lengkap.")