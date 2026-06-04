import streamlit as pd
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# 1. Page Configuration
st.set_page_config(
    page_title="Startup Ecosystem Deep Analytics",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS injection for sleek UI
st.markdown("""
    <style>
    .main .block-container {padding-top: 2rem; padding-bottom: 2rem;}
    .stMetric {background-color: #ffffff; padding: 1.2rem; border-radius: 10px; border: 1px solid #E5E7EB; box-shadow: 0 1px 3px rgba(0,0,0,0.05);}
    div[data-testid="stExpander"] {background-color: #ffffff; border-radius: 10px; border: 1px solid #E5E7EB;}
    h1, h2, h3 {color: #111827; font-weight: 700;}
    .insight-card {background-color: #EEF2F6; padding: 1rem; border-left: 5px solid #4F46E5; border-radius: 4px; margin-bottom: 1rem;}
    </style>
""", unsafe_allowed_html=True)

# 2. Data Loading & Optimization
@st.cache_data
def load_data():
    df = pd.read_csv("startup_data (1).csv")
    # Feature Engineering
    df['Valuation-to-Funding Multiple'] = df['Valuation (M USD)'] / df['Funding Amount (M USD)']
    df['Revenue-to-Funding Multiple'] = df['Revenue (M USD)'] / df['Funding Amount (M USD)']
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("⚠️ Dataset not found! Please place 'startup_data (1).csv' inside the working directory or 'data/' folder.")
    st.stop()

# 3. Sidebar Filters
st.sidebar.header("🎯 Analytics Filters")

# Filter 1: Region
all_regions = sorted(df['Region'].unique())
selected_regions = st.sidebar.multiselect("Select Regions", all_regions, default=all_regions)

# Filter 2: Industry
all_industries = sorted(df['Industry'].unique())
selected_industries = st.sidebar.multiselect("Select Industries", all_industries, default=all_industries)

# Filter 3: Exit Status
all_exits = sorted(df['Exit Status'].unique())
selected_exits = st.sidebar.multiselect("Select Exit Status", all_exits, default=all_exits)

# Filter 4: Year Founded Slider
min_year, max_year = int(df['Year Founded'].min()), int(df['Year Founded'].max())
selected_years = st.sidebar.slider("Year Founded Range", min_year, max_year, (min_year, max_year))

# Filter 5: Profitability Toggle
profit_option = st.sidebar.radio("Profitability Status", ["All Startups", "Profitable Only", "Non-Profitable Only"])

# Filter Logic Application
filtered_df = df[
    (df['Region'].isin(selected_regions)) &
    (df['Industry'].isin(selected_industries)) &
    (df['Exit Status'].isin(selected_exits)) &
    (df['Year Founded'].between(selected_years[0], selected_years[1]))
]

if profit_option == "Profitable Only":
    filtered_df = filtered_df[filtered_df['Profitable'] == 1]
elif profit_option == "Non-Profitable Only":
    filtered_df = filtered_df[filtered_df['Profitable'] == 0]

# 4. Header Section
st.title("🚀 Startup Ecosystem Deep Analytics Dashboard")
st.markdown("Unveiling macro trends, risk metrics, and valuation multiples across global startup ecosystems.")
st.markdown("---")

# Empty state handler
if filtered_df.empty:
    st.warning("⚠️ No data available matching your selected filters. Try broadening your criteria in the sidebar.")
    st.stop()

# 5. Top Level KPIs Matrix
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Total Startups", f"{len(filtered_df)}")
with col2:
    st.metric("Total Funding", f"${filtered_df['Funding Amount (M USD)'].sum():,.1f}M")
with col3:
    st.metric("Total Valuation", f"${filtered_df['Valuation (M USD)'].sum():,.1f}M")
with col4:
    prof_pct = (filtered_df['Profitable'].sum() / len(filtered_df)) * 100 if len(filtered_df) > 0 else 0
    st.metric("Profitability Rate", f"{prof_pct:.1f}%")
with col5:
    st.metric("Avg Market Share", f"{filtered_df['Market Share (%)'].mean():.2f}%")

st.markdown("<br>", unsafe_allowed_html=True)

# 6. Deep Analytics - Multi-Tab UI Layout
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Market Capital & Distribution", 
    "🏢 Sector & Regional Performance", 
    "💰 Financial ROI Insights", 
    "🔍 Granular Explorer"
])

with tab1:
    st.subheader("Market Distribution Dynamics")
    left_col, right_col = st.columns(2)
    
    with left_col:
        # Scatter Plot: Funding vs Valuation
        fig_scatter = px.scatter(
            filtered_df, 
            x="Funding Amount (M USD)", 
            y="Valuation (M USD)",
            color="Industry",
            size="Revenue (M USD)",
            hover_name="Startup Name",
            title="Funding vs. Valuation Matrix (Bubble Size = Revenue)",
            template="plotly_white",
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        fig_scatter.update_layout(title_font_size=16)
        st.plotly_chart(fig_scatter, use_container_width=True)
        
    with right_col:
        # Distribution: Exit Status
        fig_pie = px.pie(
            filtered_df, 
            names="Exit Status", 
            title="Share of Exit Statuses",
            hole=0.4,
            template="plotly_white",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(title_font_size=16)
        st.plotly_chart(fig_pie, use_container_width=True)

    # Contextual Automated Insights
    st.markdown("#### 💡 Key Observations")
    top_valued_startup = filtered_df.loc[filtered_df['Valuation (M USD)'].idxmax()]
    st.markdown(f"""
    <div class="insight-card">
    • The highest valued startup matching current criteria is <b>{top_valued_startup['Startup Name']}</b> valued at <b>${top_valued_startup['Valuation (M USD)']:,.1f}M</b> within the <b>{top_valued_startup['Industry']}</b> industry.<br>
    • Out of the filtered dataset, <b>{(filtered_df['Exit Status'] == 'IPO').sum()}</b> startups have achieved an <b>IPO</b> status, indicating late-stage maturation.
    </div>
    """, unsafe_allowed_html=True)


with tab2:
    st.subheader("Sectoral and Regional Benchmarking")
    left_col, right_col = st.columns(2)
    
    with left_col:
        # Grouped bar chart: Valuation and Funding by Industry
        ind_summary = filtered_df.groupby('Industry')[['Valuation (M USD)', 'Funding Amount (M USD)']].mean().reset_index()
        ind_summary = ind_summary.sort_values(by="Valuation (M USD)", ascending=False)
        
        fig_ind = go.Figure()
        fig_ind.add_trace(go.Bar(x=ind_summary['Industry'], y=ind_summary['Valuation (M USD)'], name='Avg Valuation (M)', marker_color='#4F46E5'))
        fig_ind.add_trace(go.Bar(x=ind_summary['Industry'], y=ind_summary['Funding Amount (M USD)'], name='Avg Funding (M)', marker_color='#9CA3AF'))
        fig_ind.update_layout(
            title='Average Valuation vs. Funding by Industry Sectors',
            barmode='group',
            template='plotly_white',
            title_font_size=16,
            xaxis_title="Industry"
        )
        st.plotly_chart(fig_ind, use_container_width=True)
        
    with right_col:
        # Regional Share of Market
        region_summary = filtered_df.groupby('Region')['Market Share (%)'].sum().reset_index().sort_values(by="Market Share (%)", ascending=False)
        fig_region = px.bar(
            region_summary,
            x="Market Share (%)",
            y="Region",
            orientation='h',
            title="Total Aggregate Market Share by Region (%)",
            template="plotly_white",
            color="Market Share (%)",
            color_continuous_scale="Purples"
        )
        fig_region.update_layout(title_font_size=16, yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig_region, use_container_width=True)

    # Financial efficiency insight
    best_ind = ind_summary.iloc[0]['Industry'] if not ind_summary.empty else "N/A"
    st.markdown(f"""
    <div class="insight-card">
    • <b>{best_ind}</b> leads the sector layout in terms of average valuation under current filters.<br>
    • Regional strength is clustered heaviest in regions with highest aggregated market share percentages.
    </div>
    """, unsafe_allowed_html=True)


with tab3:
    st.subheader("Capital Efficiency & Profitability Vectors")
    left_col, right_col = st.columns(2)
    
    with left_col:
        # Efficiency Score Boxplot
        fig_box = px.box(
            filtered_df, 
            x="Industry", 
            y="Valuation-to-Funding Multiple",
            title="Valuation Multiple ($ Val / $ Fund) Distribution by Industry",
            color="Industry",
            template="plotly_white"
        )
        fig_box.update_layout(title_font_size=16, showlegend=False)
        st.plotly_chart(fig_box, use_container_width=True)
        
    with right_col:
        # Profitability vs. Revenue Scatter
        fig_rev_val = px.scatter(
            filtered_df,
            x="Revenue (M USD)",
            y="Valuation (M USD)",
            color="Profitable",
            symbol="Profitable",
            color_discrete_map={1: "#10B981", 0: "#EF4444"},
            labels={"Profitable": "Is Profitable? (1=Yes, 0=No)"},
            title="Revenue vs. Valuation Correlation (Split by Profitability Status)",
            template="plotly_white"
        )
        fig_rev_val.update_layout(title_font_size=16)
        st.plotly_chart(fig_rev_val, use_container_width=True)

    # Calculations for text insight
    avg_multiple = filtered_df['Valuation-to-Funding Multiple'].mean()
    st.markdown(f"""
    <div class="insight-card">
    • The average global capital efficiency multiplier stands at <b>{avg_multiple:.2f}x</b> (meaning startups average ${avg_multiple:.2f} of valuation for every $1 invested).<br>
    • High efficiency sectors can be identified via upper outliers in the boxplot visualization.
    </div>
    """, unsafe_allowed_html=True)


with tab4:
    st.subheader("Interactive Cohort Explorer")
    st.markdown("Filter, sort, and slice down to target list cohorts. Use the multi-select tools to export granular results.")
    
    # Column configuration map for a cleaner UI
    st.dataframe(
        filtered_df.sort_values(by="Valuation (M USD)", ascending=False),
        column_config={
            "Funding Amount (M USD)": st.column_config.NumberColumn("Funding ($M)", format="$%.2fM"),
            "Valuation (M USD)": st.column_config.NumberColumn("Valuation ($M)", format="$%.2fM"),
            "Revenue (M USD)": st.column_config.NumberColumn("Revenue ($M)", format="$%.2fM"),
            "Market Share (%)": st.column_config.NumberColumn("Market Share", format="%.2f%%"),
            "Valuation-to-Funding Multiple": st.column_config.NumberColumn("Val Multiple", format="%.2fx"),
            "Profitable": st.column_config.CheckboxColumn("Profitable Status")
        },
        use_container_width=True,
        hide_index=True
    )
    
    # Download Action
    csv_data = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Filtered Cohort Dataset (CSV)",
        data=csv_data,
        file_name="filtered_startup_cohort.csv",
        mime="text/csv"
    )
