import streamlit as st
import fitz  # PyMuPDF
from groq import Groq
import tempfile
import os
from fpdf import FPDF
from io import BytesIO

# Initialize GROQ client (replace with your actual API key)
client = Groq(api_key="your-groq-api-key")

st.set_page_config(page_title="PDF Agreement Comparator", layout="centered")
st.title("📄 Agreement Comparison Tool")
st.write("Upload two versions of an agreement PDF to identify and highlight differences.")

# Upload files
file1 = st.file_uploader("Upload Original Agreement (PDF)", type="pdf", key="file1")
file2 = st.file_uploader("Upload Updated Agreement (PDF)", type="pdf", key="file2")

def extract_text(pdf_file):
    text = ""
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

def get_diff_using_groq(text1, text2):
    prompt = f"""
You are a legal assistant. Compare the following two versions of a legal agreement.

ORIGINAL AGREEMENT:
{text1}

UPDATED AGREEMENT:
{text2}

Identify key changes between the two versions, including added, removed, or altered clauses. Provide a clear, structured summary of the differences.
"""
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def generate_pdf(diff_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, "📝 Summary of Changes Between Agreement Versions:\n\n" + diff_text)
    output = BytesIO()
    pdf.output(output)
    output.seek(0)
    return output

# Processing
if file1 and file2:
    with st.spinner("Extracting and comparing agreements..."):
        text1 = extract_text(file1)
        text2 = extract_text(file2)

        diff_result = get_diff_using_groq(text1, text2)
        annotated_pdf = generate_pdf(diff_result)

    st.success("Comparison complete!")
    st.download_button(
        label="📥 Download Annotated PDF",
        data=annotated_pdf,
        file_name="agreement_changes_summary.pdf",
        mime="application/pdf"
    )

    with st.expander("🔍 View Changes Summary"):
        st.markdown(diff_result)

else:
    st.info("Please upload both versions of the agreement to proceed.")
