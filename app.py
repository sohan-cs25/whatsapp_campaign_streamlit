
import streamlit as st
from components.auth import check_authentication, login_form, signup_form, init_session_state
from config import APP_NAME, APP_ICON, PAGE_ICON, LAYOUT

# Page configuration
st.set_page_config(
    page_title=APP_NAME,
    page_icon=PAGE_ICON,
    layout=LAYOUT,
    initial_sidebar_state="expanded"
)

# Custom CSS for professional look
st.markdown("""
<style>
    /* Main header styling */
    .main-header {
        background: linear-gradient(90deg, #25D366 0%, #128C7E 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    /* Card styling */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
        transition: transform 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, #25D366 0%, #128C7E 100%);
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 5px;
        font-weight: 600;
        transition: opacity 0.2s;
    }
    
    .stButton > button:hover {
        opacity: 0.9;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f5f5f5;
    }
    
    /* Success message styling */
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

def main():
    """Main application"""
    init_session_state()
    
    if not check_authentication():
        # Show login/signup page
        st.markdown(f"""
        <div class="main-header">
            <h1>{APP_ICON} {APP_NAME}</h1>
            <p style="font-size: 1.2rem; opacity: 0.9;">Professional WhatsApp Marketing Solution</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.get('show_signup', False):
            signup_form()
        else:
            login_form()
    else:
        # User is authenticated, show main app
        st.markdown(f"""
        <div class="main-header">
            <h1>{APP_ICON} {APP_NAME}</h1>
            <p style="font-size: 1.2rem; opacity: 0.9;">Welcome back, {st.session_state.user.get('username', 'User')}!</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Welcome message
        st.info(f"""
        👋 Welcome to your WhatsApp Campaign Manager! 
        
        Use the sidebar to navigate:
        - **📊 Dashboard** - View your campaign statistics
        - **➕ Create Campaign** - Start a new campaign
        - **📈 Campaigns** - Manage existing campaigns
        """)
        
        # Quick stats
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: #25D366;">12</h3>
                <p style="color: #666;">Total Campaigns</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: #2196F3;">3</h3>
                <p style="color: #666;">Active</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: #4CAF50;">8</h3>
                <p style="color: #666;">Completed</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: #FF9800;">1</h3>
                <p style="color: #666;">Paused</p>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
