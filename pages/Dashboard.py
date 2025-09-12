
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
from components.auth import require_auth, logout
from components.api_client import APIClient
from config import STATUS_COLORS

# Check authentication
require_auth()

# Page header
st.title("📊 Campaign Dashboard")

# Add logout button in sidebar
with st.sidebar:
    if st.button("🚪 Logout", use_container_width=True):
        logout()

# Refresh button
col1, col2, col3 = st.columns([6, 1, 1])
with col3:
    if st.button("🔄 Refresh"):
        st.rerun()

# Get statistics from API
api = APIClient()
stats_response = api.get_stats()
campaigns_response = api.get_campaigns()

if stats_response.get('success'):
    stats = stats_response.get('statistics', {})
else:
    # Default stats for demo
    stats = {
        'total_campaigns': 0,
        'active_campaigns': 0,
        'completed_campaigns': 0,
        'total_messages_sent': 0,
        'total_messages_delivered': 0,
        'overall_success_rate': 0,
        'campaigns_by_status': {}
    }

# Display main metrics
st.markdown("### 📈 Overall Statistics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total Campaigns",
        value=stats.get('total_campaigns', 0),
        delta=None
    )

with col2:
    st.metric(
        label="Active Campaigns",
        value=stats.get('active_campaigns', 0),
        delta=None
    )

with col3:
    st.metric(
        label="Messages Sent",
        value=f"{stats.get('total_messages_sent', 0):,}",
        delta=None
    )

with col4:
    st.metric(
        label="Success Rate",
        value=f"{stats.get('overall_success_rate', 0):.1f}%",
        delta=None
    )

# Charts section
st.markdown("---")
st.markdown("### 📊 Analytics")

col1, col2 = st.columns(2)

with col1:
    # Campaign status distribution pie chart
    st.markdown("#### Campaign Status Distribution")
    
    status_data = stats.get('campaigns_by_status', {})
    if status_data:
        fig = go.Figure(data=[go.Pie(
            labels=list(status_data.keys()),
            values=list(status_data.values()),
            hole=0.3,
            marker_colors=[STATUS_COLORS.get(k, '#999') for k in status_data.keys()]
        )])
        fig.update_layout(
            height=300,
            margin=dict(t=0, b=0, l=0, r=0),
            showlegend=True
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No campaign data available")

with col2:
    # Delivery metrics
    st.markdown("#### Message Delivery Metrics")
    
    delivery_data = {
        'Sent': stats.get('total_messages_sent', 0),
        'Delivered': stats.get('total_messages_delivered', 0),
        'Failed': stats.get('total_messages_sent', 0) - stats.get('total_messages_delivered', 0)
    }
    
    if delivery_data['Sent'] > 0:
        fig = go.Figure(data=[
            go.Bar(
                x=list(delivery_data.keys()),
                y=list(delivery_data.values()),
                marker_color=['#2196F3', '#4CAF50', '#F44336']
            )
        ])
        fig.update_layout(
            height=300,
            margin=dict(t=0, b=0, l=0, r=0),
            yaxis_title="Messages",
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No message data available")

# Recent Campaigns Table
st.markdown("---")
st.markdown("### 📋 Recent Campaigns")

if campaigns_response.get('results'):
    campaigns_df = pd.DataFrame(campaigns_response['results'])
    
    # Format the dataframe for display
    display_columns = ['id', 'template_name', 'status', 'total_recipients', 
                      'sent_count', 'delivered_count', 'success_rate', 'created_at']
    
    # Filter columns that exist
    available_columns = [col for col in display_columns if col in campaigns_df.columns]
    campaigns_display = campaigns_df[available_columns].copy()
    
    # Format dates
    if 'created_at' in campaigns_display.columns:
        campaigns_display['created_at'] = pd.to_datetime(campaigns_display['created_at']).dt.strftime('%Y-%m-%d %H:%M')
    
    # Format success rate
    if 'success_rate' in campaigns_display.columns:
        campaigns_display['success_rate'] = campaigns_display['success_rate'].apply(lambda x: f"{x:.1f}%")
    
    # Rename columns for display
    campaigns_display.columns = ['ID', 'Template', 'Status', 'Recipients', 
                                'Sent', 'Delivered', 'Success Rate', 'Created'][:len(campaigns_display.columns)]
    
    # Display table with custom styling
    st.dataframe(
        campaigns_display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Status": st.column_config.TextColumn(
                "Status",
                help="Campaign status",
            ),
        }
    )
else:
    st.info("No campaigns found. Create your first campaign to get started!")
    if st.button("➕ Create First Campaign"):
        st.switch_page("pages/2_➕_Create_Campaign.py")

# Performance Trend (Mock data for demonstration)
st.markdown("---")
st.markdown("### 📈 Performance Trend (Last 7 Days)")

# Generate mock trend data
dates = pd.date_range(end=datetime.now(), periods=7, freq='D')
mock_data = pd.DataFrame({
    'Date': dates,
    'Messages Sent': [150, 200, 180, 250, 300, 280, 320],
    'Messages Delivered': [145, 195, 175, 240, 290, 270, 310],
    'Success Rate': [96.7, 97.5, 97.2, 96.0, 96.7, 96.4, 96.9]
})

fig = go.Figure()

# Add traces
fig.add_trace(go.Scatter(
    x=mock_data['Date'],
    y=mock_data['Messages Sent'],
    name='Sent',
    line=dict(color='#2196F3', width=2)
))

fig.add_trace(go.Scatter(
    x=mock_data['Date'],
    y=mock_data['Messages Delivered'],
    name='Delivered',
    line=dict(color='#4CAF50', width=2)
))

fig.update_layout(
    height=400,
    margin=dict(t=0, b=0, l=0, r=0),
    hovermode='x unified',
    yaxis_title="Messages",
    xaxis_title="Date",
    showlegend=True
)

st.plotly_chart(fig, use_container_width=True)
