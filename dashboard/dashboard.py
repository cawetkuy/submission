import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
import datetime as dt
sns.set(style='dark')
all_df = pd.read_csv("https://drive.google.com/uc?id=1j0464VTUoleh5r0SqeHIe0FQGzKsI_DQ")

datetime_columns = ["order_approved_at"]
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

def create_monthly_oders_df(df):
    monthly_orders_df  = df.resample(rule='M', on='order_approved_at').agg({
    "order_id": "size",
    "price": "sum"
    })

    monthly_orders_df .index = monthly_orders_df .index.strftime('%B')
    monthly_orders_df = monthly_orders_df .reset_index()
    monthly_orders_df.rename(columns={
        "order_id": "order_count",
        "price": "revenue"
    }, inplace=True)

    monthly_orders_df = monthly_orders_df.sort_values('order_count').drop_duplicates('order_approved_at', keep='last')
    
    month_sort = {
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12
    }
    monthly_orders_df["int"] = monthly_orders_df["order_approved_at"].map(month_sort)
    monthly_orders_df = monthly_orders_df.sort_values("int")
    monthly_orders_df = monthly_orders_df.drop("int", axis=1)
    return monthly_orders_df

def create_sort_order_items_df(df):
    sort_order_items_df = df.groupby("product_category_name_english")['product_id'].count().sort_values(ascending=False).reset_index()
    return sort_order_items_df

def create_rating_counts_df(df):
    rating_counts = df['review_score'].value_counts().sort_values(ascending=False)
    rating_indices = rating_counts.index
    rating_values = rating_counts.values
    max_score = rating_counts.idxmax()
    
    df_customer=df['review_score']
    return (rating_counts,rating_indices,rating_values,max_score,df_customer)

def create_rfm_df(df):
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])

    # Menghitung tanggal terbaru dan terlama dalam DataFrame
    latest_date = df['order_purchase_timestamp'].max()
    earliest_date = df['order_purchase_timestamp'].min()

    # Menetapkan tanggal 
    now = dt.datetime(2018, 11, 3)

    # Menghitung Recency, Frequency, dan Monetary
    recency = (now - df.groupby('customer_id')['order_purchase_timestamp'].max()).dt.days
    frequency = df.groupby('customer_id')['order_purchase_timestamp'].count()
    monetary = df.groupby('customer_id')['price'].sum()

    # Membuat DataFrame baru dengan metrik yang dihitung
    rfm_df = pd.DataFrame({
        'customer_id': recency.index,
        'Recency': recency.values,
        'Frequency': frequency.values,
        'Monetary': monetary.values
    })
    # Mengurutkan DataFrame berdasarkan Recency secara menaik
    rfm_sorted = rfm_df.sort_values(by='Recency', ascending=True)

    return rfm_sorted

monthly_orders_df = create_monthly_oders_df(all_df) 
sort_order_items_df = create_sort_order_items_df(all_df)
rating_counts,rating_indices,rating_values,max_score,df_customer = create_rating_counts_df(all_df)
rfm_df = create_rfm_df(all_df)

#------------------------------------SIDE BAR------------------------------------
# Tampilan Input Nama
st.sidebar.image("https://github.com/cawetkuy/E-commerce-Public-Dataset/raw/main/icon_shop.png", width=100)
st.sidebar.title("Welcome to the Company Website :sparkles:")

nama_pengguna = st.sidebar.text_input("Enter your nickname")
tombol_masuk = st.sidebar.button("Home")
st.header(f"Company Sales Website, Look at the Sidebar ! 👀")
if tombol_masuk:
    if nama_pengguna:
        st.header(f"Hiii!, {nama_pengguna}! Welcome to the home page of the company website :sparkles:")
        st.write("On this Streamlit website, I present the final results of the Dicoding Data Analytics Project that I have successfully completed. Through this platform, you can explore a variety of interesting data visualizations and answers to the questions I have compiled before.")
        st.write("To open the discussion, we first present key information about the company's performance. You can easily see the total orders placed as well as the amount of revenue generated from the sale of our company's products. This information provides a snapshot of how successful the company has been in managing its business.")
        st.write("Directly engaging users by providing informative diagram visualizations, we ensured that each element was easily accessible. In addition, each pre-formulated question has been answered through purposeful visualizations, allowing users to explore the key findings of the data analysis that has been conducted.")
        st.write("Not only do we present the data in the form of attractive graphs and diagrams, but we also ensure that the results of the analysis are presented in a clear and structured manner, helping users to better understand the overall picture of the company's performance. The overall presentation is geared towards providing an informative and intuitive experience to the users of this website.")
        # Tampilan Monthly Orders
        st.subheader(':bulb: Monthly Orders :bulb:')
        col1, col2 = st.columns(2)

        with col1:
            total_orders = monthly_orders_df.order_count.sum()
            st.metric("Total orders", value=total_orders)

        with col2:
            total_price = format_currency(monthly_orders_df.revenue.sum(), "EUR", locale='es_CO') 
            st.metric("Total Revenue", value=total_price)
            # Tampilkan konten halaman home di sini

        st.subheader("Monthly Orders")
        fig, ax = plt.subplots(figsize=(16, 8))
        ax.plot(
            monthly_orders_df["order_approved_at"], 
            monthly_orders_df["order_count"], 
            marker='o', 
            linewidth=2, 
            color="#72BCD4")
        ax.set_title("Number of Orders per Month (20218)", loc="center", fontsize=20)
        ax.tick_params(axis='y', labelsize=20)
        ax.tick_params(axis='x', labelsize=15)
        st.pyplot(fig)

    else:
        st.warning("Please enter your name before starting")

# Tampilan Sidebar Checkbox
st.sidebar.subheader("Choose a question below")
# Pertanyaan 1
if st.sidebar.checkbox("Question 1"):
    st.subheader("Question 1 💬")
    st.write("What was the company's sales level in 2018?")
    st.dataframe(monthly_orders_df, width=1000)
    st.subheader("📊Best & Worst Performing Product📊")
    st.write("")
    fig, ax = plt.subplots(figsize=(16, 8))
    ax.plot(
        monthly_orders_df["order_approved_at"], 
        monthly_orders_df["order_count"], 
        marker='o', 
        linewidth=2, 
        color="#72BCD4")
    ax.set_title("Number of Orders per Month (2018)", loc="center", fontsize=20)
    ax.tick_params(axis='y', labelsize=20)
    ax.tick_params(axis='x', labelsize=15)
    st.pyplot(fig)

# Pertanyaan 2
if st.sidebar.checkbox("Question 2"):
    st.subheader("Question 2 💬")
    st.write("What products are most Interested by customers?")
    st.dataframe(sort_order_items_df, width=1000)
    st.write("📊Product Interest Rate📊")
    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(16, 8))

    colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

    sns.barplot(x="product_id", y="product_category_name_english", data=sort_order_items_df.head(5), palette=colors, ax=ax[0])
    # ax[0] merupakan object untuk kanvas pertama (bagian kiri)
    ax[0].set_ylabel(None)
    ax[0].set_xlabel(None)
    ax[0].set_title("The most popular product", loc="center", fontsize=15)
    ax[0].tick_params(axis ='y', labelsize=12)

    sns.barplot(x="product_id", y="product_category_name_english", data=sort_order_items_df.sort_values(by="product_id", ascending=True).head(5), palette=colors, ax=ax[1])
    # ax[1] merupakan object untuk kanvas kedua (bagian kanan)
    ax[1].set_ylabel(None)
    ax[1].set_xlabel(None)
    ax[1].invert_xaxis()
    ax[1].yaxis.set_label_position("right")
    ax[1].yaxis.tick_right()
    ax[1].set_title("Worst Performing Product", loc="center", fontsize=20)
    ax[1].tick_params(axis='y', labelsize=15)
    st.pyplot(fig)

# Pertanyaan 3
if st.sidebar.checkbox("Question 3"):
    st.subheader("Question 3 💬")
    st.write("What is the level of rating given by customers from best to worst?")
    st.dataframe(rating_counts)
    st.subheader("📊Rating given by the customer📊")
    plt.figure(figsize=(10, 5))
    sns.barplot(
        x=rating_indices,
        y=rating_values,
        order=rating_indices,
         palette=["#72BCD4" if score == max_score else "#D3D3D3" for score in rating_indices]
    )
    plt.title("Rating given by the customer", fontsize=15)
    plt.xlabel("Rating")
    plt.ylabel("Customers")
    plt.xticks(fontsize=12)
    st.pyplot(plt)

# RFM
if st.sidebar.checkbox("RFM SCORE"):
    st.subheader("Recency, Frequency, Monetary 💬")
    st.write("1. Recency : a parameter used to see when a customer last made a transaction.\n 2. Frequency : this parameter is used to identify how often a customer makes a transaction. \n 3. Monetary : this last parameter is used to identify how much revenue comes from the customer.")
    st.dataframe(rfm_df, width=1000)
    col1, col2, col3 = st.columns(3)

    with col1:
        avg_recency = round(rfm_df.Recency.mean(), 1)
        st.metric("📊Average Recency (days)📊", value=avg_recency)

    with col2:
        avg_frequency = round(rfm_df.Frequency.mean(), 2)
        st.metric("📊Average Frequency📊", value=avg_frequency)

    with col3:
        avg_monetary = format_currency(rfm_df.Monetary.mean(), "AUD", locale='es_CO')
        st.metric("📊Average Monetary📊", value=avg_monetary)

    fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(30, 6))

    colors = ["#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4"]

    sns.barplot(y="Recency", x="customer_id", data=rfm_df.sort_values(by="Recency", ascending=True).head(5), palette=colors, ax=ax[0])
    ax[0].set_ylabel(None)
    ax[0].set_xlabel("customer_id")
    ax[0].set_title("By Recency (days)", loc="center", fontsize=18)
    ax[0].tick_params(axis ='x', labelsize=15)
    ax[0].set_xticklabels(ax[0].get_xticklabels(), rotation=90)
    ax[0].set_xticks([])

    sns.barplot(y="Frequency", x="customer_id", data=rfm_df.sort_values(by="Frequency", ascending=False).head(5), palette=colors, ax=ax[1])
    ax[1].set_ylabel(None)
    ax[1].set_xlabel('customer_id')
    ax[1].set_title("By Frequency", loc="center", fontsize=18)
    ax[1].tick_params(axis='x', labelsize=15)
    ax[1].set_xticklabels(ax[0].get_xticklabels(), rotation=90)
    ax[1].set_xticks([])

    sns.barplot(y="Monetary", x="customer_id", data=rfm_df.sort_values(by="Monetary", ascending=False).head(5), palette=colors, ax=ax[2])
    ax[2].set_ylabel(None)
    ax[2].set_xlabel('customer_id')
    ax[2].set_title("By Monetary", loc="center", fontsize=18)
    ax[2].tick_params(axis='x', labelsize=15)
    ax[2].set_xticklabels(ax[0].get_xticklabels(), rotation=90)
    ax[2].set_xticks([])

    plt.suptitle("Best Customer Based on RFM Parameters (customer_id)", fontsize=20)
    st.pyplot(fig)