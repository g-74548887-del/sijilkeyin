import streamlit as st
import pandas as pd
import io
import zipfile
import tempfile
import os
from PIL import Image
import fitz  # pip install pymupdf

# Jika guna Word template
from docx import Document
from docx2pdf import convert

st.set_page_config(page_title="Jana Sijil Automatik", layout="wide")

# ================== CSS ==================
st.markdown("""
<style>
:root { --text-color: black; }
@media (prefers-color-scheme: dark) { :root { --text-color: white; } }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='color:var(--text-color); text-align:center;'>Jana Sijil Automatik</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:var(--text-color);'>Masukkan nama & IC murid, sistem akan jana sijil ikut template.</p>", unsafe_allow_html=True)

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
st.subheader("Template Sijil (.docx / .pdf)")
template_file = st.file_uploader("Muat naik template sijil", type=["docx","pdf"])
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

def docx_to_pdf(docx_bytes):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_docx:
        tmp_docx.write(docx_bytes.read())
        tmp_docx.flush()
        pdf_path = tmp_docx.name.replace(".docx",".pdf")
        convert(tmp_docx.name,pdf_path)
    with open(pdf_path,"rb") as f:
        pdf_bytes = io.BytesIO(f.read())
    os.remove(tmp_docx.name)
    os.remove(pdf_path)
    pdf_bytes.seek(0)
    return pdf_bytes

def pdf_to_png(pdf_bytes):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc[0]
    pix = page.get_pixmap(dpi=150)
    img_bytes = io.BytesIO(pix.tobytes("png"))
    doc.close()
    img_bytes.seek(0)
    return img_bytes

def generate_pdf_from_template(template_bytes, name, ic):
    if template_file.type=="application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        docx_bytes = generate_docx(template_bytes, name, ic)
        pdf_bytes = docx_to_pdf(docx_bytes)
        return pdf_bytes
    else:
        # PDF template
        pdf_bytes = io.BytesIO(template_bytes)
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        for page in doc:
            for inst in page.search_for("{NAMA}"):
                page.insert_text(inst[:2], name)
            for inst in page.search_for("{IC}"):
                page.insert_text(inst[:2], ic)
        out = io.BytesIO()
        doc.save(out)
        out.seek(0)
        return out

def generate_png_from_pdf(pdf_bytes):
    return pdf_to_png(pdf_bytes)

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
        cols = st.columns([4,1,1])
        cols[0].markdown(f"<b>{name}</b>", unsafe_allow_html=True)
        if cols[1].button("PNG", key=f"png_{idx}"):
            pdf_bytes = generate_pdf_from_template(st.session_state.template_bytes, name, ic)
            img_bytes = generate_png_from_pdf(pdf_bytes)
            cols[1].download_button(f"Muat Turun PNG", img_bytes, f"Sijil_{name}.png", "image/png")
        if cols[2].button("PDF", key=f"pdf_{idx}"):
            pdf_bytes = generate_pdf_from_template(st.session_state.template_bytes, name, ic)
            cols[2].download_button(f"Muat Turun PDF", pdf_bytes, f"Sijil_{name}.pdf", "application/pdf")

    # ================== Download All ==================
    st.markdown("---")
    st.subheader("Download Semua Sijil Sekali")

    if st.button("Download All PNG"):
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf,"w") as zipf:
            for idx, row in st.session_state.df.iterrows():
                name = row["Nama"]
                ic = row["IC"]
                pdf_bytes = generate_pdf_from_template(st.session_state.template_bytes, name, ic)
                img_bytes = generate_png_from_pdf(pdf_bytes)
                zipf.writestr(f"Sijil_{name}.png", img_bytes.getvalue())
        zip_buf.seek(0)
        st.download_button("Muat Turun Semua PNG", zip_buf, "Sijil_All_PNG.zip", "application/zip")

    if st.button("Download All PDF"):
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf,"w") as zipf:
            for idx, row in st.session_state.df.iterrows():
                name = row["Nama"]
                ic = row["IC"]
                pdf_bytes = generate_pdf_from_template(st.session_state.template_bytes, name, ic)
                zipf.writestr(f"Sijil_{name}.pdf", pdf_bytes.getvalue())
        zip_buf.seek(0)
        st.download_button("Muat Turun Semua PDF", zip_buf, "Sijil_All_PDF.zip", "application/zip")

# ================== Footer ==================
st.markdown("""
<p style='text-align:center; font-size:16px; color:#0b5ed7; margin-top:20px;'>
<b>Inovasi Sijil Automatik</b><br><br>
Hasil ciptaan Narjihah binti Mohd Hashim, Mohamad Adham bin Abdul Malek, 
Nor Aqilah binti Aliasam, Muhammad Amin bin Muhammad Puzi, 
Siti Nur Amira bt. Abdul Talib untuk mempercepatkan proses 
penerbitan sijil secara digital.
</p>
""", unsafe_allow_html=True)
