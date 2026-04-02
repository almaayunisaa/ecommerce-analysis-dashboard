import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Olist Dashboard", layout="wide")
sns.set_theme(style="whitegrid")

DATASET_PATH = "dataset"

@st.cache_data
def load_data():
    orders   = pd.read_csv(f"{DATASET_PATH}/olist_orders_dataset.csv")
    payments = pd.read_csv(f"{DATASET_PATH}/olist_order_payments_dataset.csv")
    orders["order_purchase_timestamp"] = pd.to_datetime(orders["order_purchase_timestamp"])
    return orders, payments

orders, payments = load_data()

st.sidebar.header("Filter Tanggal")

min_date = orders["order_purchase_timestamp"].dt.date.min()
max_date = orders["order_purchase_timestamp"].dt.date.max()

start_date = st.sidebar.date_input("Tanggal Mulai", value=min_date, min_value=min_date, max_value=max_date)
end_date   = st.sidebar.date_input("Tanggal Akhir", value=max_date, min_value=min_date, max_value=max_date)

if start_date > end_date:
    st.sidebar.error("Tanggal mulai harus sebelum tanggal akhir.")
    st.stop()

st.sidebar.divider()
page = st.sidebar.radio("Navigasi", ["Dashboard", "Insight"])

mask = (
    (orders["order_purchase_timestamp"].dt.date >= start_date) &
    (orders["order_purchase_timestamp"].dt.date <= end_date)
)
df_orders = orders[mask].copy()
df_orders["jam_pesanan"]  = df_orders["order_purchase_timestamp"].dt.hour
df_orders["hari_pesanan"] = df_orders["order_purchase_timestamp"].dt.day_name()

urutan_hari = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
label_hari  = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
df_orders["hari_pesanan"] = pd.Categorical(df_orders["hari_pesanan"], categories=urutan_hari, ordered=True)

df_merged = pd.merge(payments, orders[["order_id", "order_purchase_timestamp"]], on="order_id", how="inner")
df_merged["order_purchase_timestamp"] = pd.to_datetime(df_merged["order_purchase_timestamp"])
mask_pay = (
    (df_merged["order_purchase_timestamp"].dt.date >= start_date) &
    (df_merged["order_purchase_timestamp"].dt.date <= end_date)
)
df_pay = df_merged[mask_pay & (df_merged["payment_type"] != "not_defined")].copy()

if page == "Dashboard":
    st.title("Olist E-Commerce Dashboard")
    st.caption(f"Data: {start_date.strftime('%d %b %Y')} - {end_date.strftime('%d %b %Y')}")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Pesanan",       f"{len(df_orders):,}")
    col2.metric("Total Transaksi",     f"R$ {df_pay['payment_value'].sum():,.0f}")
    col3.metric("Rata-rata Transaksi", f"R$ {df_pay['payment_value'].mean():,.1f}")
    col4.metric("Metode Pembayaran",   df_pay["payment_type"].nunique())

    st.divider()
    st.subheader("Waktu Puncak Pesanan")
    c1, c2 = st.columns([1, 1.6])

    with c1:
        volume_per_jam = df_orders.groupby("jam_pesanan")["order_id"].count()
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.lineplot(x=volume_per_jam.index, y=volume_per_jam.values,
                     marker="o", color="#2b8cbe", linewidth=2.5, ax=ax)
        ax.set_title("Volume Pesanan per Jam", fontweight="bold")
        ax.set_xlabel("Jam")
        ax.set_ylabel("Total Pesanan")
        ax.set_xticks(range(0, 24))
        ax.grid(True, linestyle="--", alpha=0.5)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with c2:
        heatmap_data = (
            df_orders.groupby(["hari_pesanan", "jam_pesanan"])["order_id"]
            .count()
            .unstack(fill_value=0)
        )
        heatmap_data.index = label_hari[:len(heatmap_data)]
        fig, ax = plt.subplots(figsize=(10, 4))
        sns.heatmap(heatmap_data, cmap="YlGnBu", annot=False, linewidths=0.3, ax=ax)
        ax.set_title("Heatmap Hari vs Jam", fontweight="bold")
        ax.set_xlabel("Jam")
        ax.set_ylabel("Hari")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    st.divider()
    st.subheader("Analisis Metode Pembayaran")
    c3, c4 = st.columns(2)

    with c3:
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.barplot(data=df_pay, x="payment_type", y="payment_value",
                    estimator="mean", errorbar=None, palette="viridis", ax=ax)
        ax.set_title("Rata-rata Nilai Transaksi per Metode", fontweight="bold")
        ax.set_xlabel("Metode Pembayaran")
        ax.set_ylabel("Rata-rata (R$)")
        ax.grid(axis="y", linestyle="--", alpha=0.5)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with c4:
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.boxplot(data=df_pay, x="payment_type", y="payment_value",
                    palette="Set2", ax=ax)
        ax.set_yscale("log")
        ax.set_title("Distribusi Nilai Transaksi (Log Scale)", fontweight="bold")
        ax.set_xlabel("Metode Pembayaran")
        ax.set_ylabel("Nilai Transaksi (Log Scale)")
        ax.grid(axis="y", linestyle="--", alpha=0.5)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

elif page == "Insight":
    st.title("Insight Analisis")
    st.caption(f"Data: {start_date.strftime('%d %b %Y')} - {end_date.strftime('%d %b %Y')}")

    st.subheader("Waktu Puncak Volume Pesanan")
    st.markdown("""
- Volume pesanan mulai meningkat signifikan sejak jam 07.00 dan mencapai puncak pertama pada jam 10.00-11.00 (6.500 pesanan)
- Setelah sedikit menurun di jam 12.00 (kemungkinan jam makan siang), volume kembali stabil tinggi di rentang jam 13.00-16.00
- Terjadi puncak kedua yang lebih rendah di jam 20.00-21.00, mengindikasikan aktivitas belanja malam hari
- Volume terendah terjadi di jam 04.00-05.00 dini hari
- Dari heatmap, hari kerja (Senin-Kamis) memiliki intensitas tertinggi di jam 10.00-18.00, Jumat aktif hingga jam 17.00 saja, kemungkinan pelanggan mulai tidak aktif menjelang akhir pekan
- Sabtu aktivitas lebih merata dan lebih rendah dibanding hari kerja
- Minggu menariknya aktivitasnya justru bergeser ke malam hari (18.00-22.00), berbeda dari pola hari kerja
""")
    st.success("Waktu puncak pesanan terjadi pada jam 10.00-16.00 di hari kerja (Senin-Kamis), dengan puncak tertinggi di jam 10.00-11.00 mencapai 6.500 pesanan. Terdapat puncak sekunder yang lebih kecil di jam 20.00-21.00 yang mencerminkan perilaku belanja malam. Hari Minggu menunjukkan pola berbeda, aktivitas bergeser ke malam hari (18.00-22.00) dibanding siang hari seperti hari kerja. Secara keseluruhan, jam 10.00-16.00 pada hari kerja adalah waktu terbaik untuk promosi atau operasional yang membutuhkan traffic tinggi.")

    st.divider()

    st.subheader("Distribusi Nilai Transaksi per Metode Pembayaran")
    st.markdown("""
- Credit card memiliki rata-rata transaksi tertinggi (R$163), diikuti boleto (R$145) dan debit card (R$142) yang relatif setara, sementara voucher jauh di bawah (R$65), wajar karena voucher biasanya digunakan sebagai potongan parsial, bukan pembayaran penuh
- Dari boxplot log scale, median credit card, boleto, dan debit card berada di kisaran R$100, sedangkan voucher di kisaran R$40-50
- Ketiga metode utama memiliki outlier transaksi besar hingga R$10.000, menunjukkan ada segmen pelanggan high-value di semua metode
- Boleto memiliki whisker bawah yang sangat panjang (mendekati R$0,01), mengindikasikan ada transaksi boleto bernilai nyaris nol yang perlu dicurigai sebagai data anomali
- Voucher memiliki sebaran paling sempit dan nilai paling kecil secara konsisten, memperkuat bahwa voucher berfungsi sebagai pelengkap pembayaran, bukan metode utama
""")
    st.success("Credit card menjadi metode pembayaran dengan nilai transaksi rata-rata tertinggi, diikuti boleto dan debit card yang setara di kisaran R$142-145. Voucher memiliki nilai rata-rata paling rendah karena umumnya digunakan sebagai pelengkap, bukan pembayaran penuh. Semua metode utama menunjukkan adanya segmen pelanggan high-value dengan transaksi hingga R$10.000. Secara keseluruhan, credit card bukan hanya metode pembayaran paling populer, tetapi juga menghasilkan nilai transaksi tertinggi, menjadikannya metode yang paling strategis untuk dioptimalkan dari sisi bisnis.")