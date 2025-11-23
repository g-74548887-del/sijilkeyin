import streamlit as st
import pandas as pd
import io
import zipfile
from PIL import Image, ImageDraw, ImageFont
from docx import Document

st.set_page_config(page_title="Jana Sijil Automatik", layout="wide")

# ================== HEADER ==================
st.markdown("""
<h1 style='text-align:center;'>📝 Jana Sijil Automatik</h1>
<p style='text-align:center;'>Masukkan nama & IC murid, sistem akan jana sijil ikut template Word.</p>
""", unsafe_allow_html=True)

# ================== SESSION STATE ==================
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=["Nama", "IC"])
if "generated" not in st.session_state:
    st.session_state.generated = False

# ================== UPLOAD TEMPLATE ==================
st.subheader("📄 Upload Template Sijil (.docx)")
template_file = st.file_uploader("Muat naik template sijil Word (.docx)", type=["docx"])

st.markdown("""
<div style="border:2px solid #0b5ed7;background-color:#eef5ff;padding:12px;border-radius:10px;">
<b style='color:#0b5ed7;'>Nota Penting:</b><br>
Template mesti mengandungi placeholder:<br>
<code>{NAMA}</code> & <code>{IC}</code>
</div>
""", unsafe_allow_html=True)

# ================== LINK TEMPLATE CONTOH ==================
st.markdown("""
### 📁 Contoh Template Sijil  
<a href='https://drive.google.com/drive/folders/1cG3kiflH1mVw4kmUvRU_16mA1SIy_chR' target='_blank' style="font-size:18px;">
🔗 <b>Klik untuk buka folder Template Sijil</b>
</a>
""", unsafe_allow_html=True)

st.markdown("---")

# ================== SENARAI NAMA / IC ==================
st.subheader("👥 Senarai Nama Murid (Nama | IC)")

edited_df = st.data_editor(
    st.session_state.df,
    use_container_width=True,
    num_rows="dynamic",
    hide_index=True,
    column_config={
        "Nama": st.column_config.TextColumn(width="large"),
        "IC": st.column_config.TextColumn(width="medium"),
    }
)
st.session_state.df = edited_df

if st.button("➕ Tambah Nama"):
    st.session_state.df = pd.concat(
        [st.session_state.df, pd.DataFrame([{"Nama": "", "IC": ""}])],
        ignore_index=True
    )

# ================== LINK SENARAI NAMA EXCEL ==================
st.markdown("""
### 📥 Import Nama dari Excel  
<a href='https://drive.google.com/drive/folders/1YetTrTDYKT4Rvl2jXb1Iv5dEYe-9xj_9' 
   target='_blank' style="font-size:18px; text-decoration:none;">
📌 <b>Klik sini untuk buka senarai nama Excel (copy & paste terus)</b>
</a>
""", unsafe_allow_html=True)

st.markdown("---")

# ================== FUNCTIONS ==================
def generate_docx(template_bytes, name, ic):
    doc = Document(io.BytesIO(template_bytes))
    
    for p in doc.paragraphs:
        p.text = p.text.replace("{NAMA}", name).replace("{IC}", ic)

    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                cell.text = cell.text.replace("{NAMA}", name).replace("{IC}", ic)

    output = io.BytesIO()
    doc.save(output)
    output.seek(0)
    return output


def docx_to_png(docx_bytes):
    doc = Document(io.BytesIO(docx_bytes.read()))
    section = doc.sections[0]
    width, height = section.page_width, section.page_height

    def emu_to_px(emu):
        return int(emu / 914400 * 300)

    W = emu_to_px(width)
    H = emu_to_px(height)

    img = Image.new("RGB", (W, H), "white")
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 72)
    except:
        font = ImageFont.load_default()

    y = 300
    for p in doc.paragraphs:
        if p.text:
            draw.text((W // 2, y), p.text, anchor="mm", fill="black", font=font)
            y += 150

    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)
    return img_bytes

# ================== BUTTON JANA ==================
if template_file and st.button("🚀 Jana Sijil"):
    st.session_state.generated = True
    st.session_state.template_bytes = template_file.read()

# ================== SENARAI OUTPUT ==================
if st.session_state.generated:
    st.subheader("📜 Senarai Sijil Murid")

    for idx, row in st.session_state.df.iterrows():
        name = row["Nama"]
        ic = row["IC"]
        cols = st.columns([4,1])
        cols[0].markdown(f"<b>{name}</b>", unsafe_allow_html=True)

        if cols[1].button("📥 Word & PNG", key=f"word_{idx}"):
            docx_bytes = generate_docx(st.session_state.template_bytes, name, ic)
            png_bytes = docx_to_png(io.BytesIO(docx_bytes.getvalue()))

            cols[1].download_button("⬇️ Word", docx_bytes, f"Sijil_{name}.docx")
            cols[1].download_button("⬇️ PNG", png_bytes, f"Sijil_{name}.png")

    st.markdown("---")

    if st.button("📦 Download Semua Word & PNG"):
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w") as zipf:
            for idx, row in st.session_state.df.iterrows():
                name = row["Nama"]
                ic = row["IC"]
                docx_bytes = generate_docx(st.session_state.template_bytes, name, ic)
                png_bytes = docx_to_png(io.BytesIO(docx_bytes.getvalue()))
                zipf.writestr(f"Sijil_{name}.docx", docx_bytes.getvalue())
                zipf.writestr(f"Sijil_{name}.png", png_bytes.getvalue())
        
        zip_buf.seek(0)
        st.download_button("⬇️ Muat Turun Semua", zip_buf, "Sijil_All.zip")

# ================== FOOTER ==================
st.markdown("""
<p style='text-align:center; font-size:16px; color:#0b5ed7; margin-top:40px;'>
<b>Inovasi Sijil Automatik</b><br><br>
Dibangunkan oleh Narjihah binti Mohd Hashim, Mohamad Adham bin Abdul Malek, 
Nor Aqilah binti Aliasam, Muhammad Amin bin Muhammad Puzi, 
Siti Nur Amira bt. Abdul Talib.
</p>
""", unsafe_allow_html=True)
