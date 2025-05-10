import PyPDF2
import pandas as pd
# import io
# from PyPDF2 import PdfReader

def extract_text_from_pdf_path(pdf_path):

    pdf_reader = PyPDF2.PdfReader(pdf_path)
    
    text = ""

    for page_num in range(1):
        page = pdf_reader.pages[page_num]
        text += page.extract_text()
    
    return text

# def classify_degree(text):
#      ref_course_math = pd.read_excel("./course_classification/B.SC-MA 2561.xlsx",
#                                     sheet_name = "Elective2")
     
#      course_math = list(ref_course_math[ref_course_math["DISTINCT"] == 1]["COURSE CODE"].values)

#      return any(code in text for code in course_math)