# app.py
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader

st.set_page_config(page_title="Jana Sijil Automatik", layout="wide")

# ======================================================
# CSS untuk Dark Mode / Light Mode Auto Text Color
# ======================================================
st.markdown("""
<style>
:root {
  --text-color: black;
}

@media (prefers-color-scheme: dark) {
  :root {
    --text-color: white;
  }
}
</style>
""", unsafe_allow_html=True)

# ======================================================
# Tajuk Utama
# ======================================================
st.markdown("<h1 style='color:var(--text-color); text-align:center;'>Jana Sijil Automatik</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:var(--text-color);'>Masukkan nama & IC murid, sistem akan jana sijil PNG & PDF.</p>", unsafe_allow_html=True)

# ======================================================
# Upload Template Sijil
# ======================================================
st.subheader("Template Sijil (.docx / .pdf)")

template_file = st.file_uploader("Muat naik template sijil", type=["docx", "pdf"])

st.markdown("""
<div style="border:2px solid #0b5ed7;background-color:#eef5ff;padding:12px;border-radius:10px; color:var(--text-color);">
<b style='color:#0b5ed7;'>Nota Penting:</b><br>
Template mesti mengandungi placeholder:<br>
<code>{NAMA}</code> & <code>{IC}</code>
</div>
""", unsafe_allow_html=True)

# ======================================================
# Session States
# ======================================================
if "rows" not in st.session_state:
    st.session_state.rows = []
if "input_done" not in st.session_state:
    st.session_state.input_done = False
if "generated" not in st.session_state:
    st.session_state.generated = False

# ======================================================
# Fungsi Generate PNG / PDF
# ======================================================
def generate_certificate_png(name, ic):
    W,H = 1240,1754
    bg = Image.new("RGBA",(W,H),(255,255,255,255))
    draw = ImageDraw.Draw(bg)

    draw.rectangle([(40,40),(W-40,H-40)], outline=(11,94,215), width=12)

    try:
        title_font = ImageFont.truetype("DejaVuSans-Bold.ttf",48)
    except:
        title_font = ImageFont.load_default()
    draw.text((W//2,140),"SIJIL PENGHARGAAN", fill=(11,94,215), font=title_font, anchor="mm")

    pil_font = ImageFont.load_default()
    draw.text((W//2,H*0.45), name, font=pil_font, anchor="mm", fill=(0,0,0))
    draw.text((W//2,H*0.55), ic, font=pil_font, anchor="mm", fill=(30,30,30))

    img_bytes = io.BytesIO()
    bg.convert("RGB").save(img_bytes, format="PNG")
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

# ======================================================
# Input Nama + IC dalam bentuk table
# ======================================================
if not st.session_state.input_done:
    st.subheader("Senarai Nama Murid (copy & paste)")

    text_data = st.text_area(
        "Format: Nama | IC",
        placeholder="Contoh:\nAli bin Abu | 010101105577\nSiti Aminah | 020202045566",
        height=200
    )

    if st.button("Selesai Masukkan Nama & IC"):
        rows = []
        for line in text_data.split("\n"):
            if "|" in line:
                name, ic = line.split("|")
                rows.append({"nama": name.strip(), "ic": ic.strip()})

        st.session_state.rows = rows
        st.session_state.input_done = True

# ======================================================
# Button Jana Sijil
# ======================================================
if st.session_state.input_done and template_file:
    if st.button("Jana Sijil Automatik"):
        st.session_state.generated = True

# ======================================================
# Senarai hasil + butang download
# ======================================================
if st.session_state.generated:
    st.subheader("Senarai Sijil Murid")

    for idx, row in enumerate(st.session_state.rows):
        name = row["nama"]
        ic = row["ic"]
        
        cols = st.columns([4,1,1])
        cols[0].markdown(f"<p style='color:var(--text-color); font-size:18px;'><b>{name}</b></p>", unsafe_allow_html=True)

        if cols[1].button("PNG", key=f"png_{idx}"):
            img_bytes = generate_certificate_png(name, ic)
            st.image(img_bytes)

        if cols[2].button("PDF", key=f"pdf_{idx}"):
            img_bytes = generate_certificate_png(name, ic)
            pdf_bytes = generate_certificate_pdf(img_bytes)
            st.download_button(f"Muat Turun PDF {name}", pdf_bytes, f"Sijil_{name}.pdf")

    if st.button("Tambah Nama Lagi"):
        st.session_state.input_done = False
        st.session_state.generated = False

# ======================================================
# Footer
# ======================================================
# Ayat Profesional Bawah
st.markdown("""
<p style='text-align:center; font-size:16px; color:#0b5ed7; margin-top:20px;'>
<b>Inovasi Sijil Automatik</b><br><br>
Hasil ciptaan Narjihah binti Mohd Hashim, Mohamad Adham bin Abdul Malek, 
Nor Aqilah binti Aliasam, Muhammad Amin bin Muhammad Puzi, 
Siti Nur Amira bt. Abdul Talib untuk mempercepatkan proses 
penerbitan sijil secara digital.
</p>
""", unsafe_allow_html=True)