import streamlit as st
import math
import base64
import pandas as pd
import plotly.express as px

# -----------------------------------------------------------------------------
# Set Page Config First
# -----------------------------------------------------------------------------
st.set_page_config(page_title="AI Carbon Footprint Estimator", layout="wide")

# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------
CO2_INTENSITY_GLOBAL = 475  # g CO₂/kWh (global average IEA)

ENERGY_FACTORS = {
    "Text": 0.5,   # Wh per token
    "Image": 5.0,     # Wh per image
    "Video": 14.375   # Wh per second of video
}

# -----------------------------------------------------------------------------
# Sidebar – Location Selection
# -----------------------------------------------------------------------------
st.sidebar.header("🛠️ Advanced Configuration")

eu_countries = [
    "🇦🇹 Austria", "🇧🇪 Belgium", "🇧🇬 Bulgaria", "🇭🇷 Croatia", "🇨🇾 Cyprus", "🇨🇿 Czech Republic",
    "🇩🇰 Denmark", "🇪🇪 Estonia", "🇫🇮 Finland", "🇫🇷 France", "🇩🇪 Germany", "🇬🇷 Greece",
    "🇭🇺 Hungary", "🇮🇪 Ireland", "🇮🇹 Italy", "🇱🇻 Latvia", "🇱🇹 Lithuania", "🇱🇺 Luxembourg",
    "🇲🇹 Malta", "🇳🇱 Netherlands", "🇵🇱 Poland", "🇵🇹 Portugal", "🇷🇴 Romania", "🇸🇰 Slovakia",
    "🇸🇮 Slovenia", "🇪🇸 Spain", "🇸🇪 Sweden"
]

# Country icon → name 매핑
country_icon = {country: country.split(" ", 1)[1] for country in eu_countries}

# 모든 국가에 기본 intensity 0 지정
default_intensity = {country: 366 for country in country_icon.values()}

# 선택 박스
selected_country = st.sidebar.selectbox("Select Location", list(country_icon.keys()))
country_name = country_icon[selected_country]
co2_default = default_intensity.get(country_name, CO2_INTENSITY_GLOBAL)

st.sidebar.markdown(
    "<small><strong>Why does location matter?</strong></small><br><small>Every country has different energy sources and CO₂ intensity.</small>",
    unsafe_allow_html=True
)

manual_override = st.sidebar.checkbox("Enter CO₂ intensity manually (g CO₂/kWh)")
if manual_override:
    CO2_INTENSITY = st.sidebar.number_input(
        "Enter custom CO₂ intensity (g CO₂/kWh)", min_value=0.0, value=float(co2_default)
    )
else:
    CO2_INTENSITY = co2_default

# -----------------------------------------------------------------------------
# Main Title & Description
# -----------------------------------------------------------------------------
st.title("AI carbon footprint calculator")

st.header("Using AI has a carbon footprint.")
st.markdown("""
Many people use AI as part of their daily lives.  
It brings convenience, but with that convenience comes carbon emissions.  
This tool estimates the **carbon emissions** that will be generated from your AI tasks:
- 📝 Text generation (ChatGPT)
- 🎨 Image generation (DALL·E)
- 🎞️ Video generation (Sora)
""")

st.markdown("""
The calculation method used in this tool is adapted from the [Berthelot et al. (2024)](https://doi.org/10.1016/j.procir.2024.01.098).
""")

# -----------------------------------------------------------------------------
# Section 2: Prompt Input
# -----------------------------------------------------------------------------
st.header("2. Select Content Type")

workload_type = st.radio(
    "What kind of AI task are you running?",
    ["Text", "Image", "Video"],
    horizontal=True
)

with st.form("input_form"):
    st.header("3. Enter Prompt Details")

    st.markdown(f"🧠 **Selected Task: {workload_type} Generation**")

    col_input1, col_input2 = st.columns(2)
    with col_input1:
        model_name = st.selectbox("Model Used", ["GPT-3.5", "GPT-4", "Other"])

    if workload_type == "Text":
        prompt = st.text_area("Enter your text prompt:", height=200)
        units = max(1, int(len(prompt.split()) * 1.3)) if prompt else 0
    elif workload_type == "Image":
        prompt = st.text_area("Describe the image you want to generate:", height=200)
        units = st.number_input("Number of images to generate:", min_value=1, step=1)
    elif workload_type == "Video":
        prompt = st.text_area("Describe the video content:", height=200)
        units = st.number_input("Video duration (seconds):", min_value=1, step=1)
    else:
        prompt = ""
        units = 0

    submit = st.form_submit_button("📊 Estimate Impact")

# -----------------------------------------------------------------------------
# Section 3: Impact Visualization
# -----------------------------------------------------------------------------
if units > 0 and submit:
    energy_wh = units * ENERGY_FACTORS[workload_type]
    energy_kwh = energy_wh / 1000
    emissions_g = energy_kwh * CO2_INTENSITY

    st.header("Impact Visualization")

    comparison_df = pd.DataFrame({
        "Activity": ["Your Task", "Google search (1 query)", "LED bulb (1 hour)"],
        "g CO₂-eq": [emissions_g, 0.05, 15]
    })

    colors = {
        "Your Task": "#F31111",
        "Google search (1 query)": "#4285F4",
        "LED bulb (1 hour)": "#FFD700"
    }

    fig = px.bar(
        comparison_df,
        x="Activity",
        y="g CO₂-eq",
        color="Activity",
        color_discrete_map=colors,
        category_orders={
            "Activity": [
                "Your Task",
                "Google search (1 query)",
                "LED bulb (1 hour)"
            ]
        },
        labels={
            "g CO₂-eq": "Emissions (g CO₂-eq)",
            "Activity": ""
        },
        height=600,
        text="g CO₂-eq"
    )

    fig.update_traces(
        texttemplate="%{text:.2f}",
        textposition="outside",
    )

    fig.update_layout(
        font=dict(size=18),
        xaxis=dict(
            tickfont=dict(size=16),
            title_font=dict(size=18)
        ),
        yaxis=dict(
            tickfont=dict(size=16),
            title_font=dict(size=18),
            gridcolor="rgba(0,0,0,0.1)"
        ),
        legend=dict(font=dict(size=16)),
        bargap=0.35,
        template="simple_white"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"**Estimated Emissions:** {emissions_g:.2f} g CO₂-eq")

    co2_kg = emissions_g / 1000
    m_driven = co2_kg * 4042
    coal_burned = co2_kg * 500
    google_search_equiv = emissions_g / 0.05
    led_bulb_equiv = emissions_g / 15

    st.markdown(f"- 🔍 Equivalent to **{google_search_equiv:.0f} Google searches**")
    st.markdown(f"- 💡 Equivalent to using an LED bulb for **{led_bulb_equiv:.1f} hours**")
    st.markdown(f"- 🚗 Equivalent to driving **{m_driven:.2f} m** with an average ICE car")
    st.markdown(f"- 🏭 Burning approximately **{coal_burned:.2f} g** of coal")

# -----------------------------------------------------------------------------
# Call-to-Action Section
# -----------------------------------------------------------------------------
st.header("Take action for a Sustainable AI")

st.info("""
###  **Do this 1**  
🔗 Follow our community: [Our LinkedIn Community](https://sustainable-energy-week.ec.europa.eu/index_en)
""")

st.info("""
### **Do this 2**  
💚 Support this project: [Support Page](https://sustainable-energy-week.ec.europa.eu/index_en)
""")

# -----------------------------------------------------------------------------
# Notes Section
# -----------------------------------------------------------------------------
st.markdown("""
---
### Notes
- Coefficients are based on published benchmarks and subject to change.
- All values are indicative and reflect average energy intensity by country.
- This app is intended for awareness, not official carbon reporting.
""")
