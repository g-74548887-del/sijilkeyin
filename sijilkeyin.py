# app.py
import streamlit as st
from docx import Document
from PIL import Image, ImageDraw, ImageFont
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
import base64

st.set_page_config(page_title="Generator Sijil Automatik", layout="wide")

# -------------------------
# Gaya & Tajuk
# -------------------------
st.markdown("""
<h1 style='color:#0b5ed7; text-align:center;'>Generator Sijil Automatik</h1>
<p style='text-align:center;'>Masukkan nama & IC murid, muat naik template Word & background imej. Sistem akan jana sijil PNG & PDF siap print.</p>
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
# Upload Template & Background
# -------------------------
st.subheader("Muat Naik Template Word (.docx)")
template_file = st.file_uploader("Upload fail .docx (placeholder {NAMA} & {IC})", type=["docx"])

st.markdown("""
<div style="border:2px solid #0b5ed7;background-color:#eef5ff;padding:12px;border-radius:10px;">
<b style='color:#0b5ed7;'>Nota:</b> Pastikan template Word mengandungi placeholder <code>{NAMA}</code> & <code>{IC}</code>.<br>
Contoh:
<code>Disampaikan kepada<br>{NAMA}<br>No. Kad Pengenalan: {IC}</code>
</div>
""", unsafe_allow_html=True)

st.subheader("Muat Naik Background Imej (Pilihan)")
bg_file = st.file_uploader("Upload imej PNG/JPG", type=["png","jpg","jpeg"])

# -------------------------
# Preview Template
# -------------------------
if template_file:
    doc = Document(template_file)
    preview_text = "\n".join([p.text.replace("{NAMA}","Contoh Nama").replace("{IC}","001122-01-1234") for p in doc.paragraphs])
    st.text_area("Preview Template", preview_text, height=200)

# -------------------------
# Pilihan Font
# -------------------------
st.subheader("Pilihan Font untuk PNG")
font_name = st.selectbox("Font", ["DejaVuSans-Bold.ttf","Arial.ttf"])
font_size = st.slider("Saiz Nama (px)", 30,160,72)

# -------------------------
# Fungsi Generate PNG & PDF
# -------------------------
def generate_certificate_png(name, ic, bg_file=None):
    W, H = 1600,1200
    if bg_file:
        bg_file.seek(0)
        bg = Image.open(bg_file).convert("RGBA")
    else:
        bg = Image.new("RGBA",(W,H),(255,255,255,255))
        draw = ImageDraw.Draw(bg)
        draw.rectangle([(40,40),(W-40,H-40)], outline=(11,94,215), width=12)
        try:
            title_font = ImageFont.truetype("DejaVuSans-Bold.ttf",48)
        except:
            title_font = ImageFont.load_default()
        draw.text((W//2,140),"SIJIL PENGHARGAAN", fill=(11,94,215), font=title_font, anchor="mm")
    draw = ImageDraw.Draw(bg)
    try:
        pil_font = ImageFont.truetype(font_name,font_size)
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

if st.button("Generate Sijil PNG & PDF"):
    for idx,row in enumerate(st.session_state.rows):
        name = st.session_state[f"nama_{idx}"]
        ic = st.session_state[f"ic_{idx}"]
        png_bytes = generate_certificate_png(name,ic,bg_file)
        pdf_bytes = generate_certificate_pdf(png_bytes)
        st.image(png_bytes,use_column_width=True)
        st.download_button(f"Muat Turun PNG {name}", png_bytes, f"Sijil_{name}.png","image/png")
        st.download_button(f"Muat Turun PDF {name}", pdf_bytes, f"Sijil_{name}.pdf","application/pdf")
        # Print button PNG
        st.markdown(f"""
        <button onclick="window.open('{base64.b64encode(png_bytes.getvalue()).decode()}')" 
        style="padding:8px 20px;margin-top:5px;background:#198754;color:white;border-radius:8px;border:none;">
        Print {name}
        </button>
        """,unsafe_allow_html=True)
        st.markdown("---")

# -------------------------
# Pembangunan Inovasi + Guru
# -------------------------
st.markdown("<h3 style='color:#0b5ed7;'>Pembangunan Inovasi Berkumpulan</h3>", unsafe_allow_html=True)
default_names = "Narjihah binti Mohd Hashim\nSyidha\nSumayah\nAisy"
guru_input = st.text_area("Senarai Nama Guru Terlibat",default_names,height=120)
st.markdown(
    f"<div style='background:#eef5ff;padding:10px;border-radius:8px;border:1px solid #cddfff;'>"
    f"<b>Senarai Guru:</b><br>{guru_input.replace(chr(10),'<br>')}"
    f"</div>",unsafe_allow_html=True
)
