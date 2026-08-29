import os
import streamlit as st
from PIL import Image
import google.generativeai as genai

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="AI Prompt Detailer",
    page_icon="🔍",
    layout="centered"
)

# Custom Styling (Dark Green Theme mirip video)
st.markdown("""
    <style>
    .stApp {
        background-color: #0d1912;
        color: #e5e7eb;
    }
    .stButton>button {
        background-color: #15803d;
        color: white;
        border-radius: 8px;
        border: 1px solid #16a34a;
        width: 100%;
        padding: 12px;
        font-weight: 700;
        font-size: 16px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #16a34a;
        color: #ffffff;
        border-color: #22c55e;
    }
    div[data-testid="stFileUploader"] {
        border: 2px dashed #16a34a;
        border-radius: 10px;
        padding: 10px;
        background-color: #0b140f;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Generator Prompt by AI")
st.caption("THE ULTIMATE AI DETAILER & PROMPT GENERATOR")

# Ambil API Key otomatis dari Streamlit Secrets atau OS Environment
api_key = None
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
elif "GEMINI_API_KEY" in os.environ:
    api_key = os.environ["GEMINI_API_KEY"]

st.subheader("Analisis Gambar Detail")
st.write("Unggah gambar untuk mendapatkan deskripsi prompt super detail yang siap disalin.")

# File Uploader
uploaded_file = st.file_uploader(
    "Klik, Drag & Drop, atau Paste Gambar", 
    type=["jpg", "jpeg", "png", "webp"]
)

# State untuk menyimpan hasil prompt
if "extracted_prompt" not in st.session_state:
    st.session_state.extracted_prompt = ""

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, caption="Gambar yang diunggah", use_container_width=True)
    
    if st.button("Generate Prompt Detail"):
        if not api_key:
            st.error("GEMINI_API_KEY tidak ditemukan di environment/secrets.")
        else:
            with st.spinner("Menganalisis gambar dan mengekstrak prompt..."):
                try:
                    # Bersihkan spasi/whitespace dari API key
                    clean_key = str(api_key).strip()
                    genai.configure(api_key=clean_key)
                    
                    model = genai.GenerativeModel("gemini-1.5-flash")
                    
                    system_instruction = (
                        "Bertindaklah sebagai AI Prompt Engineer profesional. Analisis gambar ini dan buatkan prompt pembuatan gambar AI yang sangat mendalam dan terperinci. "
                        "Jelaskan secara runtut: "
                        "1. Subjek & Pose: Jumlah orang, posisi tubuh, ekspresi wajah, arah pandangan, interaksi. "
                        "2. Pakaian & Tekstur: Model pakaian, detail bahan kain, warna spesifik, aksesoris. "
                        "3. Latar Belakang & Suasana: Ruangan, interior/eksterior, dekorasi di sekitar. "
                        "4. Pencahayaan & Kamera: Arah datangnya cahaya alami/buatan, soft shadows, kontras sinematik, sudut pengambilan gambar. "
                        "Format output: Buat dalam 1 atau 2 paragraf deskriptif padat dalam Bahasa Indonesia yang langsung siap di-copy."
                    )
                    
                    response = model.generate_content([system_instruction, img])
                    
                    st.session_state.extracted_prompt = response.text
                    st.success("Prompt berhasil digenerate!")
                except Exception as e:
                    st.error(f"Terjadi kesalahan: {e}")

# Tampilan Hasil Prompt
if st.session_state.extracted_prompt:
    st.write("---")
    st.subheader("Hasil Prompt:")
    st.text_area(
        label="Salin teks di bawah ini:",
        value=st.session_state.extracted_prompt,
        height=220
    )
