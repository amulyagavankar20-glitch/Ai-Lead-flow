import streamlit as st
import pandas as pd
from config import APP_TITLE, APP_SUBTITLE
from utils import process_lead
import time

# --- Page Configuration ---
st.set_page_config(
    page_title=APP_TITLE,
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS ---
# Giving it a polished, professional look
st.markdown("""
<style>
    .reportview-container {
        background-color: #f4f6f9;
        font-family: 'Inter', sans-serif;
    }
    .main .block-container {
        padding-top: 2rem;
    }
    .stButton > button {
        width: 100%;
        background-color: #2e6c80;
        color: white;
        font-weight: 600;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #1e4b5c;
        border-color: #1e4b5c;
    }
    .result-card {
        background-color: white;
        color: #1e1e1e;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border-left: 5px solid #2e6c80;
    }
    .result-card h4 {
        color: #2e6c80;
        margin-top: 0;
        margin-bottom: 0.5rem;
    }
    .hot-lead {
        border-left: 5px solid #d9534f;
    }
    .warm-lead {
        border-left: 5px solid #f0ad4e;
    }
    .cold-lead {
        border-left: 5px solid #5bc0de;
    }
    .score-circle {
        font-size: 3rem;
        font-weight: 700;
        text-align: center;
        background-color: #f8f9fa;
        border-radius: 50%;
        width: 120px;
        height: 120px;
        line-height: 120px;
        margin: 0 auto;
        color: #2e6c80;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)


# --- Header ---
st.title("💼 " + APP_TITLE)
st.markdown(f"**{APP_SUBTITLE}**")
st.divider()

# --- Main Layout ---
col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("📝 Enter Lead Details")
    st.markdown("Please fill out the prospect information below.")
    
    with st.form("lead_form"):
        name = st.text_input("Contact Name (e.g., John Doe)", placeholder="Enter full name")
        company = st.text_input("Company Name", placeholder="Enter company name")
        industry = st.selectbox(
            "Industry", 
            ["Healthcare", "Technology", "Finance", "Retail", "Manufacturing", "Education", "Other"]
        )
        budget = st.number_input("Estimated Budget ($)", min_value=0, value=10000, step=5000)
        problem = st.text_area(
            "Problem Statement", 
            placeholder="Describe what the prospect is looking for or the problem they are trying to solve...",
            height=120
        )
        
        submitted = st.form_submit_button("Analzye Lead")


with col2:
    st.subheader("📊 AI Analysis Results")
    
    if submitted:
        # 1. Validation
        if not name or not company or not problem:
            st.error("⚠️ Please fill in all required fields (Name, Company, and Problem Statement).")
        else:
            # Prepare payload
            lead_data = {
                "name": name,
                "company": company,
                "industry": industry,
                "budget": budget,
                "problem": problem
            }
            
            with st.spinner("🤖 AI is analyzing the lead..."):
                # Simulating a slight delay for better UX even if webhook is fast
                time.sleep(1)
                
                # Make HTTP POST request to n8n webhook
                result = process_lead(lead_data)
                
                if "error" in result:
                    st.error(f"🚨 Integration Error: {result['error']}")
                    st.info("💡 Hint: Ensure n8n is running and the webhook URL in `config.py` is correct.")
                else:
                    # Successful Response Parsing
                    output_data = result.get("output", {})
                    score = output_data.get("lead_score", result.get("score", "N/A"))
                    reason = output_data.get("reason", result.get("reason", "No reason provided."))
                    action = output_data.get("recommended_action", result.get("recommended_action", "No action specified."))
                    email = output_data.get("followup_email", result.get("followup_email", "No email draft produced."))
                    
                    qualification = result.get("qualification", output_data.get("qualification", "UNKNOWN")).upper()
                    priority = result.get("priority", "UNKNOWN")
                    team = result.get("assigned_team", "Not assigned")
                    
                    st.success("Analysis Complete!")
                    
                    # Layout for Score and Badges
                    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
                    
                    with metric_col1:
                        st.markdown(f"<div class='score-circle'>{score}</div>", unsafe_allow_html=True)
                        st.markdown("<p style='text-align: center; font-weight: bold; margin-top: 10px;'>Lead Score</p>", unsafe_allow_html=True)
                        
                    with metric_col2:
                        qual_color = "red" if qualification == "HOT" else "orange" if qualification == "WARM" else "blue"
                        st.markdown(f"**Qualification:**")
                        st.markdown(f"<h3 style='color: {qual_color};'>{qualification}</h3>", unsafe_allow_html=True)
                    
                    with metric_col3:
                        st.markdown(f"**Priority:**")
                        st.markdown(f"<h3>{priority}</h3>", unsafe_allow_html=True)
                        
                    with metric_col4:
                        st.markdown(f"**Assigned Team:**")
                        st.markdown(f"<h3>{team}</h3>", unsafe_allow_html=True)
                    
                    st.divider()
                    
                    # Analysis Details
                    css_class = "hot-lead" if qualification == "HOT" else "warm-lead" if qualification == "WARM" else "cold-lead"
                    st.markdown(f"""
                    <div class="result-card {css_class}">
                        <h4>🧠 AI Reasoning</h4>
                        <p>{reason}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div class="result-card">
                        <h4>🎯 Recommended Action</h4>
                        <p>{action}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    with st.expander("✉️ View Drafted Follow-up Email", expanded=True):
                        st.text_area("Email Draft", value=email, height=250, disabled=True)

    else:
        st.info("👈 Fill out the form and submit to see AI qualification results.")
        
        # Placeholder view
        st.markdown("""
        <div style="opacity: 0.5; pointer-events: none;">
            <div class="result-card" style="min-height: 200px; display: flex; align-items: center; justify-content: center;">
                <h4>Results will appear here</h4>
            </div>
        </div>
        """, unsafe_allow_html=True)

