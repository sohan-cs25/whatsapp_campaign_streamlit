# streamlit-app/pages/3_📈_Campaigns.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time
import json
import requests
from components.auth import require_auth, logout
from components.api_client import APIClient
from config import STATUS_COLORS, STATUS_ICONS

# Check authentication
require_auth()

# Page header
st.title("📈 Campaign Management")

# Add logout button in sidebar
with st.sidebar:
    if st.button("🚪 Logout", use_container_width=True):
        logout()
    
    st.markdown("---")
    st.markdown("### 🎯 Quick Actions")
    if st.button("➕ Create New Campaign", use_container_width=True):
        st.switch_page("pages/Create_Campaign.py")
    if st.button("📊 View Dashboard", use_container_width=True):
        st.switch_page("pages/Dashboard.py")
    
    # Add debug section in sidebar
    st.markdown("---")
    st.markdown("### 🔍 Debug Tools")
    show_debug = st.checkbox("Show Debug Info")
    
    if show_debug:
        # Test API connection
        if st.button("🧪 Test API Connection"):
            api = APIClient()
            try:
                response = api.get_campaigns()
                if response and 'results' in response:
                    st.success("✅ API Connection OK")
                    st.write(f"Found {len(response['results'])} campaigns")
                else:
                    st.error("❌ API Error")
                    st.write(response)
            except Exception as e:
                st.error(f"❌ Connection Error: {str(e)}")

# Initialize session state
if 'selected_campaign' not in st.session_state:
    st.session_state.selected_campaign = None
if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = False

# Debug information display
if show_debug if 'show_debug' in locals() else False:
    with st.expander("🔍 Debug Information", expanded=False):
        st.write("**Session State:**")
        st.write(f"- Logged in: {st.session_state.get('logged_in', False)}")
        st.write(f"- Username: {st.session_state.get('username', 'Not set')}")
        
        # Check token from session state
        token = st.session_state.get('token') or st.session_state.get('access_token')
        if token:
            st.write(f"- Token: {token[:20]}...")
        else:
            st.write("- Token: Not set")
        
        # API Client info
        api = APIClient()
        st.write(f"- API Base URL: {getattr(api, 'base_url', 'Not available')}")

def debug_start_campaign(campaign_id):
    """Enhanced start campaign function with debugging"""
    st.write("🔍 **Debug Start Campaign Process:**")
    
    # Show campaign ID
    st.write(f"- Campaign ID: {campaign_id}")
    
    # Get API client
    api = APIClient()
    
    # Check if API client has the method
    if hasattr(api, 'start_campaign'):
        st.write("- ✅ API client has start_campaign method")
        
        try:
            st.write("📡 **Making API Request...**")
            
            # Call the API
            response = api.start_campaign(campaign_id)
            
            st.write("**API Response:**")
            st.code(json.dumps(response, indent=2))
            
            if response.get('success'):
                st.success("✅ Campaign started successfully!")
                return True, response.get('message', 'Campaign started')
            else:
                st.error(f"❌ API Error: {response.get('error', 'Unknown error')}")
                return False, response.get('error', 'Unknown error')
                
        except Exception as e:
            st.error(f"❌ Exception occurred: {str(e)}")
            st.write("**Exception Details:**")
            st.exception(e)
            return False, str(e)
    else:
        st.error("❌ API client doesn't have start_campaign method")
        
        # Try direct API call as fallback
        st.write("🔄 **Trying direct API call...**")
        
        try:
            # Get token from session state
            token = st.session_state.get('token') or st.session_state.get('access_token')
            
            if not token:
                st.error("❌ No authentication token found")
                return False, "No authentication token"
            
            # Make direct API call
            headers = {"Authorization": f"Bearer {token}"}
            api_base = getattr(api, 'base_url', 'http://localhost:8000')
            url = f"{api_base}/api/campaigns/{campaign_id}/start/"
            
            st.write(f"- URL: {url}")
            st.write(f"- Headers: Authorization: Bearer {token[:20]}...")
            
            response = requests.post(url, headers=headers)
            
            st.write(f"- Status Code: {response.status_code}")
            st.write(f"- Response Text: {response.text}")
            
            if response.status_code == 200:
                response_data = response.json()
                st.success("✅ Direct API call successful!")
                return True, response_data.get('message', 'Campaign started')
            else:
                st.error(f"❌ Direct API call failed: {response.status_code}")
                return False, f"HTTP {response.status_code}: {response.text}"
                
        except Exception as e:
            st.error(f"❌ Direct API call exception: {str(e)}")
            return False, str(e)

# Get campaigns from API
api = APIClient()
campaigns_response = api.get_campaigns()

if campaigns_response.get('results'):
    campaigns = campaigns_response['results']
    
    # Campaign selector
    st.markdown("### 📋 Select Campaign")
    
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        # Create campaign options
        campaign_options = {
            f"{c['id']} - {c['template_name']} ({c['status']})": c['id'] 
            for c in campaigns
        }
        
        selected_option = st.selectbox(
            "Choose a campaign to manage",
            options=list(campaign_options.keys()),
            index=0 if not st.session_state.selected_campaign else None
        )
        
        if selected_option:
            st.session_state.selected_campaign = campaign_options[selected_option]
    
    with col2:
        auto_refresh = st.checkbox("Auto Refresh (5s)", value=st.session_state.auto_refresh)
        st.session_state.auto_refresh = auto_refresh
    
    with col3:
        if st.button("🔄 Refresh Now"):
            st.rerun()
    
    # Auto refresh logic
    if st.session_state.auto_refresh:
        time.sleep(5)
        st.rerun()
    
    # Display selected campaign details
    if st.session_state.selected_campaign:
        campaign_id = st.session_state.selected_campaign
        
        # Get campaign details
        campaign_response = api.get_campaign(campaign_id)
        stats_response = api.get_campaign_statistics(campaign_id)
        
        if campaign_response.get('id'):
            campaign = campaign_response
            stats = stats_response.get('statistics', {}) if stats_response.get('success') else {}
            
            st.markdown("---")
            
            # Campaign Header
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"## {campaign['template_name']}")
            with col2:
                status_color = STATUS_COLORS.get(campaign['status'], '#999')
                st.markdown(f"""
                <div style="background-color: {status_color}; color: white; padding: 8px; 
                            border-radius: 5px; text-align: center; font-weight: bold;">
                    {campaign['status'].upper()}
                </div>
                """, unsafe_allow_html=True)
            
            # Campaign Metrics
            st.markdown("### 📊 Campaign Metrics")
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("Total Recipients", campaign.get('total_recipients', 0))
            with col2:
                st.metric("Sent", campaign.get('sent_count', 0))
            with col3:
                st.metric("Delivered", campaign.get('delivered_count', 0))
            with col4:
                st.metric("Read", campaign.get('read_count', 0))
            with col5:
                st.metric("Failed", campaign.get('failed_count', 0))
            
            # Progress Bar
            if campaign['total_recipients'] > 0:
                progress = (campaign['sent_count'] / campaign['total_recipients']) * 100
                
                st.markdown("### 📈 Progress")
                progress_bar = st.progress(0)
                progress_bar.progress(int(progress))
                
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.markdown(f"""
                    <div style="text-align: center; font-size: 24px; font-weight: bold; color: {STATUS_COLORS.get('running')}"">
                        {progress:.1f}% Complete
                    </div>
                    """, unsafe_allow_html=True)
            
            # Campaign Actions
            st.markdown("---")
            st.markdown("### 🎮 Campaign Controls")
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                if campaign['status'] in ['pending', 'paused']:
                    if st.button("▶️ Start", use_container_width=True, type="primary"):
                        # Use debug version if debug mode is on
                        if show_debug if 'show_debug' in locals() else False:
                            success, message = debug_start_campaign(campaign_id)
                        else:
                            # Use original API client method
                            response = api.start_campaign(campaign_id)
                            success = response.get('success', False)
                            message = response.get('message') if success else response.get('error')
                        
                        if success:
                            st.success(f"✅ {message}")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
            
            with col2:
                if campaign['status'] == 'running':
                    if st.button("⏸️ Pause", use_container_width=True):
                        response = api.pause_campaign(campaign_id)
                        if response.get('success'):
                            st.success("Campaign paused!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(response.get('error'))
            
            with col3:
                if campaign['status'] == 'paused':
                    if st.button("▶️ Resume", use_container_width=True):
                        response = api.resume_campaign(campaign_id)
                        if response.get('success'):
                            st.success("Campaign resumed!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(response.get('error'))
            
            with col4:
                if st.button("📊 Refresh Stats", use_container_width=True):
                    st.rerun()
            
            with col5:
                # Download report button
                st.button("📥 Export Report", use_container_width=True, disabled=True)
            
            # Show debug info for current campaign if debug mode is on
            if show_debug if 'show_debug' in locals() else False:
                with st.expander("🔍 Campaign Debug Info", expanded=False):
                    st.write("**Campaign Data:**")
                    st.code(json.dumps(campaign, indent=2))
                    
                    if stats:
                        st.write("**Statistics Data:**")
                        st.code(json.dumps(stats, indent=2))
            
            # Detailed Statistics
            if campaign['status'] in ['completed', 'running', 'paused']:
                st.markdown("---")
                st.markdown("### 📉 Detailed Statistics")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Delivery Funnel
                    st.markdown("#### Delivery Funnel")
                    
                    funnel_data = {
                        'Stage': ['Queued', 'Sent', 'Delivered', 'Read'],
                        'Count': [
                            campaign['total_recipients'],
                            campaign['sent_count'],
                            campaign['delivered_count'],
                            campaign['read_count']
                        ]
                    }
                    
                    fig = go.Figure(go.Funnel(
                        y=funnel_data['Stage'],
                        x=funnel_data['Count'],
                        textinfo="value+percent initial",
                        marker=dict(color=['#9E9E9E', '#2196F3', '#4CAF50', '#00BCD4'])
                    ))
                    
                    fig.update_layout(
                        height=400,
                        margin=dict(t=20, b=20, l=20, r=20)
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Success Rate Gauge
                    st.markdown("#### Success Rate")
                    
                    success_rate = campaign.get('success_rate', 0)
                    
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number+delta",
                        value=success_rate,
                        domain={'x': [0, 1], 'y': [0, 1]},
                        title={'text': "Delivery Rate (%)"},
                        delta={'reference': 95, 'increasing': {'color': "green"}},
                        gauge={
                            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                            'bar': {'color': "darkblue"},
                            'bgcolor': "white",
                            'borderwidth': 2,
                            'bordercolor': "gray",
                            'steps': [
                                {'range': [0, 50], 'color': '#ffcccc'},
                                {'range': [50, 80], 'color': '#ffffcc'},
                                {'range': [80, 100], 'color': '#ccffcc'}
                            ],
                            'threshold': {
                                'line': {'color': "red", 'width': 4},
                                'thickness': 0.75,
                                'value': 95
                            }
                        }
                    ))
                    
                    fig.update_layout(
                        height=400,
                        margin=dict(t=20, b=20, l=20, r=20)
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
            
            # Campaign Timeline
            if campaign.get('started_at'):
                st.markdown("---")
                st.markdown("### ⏱️ Campaign Timeline")
                
                timeline_data = []
                
                if campaign.get('created_at'):
                    timeline_data.append({
                        'Event': 'Created',
                        'Time': campaign['created_at'],
                        'Icon': '🆕'
                    })
                
                if campaign.get('started_at'):
                    timeline_data.append({
                        'Event': 'Started',
                        'Time': campaign['started_at'],
                        'Icon': '▶️'
                    })
                
                if campaign.get('completed_at'):
                    timeline_data.append({
                        'Event': 'Completed',
                        'Time': campaign['completed_at'],
                        'Icon': '✅'
                    })
                
                for item in timeline_data:
                    col1, col2 = st.columns([1, 5])
                    with col1:
                        st.markdown(f"### {item['Icon']}")
                    with col2:
                        st.markdown(f"**{item['Event']}**  \n{item['Time']}")
            
            # Messages Preview (Optional)
            with st.expander("📨 View Messages (Sample)", expanded=False):
                messages_response = api.get_campaign_messages(campaign_id)
                if messages_response.get('results'):
                    messages_df = pd.DataFrame(messages_response['results'][:10])
                    
                    if not messages_df.empty:
                        display_columns = ['phone_number', 'status', 'sent_at', 'delivered_at']
                        available_columns = [col for col in display_columns if col in messages_df.columns]
                        
                        if available_columns:
                            st.dataframe(
                                messages_df[available_columns],
                                use_container_width=True,
                                hide_index=True
                            )
                        else:
                            st.info("No message details available")
                else:
                    st.info("No messages found")
            
else:
    st.info("No campaigns found. Create your first campaign to get started!")
    if st.button("➕ Create Your First Campaign"):
        st.switch_page("pages/Create_Campaign.py")

# Add workflow explanation at the bottom
st.markdown("---")
with st.expander("📚 Campaign Workflow Guide", expanded=False):
    st.markdown("""
    ### Campaign Status Flow:
    
    1. **📝 Draft** → Created but file still processing
    2. **✅ Pending** → File processed, ready to start
    3. **🚀 Running** → Actively sending messages
    4. **⏸️ Paused** → Temporarily stopped (can resume)
    5. **✅ Completed** → All messages sent
    6. **❌ Failed** → Error occurred
    
    ### How to Start a Campaign:
    
    1. **Create Campaign** → Upload file with contacts
    2. **Wait for Processing** → File is validated and messages created (usually 5-30 seconds)
    3. **Check Status** → Refresh to see if status changed from 'draft' to 'pending'
    4. **Start Campaign** → Click "Start Campaign" button when status is 'pending'
    5. **Monitor Progress** → Watch the progress bar and metrics update
    
    ### Troubleshooting:
    
    - **Campaign stuck in 'draft'?** → Make sure Celery worker is running
    - **Can't start campaign?** → Check if status is 'pending' and file has valid recipients
    - **No progress after starting?** → Check WhatsApp API credentials in backend
    - **High failure rate?** → Verify phone numbers format and template name
    
    ### Debug Mode:
    
    - **Enable Debug Info** → Check the "Show Debug Info" box in the sidebar
    - **Test API Connection** → Use the "Test API Connection" button
    - **View Raw Data** → Expand debug sections to see API responses
    - **Detailed Start Process** → Debug mode shows step-by-step start campaign process
    """)