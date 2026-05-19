import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Konfigurasi Halaman Utama Dashboard
st.set_page_config(
    page_title="BOD Dashboard Monitoring Rapat",
    page_icon="📊",
    layout="wide"
)

st.title("📋 Dashboard Tindak Lanjut Arahan & Rapat BOD")
st.markdown("---")

# 2. Fungsi Load Data dengan Pembersihan Sesuai File CSV Anda
@st.cache_data
def load_clean_data():
    # Menggunakan sep=";" karena file Anda dipisahkan oleh titik koma
    df = pd.read_csv("data_rapat.csv", sep=";")
    
    # Menghapus spasi gaib/tersembunyi di nama kolom (Mencegah KeyError)
    df.columns = df.columns.str.strip()
    
    # Membuang baris kosong yang tidak ada isi "Tindak Lanjut/Arahan"
    df = df.dropna(subset=['Tindak Lanjut/Arahan'])
    
    # Membersihkan spasi di dalam isi baris data teks
    for col in ['Status', 'PIC', 'Rapat', 'Kategori']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            
    # Mengisi kolom kategori yang kosong (NaN) agar tetap bisa divisualisasikan
    if 'Kategori' in df.columns:
        df['Kategori'] = df['Kategori'].replace({'nan': 'Belum Dikategorikan', '': 'Belum Dikategorikan'})
        df['Kategori'] = df['Kategori'].fillna('Belum Dikategorikan')
        
    # Mengonversi format tanggal secara otomatis
    if 'Tanggal Rapat' in df.columns:
        df['Tanggal Rapat'] = pd.to_datetime(df['Tanggal Rapat'], errors='coerce')
    if 'Due Date' in df.columns:
        df['Due Date'] = pd.to_datetime(df['Due Date'], errors='coerce')
        
    return df

try:
    df_rapat = load_clean_data()
    
    # 3. Sidebar Filter Komponen
    st.sidebar.header("⚙️ Filter Data Dashboard")
    
    # Filter Jenis Rapat (BOC / BOD / Rapat Eksternal)
    list_rapat = df_rapat['Rapat'].unique().tolist()
    filter_rapat = st.sidebar.multiselect("Pilih Jenis Rapat:", options=list_rapat, default=["BOD"] if "BOD" in list_rapat else list_rapat[:1])
    
    # Filter PIC / Divisi
    list_pic = sorted(df_rapat['PIC'].unique().tolist())
    filter_pic = st.sidebar.multiselect("Pilih PIC / Divisi:", options=list_pic)
    
    # Filter Status (Open / Closed)
    list_status = df_rapat['Status'].unique().tolist()
    filter_status = st.sidebar.multiselect("Pilih Status Komitmen:", options=list_status)

    # Mengaplikasikan Filter secara bertahap
    df_filtered = df_rapat.copy()
    if filter_rapat:
        df_filtered = df_filtered[df_filtered['Rapat'].isin(filter_rapat)]
    if filter_pic:
        df_filtered = df_filtered[df_filtered['PIC'].isin(filter_pic)]
    if filter_status:
        df_filtered = df_filtered[df_filtered['Status'].isin(filter_status)]

    # 4. Pembuatan KPI / Ringkasan Metrik Atas
    total_komitmen = len(df_filtered)
    closed_issues = len(df_filtered[df_filtered['Status'].str.lower() == 'closed'])
    open_issues = total_komitmen - closed_issues
    persentase_selesai = (closed_issues / total_komitmen) * 100 if total_komitmen > 0 else 0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Arahan/Komitmen", f"{total_komitmen} Item")
    m2.metric("Status OPEN", f"{open_issues} Item", delta_color="inverse")
    m3.metric("Status CLOSED", f"{closed_issues} Item")
    m4.metric("Penyelesaian (%)", f"{persentase_selesai:.1f}%")
    
    st.markdown("---")

    # 5. Visualisasi Grafik Interaktif (Plotly)
    g1, g2 = st.columns([3, 2]) # Pembagian proporsi lebar kolom grafik
    
    with g1:
        st.subheader("📊 Distribusi Status Komitmen Berdasarkan PIC")
        fig_pic = px.histogram(
            df_filtered, 
            x="PIC", 
            color="Status", 
            barmode="group",
            color_discrete_map={'Closed': '#2ecc71', 'Open': '#e74c3c'},
            labels={'PIC': 'Divisi / Penanggung Jawab', 'count': 'Jumlah Komitmen'}
        )
        fig_pic.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_pic, use_container_width=True)
            
    with g2:
        st.subheader("📈 Proporsi Komitmen per Kategori")
        fig_kat = px.pie(
            df_filtered, 
            names="Kategori", 
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig_kat, use_container_width=True)

    st.markdown("---")

    # 6. Tabel Detail Monitoring Kertas Kerja
    st.subheader("📋 Detail Kertas Kerja Monitoring")
    
    # Memilih kolom penting saja untuk ditampilkan di tabel utama agar rapi
    kolom_tampil = ['Kategori', 'Tindak Lanjut/Arahan', 'Rekomendasi', 'PIC', 'Status', 'Rapat', 'Tanggal Rapat', 'Due Date']
    kolom_ada = [c for c in kolom_tampil if c in df_filtered.columns]
    
    st.dataframe(
        df_filtered[kolom_ada],
        column_config={
            "Tanggal Rapat": st.column_config.DateColumn("Tanggal Rapat", format="DD-MM-YYYY"),
            "Due Date": st.column_config.DateColumn("Batas Waktu", format="DD-MM-YYYY"),
        },
        use_container_width=True,
        hide_index=True
    )

except FileNotFoundError:
    st.error("File 'data_rapat.csv' tidak ditemukan di folder root. Pastikan file data Anda berada berdampingan dengan file app.py ini.")
except Exception as e:
    st.error(f"Terjadi kesalahan sistem saat membaca data: {e}")
