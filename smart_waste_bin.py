# smart_waste_bin.py
# Virtual environment: source smartbin-env/bin/activate
# Run: streamlit run smart_waste_bin.py

import streamlit as st
from PIL import Image
import numpy as np
import datetime
import time
from bin_graphics import BinGraphics
import os

os.environ['SDL_VIDEODRIVER'] = 'dummy'

# Streamlit UI setup
st.set_page_config(page_title="Smart Waste Bin", layout="wide")

# Custom CSS for better styling
st.markdown("""
    <style>
    .stProgress > div > div > div > div {
        background-image: linear-gradient(to right, #ff6b6b, #ff8787);
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #4CAF50;
        color: white;
    }
    div.row-widget.stRadio > div {
        flex-direction: row;
        align-items: center;
    }
    </style>
""", unsafe_allow_html=True)

# Center the title and add description
st.markdown("<h1 style='text-align: center; margin-bottom: 2rem;'>TrashLink</h1>", unsafe_allow_html=True)

# Add bin simulation state
if 'biomedical_level' not in st.session_state:
    st.session_state.biomedical_level = 0
if 'general_level' not in st.session_state:
    st.session_state.general_level = 0
if 'bin_graphics' not in st.session_state:
    try:
        st.session_state.bin_graphics = BinGraphics()
    except Exception as e:
        st.error(f"Failed to initialize graphics: {str(e)}")
        st.stop()

# Create a layout with two columns for better organization
main_col1, main_col2 = st.columns([2, 1])

with main_col1:
    # Create a single placeholder for bin visualization
    bin_display = st.empty()
    
    # Show initial bin state
    st.session_state.bin_graphics.draw_bin(
        st.session_state.biomedical_level,
        st.session_state.general_level
    )
    bin_display.image(st.session_state.bin_graphics.surface_to_image())

def simulate_bin_action(waste_type):
    current_bio = st.session_state.biomedical_level
    current_gen = st.session_state.general_level
    
    # Animate waste dropping with current bin levels
    for frame in st.session_state.bin_graphics.animate_waste_drop(
        waste_type, current_bio, current_gen
    ):
        bin_display.image(frame)
        time.sleep(0.01)  # Reduced from 0.02
    
    # Update bin levels
    if waste_type == "biomedical":
        st.session_state.biomedical_level = min(100, current_bio + 20)
    else:
        st.session_state.general_level = min(100, current_gen + 20)
    
    # Show final state
    st.session_state.bin_graphics.draw_bin(
        st.session_state.biomedical_level,
        st.session_state.general_level
    )
    bin_display.image(st.session_state.bin_graphics.surface_to_image())

with main_col2:
    st.markdown("<h3 style='text-align: center; margin-bottom: 1.5rem;'>Waste Disposal Controls</h3>", unsafe_allow_html=True)
    
    # Use a form for waste disposal actions
    with st.form(key='waste_disposal_form'):
        biomedical = st.form_submit_button("🩺 Throw Biomedical Waste")
        st.markdown("<br>", unsafe_allow_html=True)  # Add spacing
        general = st.form_submit_button("🗑️ Throw General Waste")

        if biomedical:
            simulate_bin_action("biomedical")
        elif general:
            simulate_bin_action("general")

    st.markdown("<br>", unsafe_allow_html=True)  # Add spacing

    # Status display
    st.markdown("<h3 style='text-align: center;'>Bin Levels</h3>", unsafe_allow_html=True)
    
    st.markdown("**Biomedical Waste Compartment**")
    st.progress(st.session_state.biomedical_level)
    if st.session_state.biomedical_level >= 90:
        st.error("🚨 ALERT: Biomedical bin critically full!")
    elif st.session_state.biomedical_level >= 80:
        st.warning("⚠️ Biomedical bin needs emptying!")

    st.markdown("<br>", unsafe_allow_html=True)  # Add spacing
    
    st.markdown("**General Waste Compartment**")
    st.progress(st.session_state.general_level)
    if st.session_state.general_level >= 90:
        st.error("🚨 ALERT: General waste bin critically full!")
    elif st.session_state.general_level >= 80:
        st.warning("⚠️ General waste bin needs emptying!")

    st.markdown("<br>", unsafe_allow_html=True)  # Add spacing
    
    # Reset button
    if st.button("🔄 Reset Bins"):
        st.session_state.biomedical_level = 0
        st.session_state.general_level = 0
        st.session_state.bin_graphics.draw_bin(0, 0)
        bin_display.image(st.session_state.bin_graphics.surface_to_image())
        st.success("Bins emptied successfully!")
        st.rerun()

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: #666;'>© 2025 TrashLink. All rights reserved.</p>", unsafe_allow_html=True)