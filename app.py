import os
import io
import base64
import requests
import streamlit as st
from PIL import Image

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="AI Prompt Detailer",
    page_icon="🔍",
    layout="centered"
)

# Custom Styling (Dark Green Theme)
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

# Ambil API key dari Secrets
api_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", ""))
api_key = str(api_key).strip().strip('"').strip("'")

st.subheader("Analisis Gambar Detail")
st.write("Unggah gambar untuk mendapatkan deskripsi prompt super detail yang siap disalin.")

uploaded_file = st.file_uploader(
    "Klik, Drag & Drop, atau Paste Gambar", 
    type=["jpg", "jpeg", "png", "webp"]
)

if "extracted_prompt" not in st.session_state:
    st.session_state.extracted_prompt = ""

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, caption="Gambar yang diunggah", use_container_width=True)
    
    if st.button("Generate Prompt Detail"):
        if not api_key:
            st.error("GEMINI_API_KEY belum terpasang di Secrets.")
        else:
            with st.spinner("Menganalisis gambar dan mengekstrak prompt..."):
                try:
                    # Konversi gambar ke base64
                    buffered = io.BytesIO()
                    img_format = img.format if img.format else "JPEG"
                    img.save(buffered, format=img_format)
                    img_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
                    mime_type = uploaded_file.type or "image/jpeg"

                    system_instruction = (
                        "Bertindaklah sebagai AI Prompt Engineer profesional. Analisis gambar ini dan buatkan prompt pembuatan gambar AI yang sangat mendalam dan terperinci. "
                        "Jelaskan secara runtut: "
                        "1. Subjek & Pose: Jumlah orang, posisi tubuh, ekspresi wajah, arah pandangan, interaksi. "
                        "2. Pakaian & Tekstur: Model pakaian, detail bahan kain, warna spesifik, aksesoris. "
                        "3. Latar Belakang & Suasana: Ruangan, interior/eksterior, dekorasi di sekitar. "
                        "4. Pencahayaan & Kamera: Arah datangnya cahaya alami/buatan, soft shadows, kontras sinematik, sudut pengambilan gambar. "
                        "Format output: Buat dalam 1 atau 2 paragraf deskriptif padat dalam Bahasa Indonesia yang langsung siap di-copy."
                    )

                    # Endpoint REST API Gemini
                    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
                    
                    # Header autentikasi resmi untuk format kunci baru AQ. dan AIza
                    headers = {
                        "Content-Type": "application/json",
                        "x-goog-api-key": api_key
                    }

                    payload = {
                        "contents": [
                            {
                                "parts": [
                                    {"text": system_instruction},
                                    {
                                        "inline_data": {
                                            "mime_type": mime_type,
                                            "data": img_b64
                                        }
                                    }
                                ]
                            }
                        ]
                    }

                    response = requests.post(url, headers=headers, json=payload)
                    res_json = response.json()

                    if response.status_code == 200:
                        prompt_text = res_json["candidates"][0]["content"]["parts"][0]["text"]
                        st.session_state.extracted_prompt = prompt_text
                        st.success("Prompt berhasil digenerate!")
                    else:
                        error_msg = res_json.get("error", {}).get("message", response.text)
                        st.error(f"Gagal generate prompt: {error_msg}")

                except Exception as e:
                    st.error(f"Terjadi kesalahan: {e}")

if st.session_state.extracted_prompt:
    st.write("---")
    st.subheader("Hasil Prompt:")
    st.text_area(
        label="Salin teks di bawah ini:",
        value=st.session_state.extracted_prompt,
        height=220
    )
