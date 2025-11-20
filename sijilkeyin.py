# app.py
import streamlit as st
from docx import Document
from PIL import Image, ImageDraw, ImageFont
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader

st.set_page_config(page_title="Jana Sijil Automatik", layout="wide")

# -------------------------
# Tajuk Utama
# -------------------------
st.markdown("<h1 style='color:#0b5ed7; text-align:center;'>Jana Sijil Automatik</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Masukkan nama & IC murid, sistem akan jana sijil PNG & PDF berdasarkan template Word.</p>", unsafe_allow_html=True)

# -------------------------
# Upload Template Word
# -------------------------
st.subheader("Muat Naik Template Word (.docx)")
template_file = st.file_uploader("Upload fail .docx (placeholder {NAMA} & {IC})", type=["docx"])

st.markdown("""
<div style="border:2px solid #0b5ed7;background-color:#eef5ff;padding:12px;border-radius:10px;">
<b style='color:#0b5ed7;'>Nota Penting:</b><br>
Template Word mesti mengandungi placeholder:<br>
<code>{NAMA}</code> & <code>{IC}</code>
</div>
""", unsafe_allow_html=True)

# -------------------------
# Session state
# -------------------------
if "rows" not in st.session_state:
    st.session_state.rows = [{"nama": "", "ic": ""}]
if "input_done" not in st.session_state:
    st.session_state.input_done = False
if "generated" not in st.session_state:
    st.session_state.generated = False

# -------------------------
# Input Nama & IC Murid
# -------------------------
if not st.session_state.input_done:
    st.subheader("Masukkan Nama & IC Murid")
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

    if st.button("Selesai Masukkan Nama & IC"):
        st.session_state.input_done = True

# -------------------------
# Fungsi Generate PNG & PDF
# -------------------------
def generate_certificate_png(name, ic):
    W,H = 1600,1200
    bg = Image.new("RGBA",(W,H),(255,255,255,255))
    draw = ImageDraw.Draw(bg)
    draw.rectangle([(40,40),(W-40,H-40)], outline=(11,94,215), width=12)
    try:
        title_font = ImageFont.truetype("DejaVuSans-Bold.ttf",48)
    except:
        title_font = ImageFont.load_default()
    draw.text((W//2,140),"SIJIL PENGHARGAAN", fill=(11,94,215), font=title_font, anchor="mm")
    pil_font = ImageFont.load_default()
    draw.text((W//2,H*0.45),name,font=pil_font,anchor="mm",fill=(0,0,0))
    draw.text((W//2,H*0.55),f"IC: {ic}",font=pil_font,anchor="mm",fill=(30,30,30))
    img_bytes = io.BytesIO()
    bg.convert("RGB").save(img_bytes,format="PNG")
    img_bytes.seek(0)
    return img_bytes

def generate_certificate_pdf(img_bytes):
    img_bytes.seek(0)
    c = canvas.Canvas("temp.pdf", pagesize=A4)
    width,height = A4
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
# Button Generate Sijil tunggal
# -------------------------
if st.session_state.input_done and template_file:
    if st.button("Jana Sijil Automatik"):
        st.session_state.generated = True

# -------------------------
# Senarai Nama Murid + Button PNG/PDF (KeyError diperbetul)
# -------------------------
if st.session_state.generated:
    st.subheader("Senarai Sijil Murid")
    for idx, row in enumerate(st.session_state.rows):
        name = row["nama"]
        ic = row["ic"]
        cols = st.columns([4,1,1])
        cols[0].markdown(f"**{name}**")
        # PNG button
        if cols[1].button("PNG", key=f"png_{idx}"):
            img_bytes = generate_certificate_png(name, ic)
            st.image(img_bytes,use_column_width=True)
        # PDF button
        if cols[2].button("PDF", key=f"pdf_{idx}"):
            img_bytes = generate_certificate_png(name, ic)
            pdf_bytes = generate_certificate_pdf(img_bytes)
            st.download_button(f"Muat Turun PDF {name}", pdf_bytes, f"Sijil_{name}.pdf","application/pdf")

# -------------------------
# Ayat Profesional Bawah
# -------------------------
st.markdown("""
<p style='text-align:center; font-size:16px; color:#0b5ed7; margin-top:20px;'>
Inovasi Sijil Automatik: Hasil ciptaan Jiha, Syidha, Sumayah & Aisy untuk mempercepatkan proses penerbitan sijil secara digital.
</p>
""", unsafe_allow_html=True)
