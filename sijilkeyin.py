import streamlit as st
from docx import Document
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import io
import base64
import pandas as pd

# =============================
#  CUSTOM CSS – SUPAYA TULISAN JELAS
# =============================
st.markdown("""
<style>
html, body, [class*="css"]  {
    color: #ffffff !important;
}
label, .stTextInput label, .stFileUploader label, .stDataFrame {
    color: #ffffff !important;
}
</style>
""", unsafe_allow_html=True)

st.title("Generator Sijil (Template Word / PDF) – Versi Baharu")

# =============================
#  UPLOAD TEMPLATE
# =============================
uploaded_template = st.file_uploader(
    "Upload Template Sijil (Word / PDF)",
    type=["docx", "pdf"]
)

st.info("**Nota penting:** Pastikan template mempunyai tag **{NAMA}** dan **{IC}**.")

# =============================
#  TABLE UNTUK NAMA & IC
# =============================
st.subheader("Senarai Nama Murid")

default_data = pd.DataFrame({
    "NAMA": [""],
    "IC": [""]
})

df = st.data_editor(
    default_data,
    num_rows="dynamic",
    use_container_width=True
)

# =============================
#  BUTTON JANA SIJIL
# =============================
if st.button("Jana Sijil"):
    if uploaded_template is None:
        st.error("Sila upload template dahulu.")
    else:
        # Simpan semua fail sijil dalam ZIP
        zip_buffer = io.BytesIO()
        import zipfile
        zip_file = zipfile.ZipFile(zip_buffer, "w")

        for idx, row in df.iterrows():
            nama = str(row["NAMA"]).strip()
            ic = str(row["IC"]).strip()

            if nama == "" or ic == "":
                continue

            # =============================
            #   TEMPLATE DOCX
            # =============================
            if uploaded_template.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                doc = Document(uploaded_template)
                for p in doc.paragraphs:
                    if "{NAMA}" in p.text or "{IC}" in p.text:
                        p.text = p.text.replace("{NAMA}", nama).replace("{IC}", ic)

                # Simpan ke buffer
                out = io.BytesIO()
                doc.save(out)
                zip_file.writestr(f"{nama}_{ic}.docx", out.getvalue())

            # =============================
            #   TEMPLATE PDF – hanya overlay teks ganti
            # =============================
            else:
                pdf_buffer = io.BytesIO()
                c = canvas.Canvas(pdf_buffer, pagesize=A4)
                c.drawString(100, 750, f"Nama: {nama}")
                c.drawString(100, 720, f"IC: {ic}")
                c.save()

                zip_file.writestr(f"{nama}_{ic}.pdf", pdf_buffer.getvalue())

        zip_file.close()

        st.success("Sijil berjaya dijana!")

        # Butang download ZIP
        st.download_button(
            "Download Semua Sijil (ZIP)",
            data=zip_buffer.getvalue(),
            file_name="sijil.zip",
            mime="application/zip"
        )
