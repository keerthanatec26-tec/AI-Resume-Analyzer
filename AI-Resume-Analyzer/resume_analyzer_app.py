import streamlit as st
import spacy
import language_tool_python
import PyPDF2
from PIL import Image
import pytesseract

nlp = spacy.load("en_core_web_sm")
tool = language_tool_python.LanguageTool('en-US')

def grammar_check(text):
    matches = tool.check(text)
    suggestions = []
    for match in matches:
        wrong_text = text[match.offset : match.offset + match.errorLength]
        suggestion = match.replacements[0] if match.replacements else ""
        reason = match.message
        suggestions.append((wrong_text, suggestion, reason))
    return suggestions

def keyword_match(text, keywords):
    return [kw for kw in keywords if kw.lower() in text.lower()]

def extract_soft_skills(text):
    soft_skills = ["communication", "leadership", "teamwork", "adaptability", "problem-solving"]
    return [skill for skill in soft_skills if skill in text.lower()]

def resume_format_validator(text):
    required_sections = ["education", "experience", "skills"]
    return [section for section in required_sections if section not in text.lower()]

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

def extract_text_from_image(image):
    return pytesseract.image_to_string(image)

def analyze_resume(text, keywords):
    return {
        "grammar_errors": grammar_check(text),
        "soft_skills": extract_soft_skills(text),
        "missing_sections": resume_format_validator(text),
        "matched_keywords": keyword_match(text, keywords)
    }

def build_summary(results):
    summary = "## 📊 **AI Resume Analysis Report**\n"

    # ✅ Grammar table
    summary += "### ✏️ Grammar Suggestions:\n"
    if results["grammar_errors"]:
        summary += "| Wrong | Suggestion | Reason |\n|------|-------------|-------|\n"
        for wrong, suggestion, reason in results["grammar_errors"]:
            summary += f"| {wrong} | {suggestion} | {reason} |\n"
    else:
        summary += "✔ No grammar errors found.\n"

    # 🧠 Soft Skills
    summary += "\n### 🧠 Soft Skills Found:\n"
    summary += ", ".join(results["soft_skills"]) if results["soft_skills"] else "⚠ No soft skills found."

    # 📂 Missing Sections
    summary += "\n\n### 📂 Missing Sections:\n"
    summary += ", ".join(results["missing_sections"]) if results["missing_sections"] else "✔ All standard sections present."

    # 🔍 Matched Keywords
    summary += "\n\n### 🔍 Matched Keywords:\n"
    summary += ", ".join(results["matched_keywords"]) if results["matched_keywords"] else "⚠ No keywords matched."

    return summary

# 🌟 Streamlit App UI
st.set_page_config(page_title="AI Resume Analyzer", page_icon="📄", layout="wide")
st.title("📄 AI Resume Analyzer (PDF, Image, Text)")

st.markdown("Upload your **resume PDF**, **photo**, or paste as text to get instant analysis.")

uploaded_file = st.file_uploader("📤 Upload Resume (PDF or Image)", type=["pdf", "png", "jpg", "jpeg"])
resume_text = st.text_area("✏️ Or paste resume text here:", height=250)
keywords_text = st.text_input("🔑 Enter job keywords (comma separated):", "Python, Java, teamwork, leadership")

job_keywords = [kw.strip() for kw in keywords_text.split(",") if kw.strip()]

if st.button("🚀 Analyze Resume"):
    text = ""
    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            text = extract_text_from_pdf(uploaded_file)
        else:
            image = Image.open(uploaded_file)
            text = extract_text_from_image(image)
    elif resume_text:
        text = resume_text
    else:
        st.warning("⚠ Please upload a file or paste resume text.")
        st.stop()

    if not text.strip():
        st.error("❌ Could not extract text. Please check your file or text input.")
    else:
        results = analyze_resume(text, job_keywords)
        summary = build_summary(results)
        st.markdown(summary, unsafe_allow_html=True)
