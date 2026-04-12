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

st.sidebar.header("Date Filter")

min_date = orders["order_purchase_timestamp"].dt.date.min()
max_date = orders["order_purchase_timestamp"].dt.date.max()

start_date = st.sidebar.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date)
end_date   = st.sidebar.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date)

if start_date > end_date:
    st.sidebar.error("Start date must be before end date.")
    st.stop()

st.sidebar.divider()
page = st.sidebar.radio("Navigation", ["Dashboard", "Insight"])

mask = (
    (orders["order_purchase_timestamp"].dt.date >= start_date) &
    (orders["order_purchase_timestamp"].dt.date <= end_date)
)
df_orders = orders[mask].copy()
df_orders["order_hour"]  = df_orders["order_purchase_timestamp"].dt.hour
df_orders["order_day"] = df_orders["order_purchase_timestamp"].dt.day_name()

urutan_hari = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
label_hari  = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
df_orders["order_day"] = pd.Categorical(df_orders["order_day"], categories=urutan_hari, ordered=True)

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
    col1.metric("Total Orders",           f"{len(df_orders):,}")
    col2.metric("Total Transactions",     f"R$ {df_pay['payment_value'].sum():,.0f}")
    col3.metric("Average Transaction",    f"R$ {df_pay['payment_value'].mean():,.1f}")
    col4.metric("Payment Methods",        df_pay["payment_type"].nunique())

    st.divider()
    st.subheader("Peak Order Time")
    c1, c2 = st.columns([1, 1.6])

    with c1:
        volume_per_hour = df_orders.groupby("order_hour")["order_id"].count()
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.lineplot(x=volume_per_hour.index, y=volume_per_hour.values,
                     marker="o", color="#2b8cbe", linewidth=2.5, ax=ax)
        ax.set_title("Order Volume by Hour", fontweight="bold")
        ax.set_xlabel("Hour")
        ax.set_ylabel("Total Orders")
        ax.set_xticks(range(0, 24))
        ax.grid(True, linestyle="--", alpha=0.5)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with c2:
        heatmap_data = (
            df_orders.groupby(["order_day", "order_hour"])["order_id"]
            .count()
            .unstack(fill_value=0)
        )
        heatmap_data.index = label_hari[:len(heatmap_data)]
        fig, ax = plt.subplots(figsize=(10, 4))
        sns.heatmap(heatmap_data, cmap="YlGnBu", annot=False, linewidths=0.3, ax=ax)
        ax.set_title("Heatmap Day vs Hour", fontweight="bold")
        ax.set_xlabel("Hour")
        ax.set_ylabel("Day")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    st.divider()
    st.subheader("Payment Method Analysis")
    c3, c4 = st.columns(2)

    with c3:
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.barplot(data=df_pay, x="payment_type", y="payment_value",
                    estimator="mean", errorbar=None, palette="viridis", ax=ax)
        ax.set_title("Average Transaction Value per Method", fontweight="bold")
        ax.set_xlabel("Payment Method")
        ax.set_ylabel("Average (R$)")
        ax.grid(axis="y", linestyle="--", alpha=0.5)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with c4:
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.boxplot(data=df_pay, x="payment_type", y="payment_value",
                    palette="Set2", ax=ax)
        ax.set_yscale("log")
        ax.set_title("Transaction Value Distribution (Log Scale)", fontweight="bold")
        ax.set_xlabel("Payment Method")
        ax.set_ylabel("Transaction Value (Log Scale)")
        ax.grid(axis="y", linestyle="--", alpha=0.5)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

elif page == "Insight":
    st.title("Analysis Insight")
    st.caption(f"Data: {start_date.strftime('%d %b %Y')} - {end_date.strftime('%d %b %Y')}")

    st.subheader("Peak Order Volume Time")
    st.markdown("""
- Order volume starts increasing significantly from 07:00, reaching its first peak at 10:00-11:00 (6,500 orders).
- After a slight dip at 12:00 (likely due to lunch break), volume remains consistently high between 13:00-16:00.
- A second, lower peak occurs at 20:00-21:00, indicating nighttime shopping activity.
- The lowest volume is recorded at 04:00-05:00 in the early morning.
- From the heatmap, weekdays (Monday-Thursday) show the highest intensity between 10:00-18:00, while Friday remains active only until 17:00, suggesting customers begin disengaging ahead of the weekend.
- Saturday shows more evenly distributed but lower activity compared to weekdays.
- Interestingly, Sunday activity shifts toward the evening (18:00-22:00), diverging from the typical weekday pattern.
""")
    st.success("Peak order time occurs between 10:00-16:00 on weekdays (Monday-Thursday), with the highest peak at 10:00-11:00 reaching 6,500 orders. A smaller secondary peak appears at 20:00-21:00, reflecting nighttime shopping behavior. Sunday shows a distinct pattern, with activity shifting to the evening (18:00-22:00) rather than daytime as seen on weekdays. Overall, 10:00-16:00 on weekdays is the optimal window for promotions or operations requiring high traffic.")

    st.divider()

    st.subheader("Transaction Value Distribution per Payment Method")
    st.markdown("""
- Credit card has the highest average transaction value (R$163), followed by boleto (R$145) and debit card (R$142) which are relatively similar, while voucher is significantly lower (R$65) — expected, as vouchers are typically used as partial discounts rather than full payment methods.
- From the log-scale boxplot, the median for credit card, boleto, and debit card sits around R$100, while voucher falls around R$40-50.
- All three main payment methods show high-value transaction outliers reaching up to R$10,000, indicating the presence of high-value customer segments across all methods.
- Boleto has a notably long lower whisker (approaching R$0.01), suggesting the existence of near-zero boleto transactions that may warrant investigation as anomalous data.
- Voucher shows the narrowest spread and consistently lowest values, reinforcing its role as a supplementary payment method rather than a primary one.
""")
    st.success("Credit card is the payment method with the highest average transaction value, followed by boleto and debit card which are relatively equal in the range of R$142-145. Voucher has the lowest average value as it is generally used as a supplementary method rather than a full payment. All primary payment methods show the presence of high-value customer segments with transactions reaching up to R$10,000. Overall, credit card is not only the most popular payment method but also generates the highest transaction value, making it the most strategically significant method to optimize from a business perspective.")