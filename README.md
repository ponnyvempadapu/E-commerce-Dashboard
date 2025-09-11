# E-commerce-Dashboard
An interactive dashboard for e-commerce analytics, featuring sales analysis, RFM customer segmentation, time series decomposition, and market basket analysis. Built with Python and Streamlit.


# 🛒 Advanced E-commerce Analytics Dashboard

An interactive dashboard built with Streamlit for analyzing e-commerce data. This project showcases sales trends, performs RFM customer segmentation, decomposes time series data, and uncovers product associations using market basket analysis.

---

### **🔴 Live Demo**

**[➡️ View the Live Deployed App Here](https-your-app-url.streamlit.app)**

*(After deploying on Streamlit Community Cloud, replace the link above with your public URL)*

### **🎥 Dashboard Demo**

![Dashboard Demo](./dashboard-demo.gif)

*(Create a GIF of you using the dashboard and add it to your repository with this filename)*

---

### **🎯 Project Overview**

This dashboard is designed to provide actionable insights for a fictional e-commerce business. By leveraging advanced data analysis techniques, it moves beyond simple reporting to answer complex business questions related to sales performance, customer behavior, and product relationships. The user-friendly interface allows non-technical stakeholders to explore data and make informed decisions.

### **✨ Key Features & Analysis**

* **Interactive KPI Metrics:** High-level view of Total Revenue, Sales Volume, and Unique Customers.
* **Advanced Filtering:** Granular control over the analysis with dynamic filters for Country and Date Range.
* **Core Sales Analysis:** Visualization of monthly sales trends and identification of top-selling products and top customers by revenue.
* **👥 RFM Customer Segmentation:** Implements K-Means clustering on Recency, Frequency, and Monetary (RFM) metrics to segment customers into `High-Value`, `At-Risk`, and `New/Promising` categories.
* **🕰️ Time Series Decomposition:** Deconstructs daily sales data into its `Trend`, `Seasonality`, and `Residual` components to understand underlying patterns.
* **💡 Market Basket Analysis:** Employs the Apriori algorithm to discover product association rules, providing data-driven insights for cross-selling and promotion strategies (e.g., "Customers who buy X are also likely to buy Y").

---

### **🛠️ Tech Stack**

* **Language:** Python
* **Libraries:** Streamlit, Pandas, DuckDB, Plotly, Scikit-learn, Statsmodels, Mlxtend
* **Deployment:** Streamlit Community Cloud

---

### **⚙️ Running the Project Locally**

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/ponnyvempadapu/streamlit-ecommerce-dashboard.git](https://github.com/ponnyvempadapu/streamlit-ecommerce-dashboard.git)
    cd streamlit-ecommerce-dashboard
    ```
2.  **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Run the Streamlit app:**
    ```bash
    streamlit run app.py
    ```
