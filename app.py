import streamlit as st
import pandas as pd
import duckdb
import plotly.express as px
from sklearn.cluster import KMeans
from statsmodels.tsa.seasonal import seasonal_decompose
from mlxtend.frequent_patterns import apriori, association_rules
from datetime import datetime

st.set_page_config(
    page_title="Advanced E-commerce Dashboard",
    page_icon="🛒",
    layout="wide"
)

def format_indian_currency(num):
    if not pd.isna(num):
        if num >= 1_00_00_000:
            return f"₹ {num / 1_00_00_000:.2f} Cr"
        elif num >= 1_00_000:
            return f"₹ {num / 1_00_000:.2f} L"
        else:
            return f"₹ {num:,.2f}"
    return "₹ 0.00"

@st.cache_data
def load_data(path):
    df = pd.read_csv(path, encoding='latin1')
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    df.dropna(subset=['Customer ID'], inplace=True)
    df['Customer ID'] = df['Customer ID'].astype(int)
    df = df[~df['Invoice'].str.startswith('C', na=False)]
    df = df[df['Quantity'] > 0]
    df['TotalPrice'] = df['Quantity'] * df['Price']
    return df

df = load_data('online_retail_II.zip')

st.title("🛒 Advanced E-commerce Analytics Dashboard")
st.markdown("Use the filters in the sidebar to analyze sales data, segment customers, and discover product associations.")

st.sidebar.header("Dashboard Filters")
st.sidebar.info("Use these filters to drill down into the data. The entire dashboard will update based on your selections.")

country_list = ['All'] + sorted(df['Country'].unique().tolist())
selected_country = st.sidebar.selectbox("Select a Country", country_list)

min_date = df['InvoiceDate'].min().date()
max_date = df['InvoiceDate'].max().date()
selected_date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

top_n = st.sidebar.slider("Select Top N for Charts", min_value=5, max_value=20, value=10)

df_filtered = df.copy()
if selected_country != 'All':
    df_filtered = df_filtered[df_filtered['Country'] == selected_country]

start_date = datetime.combine(selected_date_range[0], datetime.min.time())
end_date = datetime.combine(selected_date_range[1], datetime.max.time())
df_filtered = df_filtered[(df_filtered['InvoiceDate'] >= start_date) & (df_filtered['InvoiceDate'] <= end_date)]

con = duckdb.connect(database=':memory:', read_only=False)
con.register('filtered_sales_df', df_filtered)

st.header("📊 High-Level Metrics")
total_revenue = df_filtered['TotalPrice'].sum()
total_sales = len(df_filtered)
unique_customers = df_filtered['Customer ID'].nunique()

col1, col2, col3 = st.columns(3)
col1.metric("Total Revenue", format_indian_currency(total_revenue))
col2.metric("Total Sales", f"{total_sales:,}")
col3.metric("Unique Customers", f"{unique_customers:,}")

st.markdown("---")

st.header("📈 Core Sales Analysis")

query_sales_over_time = """
SELECT
    strftime('%Y-%m', InvoiceDate) AS month,
    SUM(TotalPrice) AS monthly_revenue
FROM filtered_sales_df
GROUP BY month
ORDER BY month;
"""
sales_over_time = con.execute(query_sales_over_time).fetchdf()
fig_sales = px.line(sales_over_time, x='month', y='monthly_revenue', title='Monthly Sales Revenue', markers=True)
fig_sales.update_layout(yaxis_tickprefix='₹')
fig_sales.update_traces(hovertemplate='Month: %{x}<br>Revenue: ₹%{y:,.2f}')
st.plotly_chart(fig_sales, use_container_width=True)

col1, col2 = st.columns(2)
with col1:
    st.subheader(f"Top {top_n} Selling Products")
    query_top_products = f"""
    SELECT Description, SUM(Quantity) AS total_quantity_sold
    FROM filtered_sales_df WHERE Description IS NOT NULL
    GROUP BY Description ORDER BY total_quantity_sold DESC LIMIT {top_n};
    """
    top_products = con.execute(query_top_products).fetchdf()
    st.dataframe(top_products)

with col2:
    st.subheader(f"Top {top_n} Customers by Revenue")
    query_top_customers = f"""
    SELECT "Customer ID", SUM(TotalPrice) AS total_spent
    FROM filtered_sales_df GROUP BY "Customer ID" ORDER BY total_spent DESC LIMIT {top_n};
    """
    top_customers = con.execute(query_top_customers).fetchdf()
    st.dataframe(top_customers.style.format({'total_spent': '₹{:,.2f}'}))

st.markdown("---")

st.header("👥 Customer Segmentation (RFM)")
st.info("""
This section segments customers based on their purchasing behavior using the RFM model:
- **Recency:** How recently did they purchase? (Fewer days is better)
- **Frequency:** How often do they purchase? (Higher is better)
- **Monetary:** How much do they spend? (Higher is better)
""")

max_date = df_filtered['InvoiceDate'].max()
rfm_df = df_filtered.groupby('Customer ID').agg(
    Recency=('InvoiceDate', lambda date: (max_date - date.max()).days),
    Frequency=('Invoice', 'nunique'),
    Monetary=('TotalPrice', 'sum')).reset_index()

if len(rfm_df) > 3:
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    rfm_df['Cluster'] = kmeans.fit_predict(rfm_df[['Recency', 'Frequency', 'Monetary']])
    cluster_map = {0: '🚨 At-Risk', 1: '🏆 High-Value', 2: '🌱 New/Promising'}
    rfm_df['Segment'] = rfm_df['Cluster'].map(cluster_map)

    fig_rfm = px.scatter(rfm_df, x='Recency', y='Frequency', color='Segment', size='Monetary', title='Customer Segments',
                         hover_data={'Recency': True, 'Frequency': True, 'Monetary': ':.2f'})
    fig_rfm.update_traces(hovertemplate='<b>Recency</b>: %{x} days<br><b>Frequency</b>: %{y} orders<br><b>Monetary Value</b>: ₹%{marker.size:,.2f}')
    st.plotly_chart(fig_rfm, use_container_width=True)
else:
    st.warning("Not enough data with the current filters to perform customer segmentation.")

st.markdown("---")

st.header("🔬 Advanced Analytics")

with st.expander("🕰️ See Time Series Decomposition Analysis"):
    st.markdown("""
    This analysis breaks down the daily sales data into three components:
    - **Trend:** The underlying long-term direction of sales.
    - **Seasonality:** Repeating weekly patterns in sales.
    - **Residuals:** The random, irregular noise in the data.
    """)
    daily_sales = df_filtered.set_index('InvoiceDate').resample('D')['TotalPrice'].sum()
    if not daily_sales.empty and len(daily_sales) > 14:
        decomposition = seasonal_decompose(daily_sales, model='additive', period=7)
        st.subheader("Trend Component")
        st.line_chart(decomposition.trend)
        st.subheader("Seasonality Component")
        st.line_chart(decomposition.seasonal)
        st.subheader("Residual (Noise) Component")
        st.line_chart(decomposition.resid)
    else:
        st.warning("Not enough daily data in the selected range to perform time series decomposition.")

with st.expander("💡 See Market Basket Analysis (Product Associations)"):
    st.markdown("""
    This analysis finds which products are frequently bought together. This can be used for store promotions or website recommendations.
    - **Support:** How frequently the items appear together in transactions.
    - **Confidence:** The likelihood that a customer will buy Item B if they bought Item A.
    - **Lift:** How much more likely a customer is to buy Item B if they bought Item A (a lift > 1 is a good indicator).
    """)

    with st.spinner("Calculating product associations... This may take a moment."):
        if not df_filtered.empty and 'Description' in df_filtered.columns:
            basket_df = df_filtered.groupby(['Invoice', 'Description'])['Quantity'].sum().unstack().reset_index().fillna(0).set_index('Invoice')
            def encode_units(x): return 1 if x >= 1 else 0
            basket_encoded = basket_df.applymap(encode_units)
            if 'POSTAGE' in basket_encoded.columns: basket_encoded = basket_encoded.drop('POSTAGE', axis=1)

            if not basket_encoded.empty:
                frequent_itemsets = apriori(basket_encoded, min_support=0.01, use_colnames=True)
                if not frequent_itemsets.empty:
                    rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1)
                    
                    st.subheader("Top Product Association Rules")
                    rules["antecedents"] = rules["antecedents"].apply(lambda x: ', '.join(list(x)))
                    rules["consequents"] = rules["consequents"].apply(lambda x: ', '.join(list(x)))
                    display_rules = rules.sort_values('lift', ascending=False).head(10)
                    st.dataframe(
                        display_rules[['antecedents', 'consequents', 'support', 'confidence', 'lift']].rename(columns={
                            'antecedents': 'If You Buy...',
                            'consequents': 'You Might Also Buy...'
                        }).style.format({'support': '{:.2%}', 'confidence': '{:.2%}', 'lift': '{:.2f}'})
                    )
                else:
                    st.warning("No significant product associations found. Try a wider date range.")
            else:
                st.warning("Not enough data to perform Market Basket Analysis.")