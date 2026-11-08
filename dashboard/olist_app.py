import pandas as pd
import plotly.express as px
import streamlit as st

from sqlalchemy import text
from src.database.postgres import olist_engine


# ---------------------------------------------------------------------
# Page configuration and visual theme
# ---------------------------------------------------------------------
st.set_page_config(
    page_title="Olist E-Commerce Analytics",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        .stApp {
            background-color: #0B1220;
            color: #E5E7EB;
        }

        [data-testid="stSidebar"] {
            background-color: #111B2E;
            border-right: 1px solid #263449;
        }

        [data-testid="stMetric"] {
            background-color: #162238;
            border: 1px solid #263B55;
            padding: 18px 18px;
            border-radius: 12px;
        }

        [data-testid="stMetricLabel"] {
            color: #AABBD0;
        }

        [data-testid="stMetricValue"] {
            color: #38BDF8;
        }

        h1, h2, h3 {
            color: #F1F5F9;
        }

        div[data-testid="stTabs"] button[aria-selected="true"] {
            color: #38BDF8;
            border-bottom-color: #38BDF8;
        }

        [data-testid="stDataFrame"] {
            border: 1px solid #263B55;
            border-radius: 10px;
        }

        div[data-testid="stAlert"] {
            border-radius: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🛒 Olist E-Commerce Analytics")
st.caption(
    "Business intelligence dashboard | Olist Brazilian E-Commerce Dataset"
)


# ---------------------------------------------------------------------
# Data access
# ---------------------------------------------------------------------
@st.cache_data(ttl=300)
def fetch_data(query: str) -> pd.DataFrame:
    """Run a read-only analytics query and cache its result for five minutes."""
    with olist_engine.connect() as connection:
        return pd.read_sql_query(text(query), connection)


try:
    order_kpis = fetch_data("SELECT * FROM vw_order_kpis")
    sales_kpis = fetch_data("SELECT * FROM vw_sales_kpis")

    monthly_sales = fetch_data(
        """
        SELECT *
        FROM vw_monthly_sales
        ORDER BY sales_month
        """
    )

    category_performance = fetch_data(
        """
        SELECT *
        FROM vw_category_performance
        ORDER BY item_gmv DESC
        """
    )

    product_performance = fetch_data(
        """
        SELECT *
        FROM vw_product_performance
        ORDER BY item_gmv DESC
        LIMIT 10
        """
    )

    customer_analytics = fetch_data(
        """
        SELECT *
        FROM vw_customer_analytics
        ORDER BY item_gmv DESC
        LIMIT 10
        """
    )

    order_status = fetch_data(
        """
        SELECT
            order_status,
            COUNT(*) AS total_orders
        FROM orders
        GROUP BY order_status
        ORDER BY total_orders DESC
        """
    )

    data_quality = fetch_data(
        """
        SELECT
            COUNT(*) FILTER (
                WHERE flag_approval_before_purchase
            ) AS approval_before_purchase,

            COUNT(*) FILTER (
                WHERE flag_carrier_before_purchase
            ) AS carrier_before_purchase,

            COUNT(*) FILTER (
                WHERE flag_customer_before_carrier
            ) AS customer_before_carrier,

            COUNT(*) FILTER (
                WHERE flag_delivered_missing_customer_date
            ) AS delivered_missing_date

        FROM orders
        """
    )

except Exception as error:
    st.error(
        "Could not load dashboard data. "
        "Please check the PostgreSQL connection and SQL analytics views."
    )
    st.exception(error)
    st.stop()


# ---------------------------------------------------------------------
# KPI calculations
# ---------------------------------------------------------------------
orders = order_kpis.iloc[0]
sales = sales_kpis.iloc[0]
quality = data_quality.iloc[0]

total_orders = int(orders["total_orders"])
delivered_orders = int(orders["delivered_orders"])
canceled_orders = int(orders["canceled_orders"])

item_gmv = float(sales["item_gmv_all_orders"])
delivered_gmv = float(sales["delivered_item_gmv"])
total_freight = float(sales["total_freight"])

delivery_rate = (
    delivered_orders / total_orders * 100
    if total_orders
    else 0
)


# ---------------------------------------------------------------------
# Shared Plotly styling
# ---------------------------------------------------------------------
PLOT_LAYOUT = {
    "template": "plotly_dark",
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font": {"color": "#E5E7EB"},
}

ACCENT_BLUE = "#38BDF8"
ACCENT_TEAL = "#2DD4BF"
STATUS_COLORS = [
    "#38BDF8",
    "#2DD4BF",
    "#A78BFA",
    "#F59E0B",
    "#FB7185",
    "#60A5FA",
    "#34D399",
    "#F97316",
]


# ---------------------------------------------------------------------
# Sidebar controls
# ---------------------------------------------------------------------
with st.sidebar:
    st.header("Dashboard Controls")
    st.write("**Dataset:** Olist E-Commerce")
    st.write("**Database:** PostgreSQL")
    st.write("**Analytics:** SQL Views")
    st.divider()

    if st.button("🔄 Refresh Dashboard", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.caption("Data refresh interval: 5 minutes")


# ---------------------------------------------------------------------
# Dashboard tabs
# ---------------------------------------------------------------------
overview_tab, sales_tab, product_tab, customer_tab, quality_tab = st.tabs(
    [
        "Overview",
        "Sales Analytics",
        "Products & Categories",
        "Customers",
        "Data Quality",
    ]
)


# ---------------------------------------------------------------------
# Overview
# ---------------------------------------------------------------------
with overview_tab:
    st.subheader("Business Overview")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Orders", f"{total_orders:,}")
    col2.metric("Delivered Orders", f"{delivered_orders:,}")
    col3.metric("Canceled Orders", f"{canceled_orders:,}")
    col4.metric("Delivery Rate", f"{delivery_rate:.2f}%")

    st.divider()

    col1, col2, col3 = st.columns(3)
    col1.metric("Item GMV", f"R$ {item_gmv:,.2f}")
    col2.metric("Delivered Item GMV", f"R$ {delivered_gmv:,.2f}")
    col3.metric("Total Freight", f"R$ {total_freight:,.2f}")

    st.divider()

    left, right = st.columns(2)

    with left:
        st.subheader("Monthly Item GMV")

        monthly_chart = px.line(
            monthly_sales,
            x="sales_month",
            y="item_gmv",
            markers=True,
            template="plotly_dark",
            color_discrete_sequence=[ACCENT_BLUE],
            labels={
                "sales_month": "Month",
                "item_gmv": "Item GMV (R$)",
            },
        )
        monthly_chart.update_traces(
            line={"width": 3},
            marker={"size": 7},
            hovertemplate=(
                "Month: %{x|%b %Y}<br>"
                "Item GMV: R$ %{y:,.2f}"
                "<extra></extra>"
            ),
        )
        monthly_chart.update_layout(
            **PLOT_LAYOUT,
            xaxis_title="Month",
            yaxis_title="Item GMV (R$)",
            hovermode="x unified",
        )
        st.plotly_chart(monthly_chart, use_container_width=True)

    with right:
        st.subheader("Order Status Distribution")

        status_chart = order_status.copy()
        status_total = status_chart["total_orders"].sum()
        status_chart["share_pct"] = (
            status_chart["total_orders"] / status_total * 100
            if status_total
            else 0
        )
        status_chart = status_chart.sort_values(
            "total_orders",
            ascending=True,
        )

        status_fig = px.bar(
            status_chart,
            x="total_orders",
            y="order_status",
            orientation="h",
            text="total_orders",
            custom_data=["share_pct"],
            color="order_status",
            color_discrete_sequence=STATUS_COLORS,
            labels={
                "total_orders": "Number of Orders",
                "order_status": "Order Status",
            },
        )
        status_fig.update_traces(
            textposition="outside",
            cliponaxis=False,
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Orders: %{x:,}<br>"
                "Share: %{customdata[0]:.2f}%"
                "<extra></extra>"
            ),
        )
        status_fig.update_layout(
            **PLOT_LAYOUT,
            xaxis_type="log",
            xaxis_title="Number of Orders (log scale)",
            yaxis_title="",
            showlegend=False,
            margin={"l": 15, "r": 55, "t": 25, "b": 45},
            height=430,
        )
        st.plotly_chart(status_fig, use_container_width=True)

    st.caption(
        "The order-status chart uses a logarithmic x-axis so smaller "
        "statuses remain visible alongside the dominant delivered category."
    )


# ---------------------------------------------------------------------
# Sales analytics
# ---------------------------------------------------------------------
with sales_tab:
    st.subheader("Sales Performance")

    col1, col2 = st.columns(2)
    col1.metric("All Orders Item GMV", f"R$ {item_gmv:,.2f}")
    col2.metric("Delivered Orders Item GMV", f"R$ {delivered_gmv:,.2f}")

    st.divider()
    st.subheader("Monthly Sales Trend")

    monthly_bar = px.bar(
        monthly_sales,
        x="sales_month",
        y="item_gmv",
        template="plotly_dark",
        color_discrete_sequence=[ACCENT_TEAL],
        labels={
            "sales_month": "Month",
            "item_gmv": "Item GMV (R$)",
        },
    )
    monthly_bar.update_layout(
        **PLOT_LAYOUT,
        xaxis_title="Month",
        yaxis_title="Item GMV (R$)",
        hovermode="x unified",
    )
    monthly_bar.update_traces(
        hovertemplate=(
            "Month: %{x|%b %Y}<br>"
            "Item GMV: R$ %{y:,.2f}"
            "<extra></extra>"
        )
    )
    st.plotly_chart(monthly_bar, use_container_width=True)

    st.subheader("Monthly Sales Data")
    st.dataframe(
        monthly_sales,
        use_container_width=True,
        hide_index=True,
    )


# ---------------------------------------------------------------------
# Products and categories
# ---------------------------------------------------------------------
with product_tab:
    st.subheader("Category Performance")

    top_categories = (
        category_performance
        .sort_values("item_gmv", ascending=False)
        .head(10)
        .sort_values("item_gmv", ascending=True)
    )

    category_fig = px.bar(
        top_categories,
        x="item_gmv",
        y="category_name_english",
        orientation="h",
        text="item_gmv",
        template="plotly_dark",
        color="item_gmv",
        color_continuous_scale=["#164E63", "#38BDF8", "#A5F3FC"],
        labels={
            "item_gmv": "Item GMV (R$)",
            "category_name_english": "Category",
        },
    )
    category_fig.update_traces(
        texttemplate="R$ %{x:,.0f}",
        textposition="outside",
        cliponaxis=False,
        hovertemplate=(
            "Category: %{y}<br>"
            "Item GMV: R$ %{x:,.2f}"
            "<extra></extra>"
        ),
    )
    category_fig.update_layout(
        **PLOT_LAYOUT,
        xaxis_title="Item GMV (R$)",
        yaxis_title="",
        coloraxis_showscale=False,
        margin={"l": 15, "r": 65, "t": 25, "b": 45},
    )
    st.plotly_chart(category_fig, use_container_width=True)

    st.subheader("Top 10 Products")

    top_products = product_performance.sort_values(
        "item_gmv",
        ascending=True,
    )
    product_fig = px.bar(
        top_products,
        x="item_gmv",
        y="product_id",
        orientation="h",
        text="item_gmv",
        template="plotly_dark",
        color_discrete_sequence=[ACCENT_TEAL],
        labels={
            "item_gmv": "Item GMV (R$)",
            "product_id": "Product ID",
        },
    )
    product_fig.update_traces(
        texttemplate="R$ %{x:,.0f}",
        textposition="outside",
        cliponaxis=False,
        hovertemplate=(
            "Product ID: %{y}<br>"
            "Item GMV: R$ %{x:,.2f}"
            "<extra></extra>"
        ),
    )
    product_fig.update_layout(
        **PLOT_LAYOUT,
        xaxis_title="Item GMV (R$)",
        yaxis_title="",
        margin={"l": 15, "r": 65, "t": 25, "b": 45},
    )
    st.plotly_chart(product_fig, use_container_width=True)

    st.subheader("Category Details")
    st.dataframe(
        category_performance,
        use_container_width=True,
        hide_index=True,
    )


# ---------------------------------------------------------------------
# Customer analytics
# ---------------------------------------------------------------------
with customer_tab:
    st.subheader("Customer Analytics")

    state_summary = fetch_data(
        """
        SELECT
            customer_state,
            COUNT(*) AS total_customers
        FROM customers
        GROUP BY customer_state
        ORDER BY total_customers DESC
        """
    )

    left, right = st.columns(2)

    with left:
        st.subheader("Customers by State")

        state_chart = px.bar(
            state_summary.head(10).sort_values(
                "total_customers",
                ascending=True,
            ),
            x="total_customers",
            y="customer_state",
            orientation="h",
            text="total_customers",
            template="plotly_dark",
            color_discrete_sequence=[ACCENT_BLUE],
            labels={
                "total_customers": "Customers",
                "customer_state": "State",
            },
        )
        state_chart.update_traces(
            textposition="outside",
            cliponaxis=False,
            hovertemplate=(
                "State: %{y}<br>"
                "Customers: %{x:,}"
                "<extra></extra>"
            ),
        )
        state_chart.update_layout(
            **PLOT_LAYOUT,
            xaxis_title="Customers",
            yaxis_title="",
            margin={"l": 15, "r": 55, "t": 25, "b": 40},
        )
        st.plotly_chart(state_chart, use_container_width=True)

    with right:
        st.subheader("Top Customers by Item GMV")
        st.dataframe(
            customer_analytics[
                [
                    "customer_unique_id",
                    "customer_state",
                    "total_orders",
                    "item_gmv",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

    st.caption(
        "Customer analytics are based on customer records "
        "and their associated orders."
    )


# ---------------------------------------------------------------------
# Data quality
# ---------------------------------------------------------------------
with quality_tab:
    st.subheader("Data Quality Monitoring")
    st.write(
        "Order timestamp anomalies identified during "
        "the transformation process."
    )

    col1, col2 = st.columns(2)
    col1.metric(
        "Approval Before Purchase",
        f"{int(quality['approval_before_purchase']):,}",
    )
    col2.metric(
        "Carrier Before Purchase",
        f"{int(quality['carrier_before_purchase']):,}",
    )

    col1, col2 = st.columns(2)
    col1.metric(
        "Customer Before Carrier",
        f"{int(quality['customer_before_carrier']):,}",
    )
    col2.metric(
        "Delivered Missing Date",
        f"{int(quality['delivered_missing_date']):,}",
    )

    st.divider()
    st.subheader("Order Status Counts")
    st.dataframe(
        order_status,
        use_container_width=True,
        hide_index=True,
    )


# ---------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------
st.divider()
st.caption(
    "Olist E-Commerce Analytics | "
    "Built with Python, Streamlit, Plotly and PostgreSQL"
)
