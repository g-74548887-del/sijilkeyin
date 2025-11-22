import streamlit as st
import pandas as pd
import io
import zipfile
from PIL import Image
import fitz  # PyMuPDF
from docx import Document

st.set_page_config(page_title="Jana Sijil Automatik", layout="wide")

# ================== CSS ==================
st.markdown("""
<style>
:root { --text-color: black; }
@media (prefers-color-scheme: dark) { :root { --text-color: white; } }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='color:var(--text-color); text-align:center;'>Jana Sijil Automatik</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:var(--text-color);'>Masukkan nama & IC murid, sistem akan jana sijil ikut template Word.</p>", unsafe_allow_html=True)

# ================== Session State ==================
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=["Nama", "IC"])
if "generated" not in st.session_state:
    st.session_state.generated = False

# ================== Table Input ==================
st.subheader("Senarai Nama Murid")
edited_df = st.data_editor(
    st.session_state.df,
    use_container_width=True,
    num_rows="dynamic"
)
st.session_state.df = edited_df

if st.button("Tambah Nama"):
    st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([{"Nama":"","IC":""}])], ignore_index=True)

# ================== Upload Template ==================
st.subheader("Template Sijil (.docx)")
template_file = st.file_uploader("Muat naik template sijil Word (.docx)", type=["docx"])
st.markdown("""
<div style="border:2px solid #0b5ed7;background-color:#eef5ff;padding:12px;border-radius:10px; color:var(--text-color);">
<b style='color:#0b5ed7;'>Nota Penting:</b><br>
Template mesti mengandungi placeholder:<br>
<code>{NAMA}</code> & <code>{IC}</code>
</div>
""", unsafe_allow_html=True)

# ================== Fungsi ==================
def generate_docx(template_bytes, name, ic):
    doc = Document(io.BytesIO(template_bytes))
    for p in doc.paragraphs:
        if "{NAMA}" in p.text:
            p.text = p.text.replace("{NAMA}", name)
        if "{IC}" in p.text:
            p.text = p.text.replace("{IC}", ic)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                if "{NAMA}" in cell.text:
                    cell.text = cell.text.replace("{NAMA}", name)
                if "{IC}" in cell.text:
                    cell.text = cell.text.replace("{IC}", ic)
    output = io.BytesIO()
    doc.save(output)
    output.seek(0)
    return output

def docx_to_pdf_bytes(docx_bytes):
    # Generate PDF from Word in-memory using fitz: Word -> temp PDF -> fitz
    # Trick: Save docx as temp, read in fitz as pdf not possible directly, so generate PNG from docx first
    # Simpler: Generate PNG by converting each page to image using python-docx & PIL (simple placeholder replacement)
    # For now, just convert first page text to image
    doc = Document(io.BytesIO(docx_bytes.read()))
    # Create white canvas
    img = Image.new("RGB",(1240,1754),"white")
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf",48)
    except:
        font = ImageFont.load_default()
    y = 200
    for p in doc.paragraphs:
        draw.text((620,y), p.text, anchor="mm", fill=(0,0,0), font=font)
        y += 100
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)
    return img_bytes

# ================== Jana Sijil ==================
if template_file and st.button("Jana Sijil"):
    st.session_state.generated = True
    st.session_state.template_bytes = template_file.read()

# ================== Senarai Hasil ==================
if st.session_state.generated:
    st.subheader("Senarai Sijil Murid")
    for idx, row in st.session_state.df.iterrows():
        name = row["Nama"]
        ic = row["IC"]
        cols = st.columns([4,1])
        cols[0].markdown(f"<b>{name}</b>", unsafe_allow_html=True)
        if cols[1].button("Word & PNG", key=f"word_{idx}"):
            docx_bytes = generate_docx(st.session_state.template_bytes, name, ic)
            png_bytes = docx_to_pdf_bytes(io.BytesIO(docx_bytes.getvalue()))
            # Download Word
            cols[1].download_button(f"Muat Turun Word", docx_bytes, f"Sijil_{name}.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            # Download PNG
            cols[1].download_button(f"Muat Turun PNG", png_bytes, f"Sijil_{name}.png", "image/png")

    # ================== Download All ==================
    st.markdown("---")
    st.subheader("Download Semua Sijil Sekali (Word + PNG)")

    if st.button("Download All Word & PNG"):
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf,"w") as zipf:
            for idx, row in st.session_state.df.iterrows():
                name = row["Nama"]
                ic = row["IC"]
                docx_bytes = generate_docx(st.session_state.template_bytes, name, ic)
                png_bytes = docx_to_pdf_bytes(io.BytesIO(docx_bytes.getvalue()))
                zipf.writestr(f"Sijil_{name}.docx", docx_bytes.getvalue())
                zipf.writestr(f"Sijil_{name}.png", png_bytes.getvalue())
        zip_buf.seek(0)
        st.download_button("Muat Turun Semua Word & PNG", zip_buf, "Sijil_All.zip", "application/zip")

# ================== Footer ==================
st.markdown("""
<p style='text-align:center; font-size:16px; color:#0b5ed7; margin-top:20px;'>
<b>Inovasi Sijil Automatik</b><br><br>
Dibangunkan oleh Narjihah binti Mohd Hashim, Mohamad Adham bin Abdul Malek, 
Nor Aqilah binti Aliasam, Muhammad Amin bin Muhammad Puzi, 
Siti Nur Amira bt. Abdul Talib untuk mempercepatkan proses 
penerbitan sijil secara digital.
</p>
""", unsafe_allow_html=True)
