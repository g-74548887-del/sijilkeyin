# app.py
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
import base64

st.set_page_config(page_title="Generator Sijil Automatik", layout="wide")

# -------------------------
# Background Tapak (GitHub / URL)
# -------------------------
background_url = "https://raw.githubusercontent.com/username/repo/main/background.jpg"  # ganti URL sebenar
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("{background_url}");
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
    }}
    .center-button button {{
        display:block;
        margin: 10px auto;
        font-weight:bold;
        padding:10px 20px;
        background:#0b5ed7;
        color:white;
        border-radius:8px;
        border:none;
    }}
    .small-download button {{
        padding:5px 10px;
        font-size:12px;
        margin:3px;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------
# Tajuk Utama
# -------------------------
st.markdown("""
<h1 style='color:#0b5ed7; text-align:center;'>Generator Sijil Automatik</h1>
<p style='text-align:center;'>Masukkan nama & IC murid, sistem akan jana sijil PNG & PDF siap print.</p>
""", unsafe_allow_html=True)

# -------------------------
# Session State untuk Murid
# -------------------------
if "rows" not in st.session_state:
    st.session_state.rows = [{"nama": "", "ic": ""}]

# -------------------------
# Tambah / Buang Murid
# -------------------------
st.subheader("Senarai Murid")
remove_idx = None
for idx, row in enumerate(st.session_state.rows):
    cols = st.columns([4,4,2])
    nama = cols[0].text_input(f"Nama Murid {idx+1}", value=row["nama"], key=f"nama_{idx}")
    ic = cols[1].text_input(f"IC Murid {idx+1}", value=row["ic"], key=f"ic_{idx}")
    if cols[2].button("Buang", key=f"remove_{idx}"):
        remove_idx = idx

if remove_idx is not None:
    st.session_state.rows.pop(remove_idx)

if st.button("Tambah Nama Murid"):
    st.session_state.rows.append({"nama":"","ic":""})

# -------------------------
# Fungsi Generate PNG & PDF
# -------------------------
def generate_certificate_png(name, ic):
    W, H = 1600,1200
    bg = Image.new("RGBA",(W,H),(255,255,255,255))  # latar sijil putih
    draw = ImageDraw.Draw(bg)
    draw.rectangle([(40,40),(W-40,H-40)], outline=(11,94,215), width=12)
    try:
        title_font = ImageFont.truetype("DejaVuSans-Bold.ttf",48)
    except:
        title_font = ImageFont.load_default()
    draw.text((W//2,140),"SIJIL PENGHARGAAN", fill=(11,94,215), font=title_font, anchor="mm")
    try:
        pil_font = ImageFont.load_default()
    except:
        pil_font = ImageFont.load_default()
    draw.text((W//2,H*0.45),name,font=pil_font,anchor="mm",fill=(0,0,0))
    small_font = ImageFont.load_default()
    draw.text((W//2,H*0.55),f"IC: {ic}",font=small_font,anchor="mm",fill=(30,30,30))
    img_bytes = io.BytesIO()
    bg.convert("RGB").save(img_bytes,format="PNG")
    img_bytes.seek(0)
    return img_bytes

def generate_certificate_pdf(img_bytes):
    img_bytes.seek(0)
    c = canvas.Canvas("temp.pdf", pagesize=A4)
    width, height = A4
    img = Image.open(img_bytes)
    aspect = img.width / img.height
    new_width = width - 100
    new_height = new_width / aspect
    c.drawImage(ImageReader(img),50,(height-new_height)/2,width=new_width,height=new_height)
    pdf_bytes = io.BytesIO()
    c.save()
    with open("temp.pdf","rb") as f:
        pdf_bytes.write(f.read())
    pdf_bytes.seek(0)
    return pdf_bytes

# -------------------------
# Generate & Print
# -------------------------
st.markdown("<h2 style='color:#0b5ed7;'>Jana Sijil</h2>", unsafe_allow_html=True)

# Butang Generate tengah & bold
if st.button("Generate Sijil PNG & PDF", key="generate", help="Klik untuk jana semua sijil"):
    for idx,row in enumerate(st.session_state.rows):
        name = st.session_state[f"nama_{idx}"]
        ic = st.session_state[f"ic_{idx}"]
        png_bytes = generate_certificate_png(name,ic)
        pdf_bytes = generate_certificate_pdf(png_bytes)
        st.image(png_bytes,use_column_width=True)
        # Download kecil
        st.markdown('<div class="small-download">', unsafe_allow_html=True)
        st.download_button(f"PNG {name}", png_bytes, f"Sijil_{name}.png","image/png")
        st.download_button(f"PDF {name}", pdf_bytes, f"Sijil_{name}.pdf","application/pdf")
        st.markdown('</div>', unsafe_allow_html=True)
        # Print PNG button
        st.markdown(f"""
        <button onclick="window.open('{base64.b64encode(png_bytes.getvalue()).decode()}')" 
        style="padding:5px 10px;margin-top:5px;background:#198754;color:white;border-radius:8px;border:none;">
        Print {name}
        </button>
        """,unsafe_allow_html=True)
        st.markdown("---")

# -------------------------
# Ayat comel bawah
# -------------------------
st.markdown("""
<p style='text-align:center; font-size:16px; color:#0b5ed7; margin-top:20px;'>
Inovasi sijil automatik ini dibangunkan oleh Jiha, Syidha, Sumayah & Aisy
</p>
""", unsafe_allow_html=True)
