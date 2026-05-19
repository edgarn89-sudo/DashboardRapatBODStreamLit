import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Judul Halaman Dashboard
st.set_page_config(page_title="BOD Dashboard", layout="wide")
st.title("📊 Dashboard Monitoring Tindak Lanjut Rapat BOD")

# 2. Membaca data CSV yang tadi kita siapkan
# Jika kolom Status Anda ada spasi tersembunyi, kita bersihkan dulu
df = pd.read_csv("data_rapat.csv")
df.columns = df.columns.str.strip()

# 3. Membuat Angka Ringkasan (Metrik) di Atas
total_data = len(df)
# Menghitung data yang berstatus Open / Closed (huruf besar/kecil disamakan)
df['Status_Clean'] = df['Status'].astype(str).str.strip().str.upper()
banyak_open = len(df[df['Status_Clean'] == 'OPEN'])
banyak_closed = len(df[df['Status_Clean'] == 'CLOSED'])

# Menampilkan metrik ke dalam 3 kolom berdampingan
m1, m2, m3 = st.columns(3)
m1.metric("Total Arahan Rapat", f"{total_data} Item")
m2.metric("Status OPEN (Belum Selesai)", f"{banyak_open} Item")
m3.metric("Status CLOSED (Selesai)", f"{banyak_closed} Item")

st.markdown("---")

# 4. Membuat Filter di Samping Kiri (Sidebar)
st.sidebar.header("Filter Data")
pilihan_pic = st.sidebar.multiselect("Pilih PIC / Divisi:", options=df['PIC'].unique())
pilihan_status = st.sidebar.multiselect("Pilih Status:", options=df['Status'].unique())

# Terapkan filter jika user memilih sesuatu
df_pilihan = df.copy()
if pilihan_pic:
    df_pilihan = df_pilihan[df_pilihan['PIC'].isin(pilihan_pic)]
if pilihan_status:
    df_pilihan = df_pilihan[df_pilihan['Status'].isin(pilihan_status)]

# 5. Membuat Grafik Visualisasi
g1, g2 = st.columns(2)

with g1:
    st.subheader("Grafik Status per PIC")
    fig_pic = px.histogram(df_pilihan, x="PIC", color="Status", barmode="group")
    st.plotly_chart(fig_pic, use_container_width=True)

with g2:
    st.subheader("Proporsi Berdasarkan Kategori")
    fig_kat = px.pie(df_pilihan, names="Kategori")
    st.plotly_chart(fig_kat, use_container_width=True)

st.markdown("---")

# 6. Menampilkan Tabel Data Asli di bawah grafik
st.subheader("Detail Tabel Kertas Kerja")
st.dataframe(df_pilihan, use_container_width=True, hide_index=True)