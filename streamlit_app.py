import streamlit as st
from datetime import datetime
from scraper import MDPIBrowserSession, run_mdpi_campaign

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="MDPI Automator", 
    page_icon="✉️", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- HEADER ---
st.title("✉️ MDPI Campaign Automator")
st.markdown("Automate your monthly mass mailing data collection. Extract, clean, and format data seamlessly.")
st.caption("The MDPI browser stays open after the campaign so its sign-in session is retained.")
st.divider()

if "mdpi_browser_session" not in st.session_state:
    st.session_state.mdpi_browser_session = MDPIBrowserSession()

# --- INPUT SECTION ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("🔑 Credentials")
    email = st.text_input("MDPI Email", placeholder="your.email@example.com")
    password = st.text_input("MDPI Password", type="password", placeholder="••••••••")

with col2:
    st.subheader("📅 Date Filters")
    current_year = datetime.now().year
    
    col_start, col_end = st.columns(2)
    with col_start:
        start_year = st.number_input("Start Year", min_value=2000, max_value=current_year+5, value=current_year-2)
    with col_end:
        end_year = st.number_input("End Year", min_value=2000, max_value=current_year+5, value=current_year)

st.subheader("🏷️ Journal Keywords")
st.markdown("Enter the keywords for your target journal (one per line):")
keywords_text = st.text_area("Keywords List", height=150, placeholder="spine\nscoliosis\ncervical\nlumbar...", label_visibility="collapsed")

st.divider()

# --- ACTION SECTION ---
if st.button("🚀 Start Campaign Automation", use_container_width=True, type="primary"):
    keywords = [k.strip() for k in keywords_text.split('\n') if k.strip()]
    
    if not email or not password:
        st.error("⚠️ Please enter your MDPI credentials.")
    elif not keywords:
        st.error("⚠️ Please enter at least one keyword.")
    else:
        # UI Elements for progress
        progress_bar = st.progress(0, text="Initializing automation engine...")
        
        with st.status("Running Campaign...", expanded=True) as status:
            
            # Create a callback function to update the Streamlit UI from inside the scraper
            def update_ui(msg):
                st.write(msg)
                
            try:
                # Call the actual scraper function
                output_file = run_mdpi_campaign(
                    email,
                    password,
                    start_year,
                    end_year,
                    keywords,
                    progress_callback=update_ui,
                    browser_session=st.session_state.mdpi_browser_session,
                )
                
                status.update(label="Campaign Complete!", state="complete", expanded=False)
                st.balloons()
                st.success(f"✅ Automation finished successfully! Data saved to **{output_file}**")
                
                # Provide a download button for the generated Excel file
                with open(output_file, "rb") as file:
                    st.download_button(
                        label="📥 Download Excel File",
                        data=file,
                        file_name=output_file,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    
            except Exception as e:
                status.update(label="Campaign Failed!", state="error", expanded=True)
                st.error(f"❌ An error occurred: {str(e)}")
