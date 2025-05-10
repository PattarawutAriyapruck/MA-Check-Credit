from PyPDF2 import PdfReader, PdfWriter

import pandas as pd
import os
import tempfile
import uuid

def export_summary(classified_dict, credit_dict, export_path=None):
    if export_path == None:
        export_path = tempfile.gettempdir()

    field_dict = extract_fied_name(classified_dict, credit_dict)
    reader = PdfReader("./export_summary/BScMA_2561 แบบฟอร์มสำเร็จ คณิตศาสตร์.pdf")
    writer = PdfWriter()
    
    for page_num in range(len(reader.pages)):
        writer.add_page(reader.pages[page_num])
        writer.update_page_form_field_values(
            writer.pages[page_num], field_dict
        )

    output_file = os.path.join(export_path, f"BscMA_2561_ดาวน์โหลด_{uuid.uuid4().hex}.pdf")
    with open(output_file, "wb") as output_stream:
        writer.write(output_stream)
    return output_file

def extract_fied_name(classified_dict:dict, credit_dict:dict):
    reader = PdfReader("./export_summary/BScMA_2561 แบบฟอร์มสำเร็จ คณิตศาสตร์.pdf")
    fields_name = list(reader.get_fields().keys())
    course_name = list(map(lambda course: course[0], classified_dict["TOTAL"]))
    
    # Field name for exsisting course grade.
    existing_field = list(filter(lambda field: field[:7] in course_name and field[7:] == "_Grade1", fields_name))
    
    # Field name for GendEd_Elective course.
    gened_code_field = list(filter(lambda field: field[:14] == "GenEd_Elective" and len(field) == 15, fields_name))
    gened_credit_field = list(filter(lambda field: field[:21] == "Credit_GenEd_Elective", fields_name))
    gened_grade_field = list(filter(lambda field: field[:14] == "GenEd_Elective" and "Grade1" in field, fields_name))
    gened_total_field = list(filter(lambda field: field == "Total_GenEd_Elective", fields_name))
    gened_field = {
        "course_code": gened_code_field,
        "credit": gened_credit_field,
        "grade": gened_grade_field,
        "total": gened_total_field
        }
    
    # Field name for Elective course.
    elcetive_code_field = ["Elective1", "text_159havq", "text_160lklk", "text_161tkfj",
                           "text_162yjie", "text_163wfsu", "text_164agsx", "text_165hymw",
                           "text_167hjcn", "text_168jfdx", "text_169yyba", "text_170ugky",
                           "text_171acwv", "text_172kibh"]
    elcetive_credit_field = list(filter(lambda field: field[:15] == "Credit_Elective", fields_name))
    elcetive_grade_field = list(filter(lambda field: field[:8] == "Elective" and "Grade1" in field, fields_name))
    elcetive_total_field = list(filter(lambda field: field == "Total_Elective", fields_name))
    elcetive_field = {
        "course_code": elcetive_code_field,
        "credit": elcetive_credit_field,
        "grade": elcetive_grade_field,
        "total": elcetive_total_field
        }
    
    # Field name for Free Elective course.
    free_elcetive_code_field = list(filter(lambda field: field[:12] == "FreeElective" and len(field) == 13, fields_name))
    free_elcetive_credit_field = list(filter(lambda field: field[:19] == "Credit_FreeElective", fields_name))
    free_elcetive_grade_field = list(filter(lambda field: field[:12] == "FreeElective" and "Grade1" in field, fields_name))
    free_elcetive_total_field = list(filter(lambda field: field == "Total_FreeElective", fields_name))
    free_elcetive_field = {
        "course_code": free_elcetive_code_field,
        "credit": free_elcetive_credit_field,
        "grade": free_elcetive_grade_field,
        "total": free_elcetive_total_field
        }
    
    field_dict = {
        "Existing_course": existing_field,
        "GenEd": gened_field,
        "Elective": elcetive_field,
        "FreeElective": free_elcetive_field
        }
    exist_mapping = create_exist_mapping(field_dict, classified_dict, credit_dict)
    notex_mapping = create_notexist_mapping(field_dict, classified_dict, credit_dict)
    exist_mapping.update(notex_mapping)
    return exist_mapping

def create_exist_mapping(field_dict:dict, classified_dict:dict, credit_dict:dict):
    propper_mapping = {}

    for field_name in field_dict["Existing_course"]:
        field_code = field_name[:7]
        for course_data in classified_dict["TOTAL"]:
            if field_code == course_data[0] and field_code not in propper_mapping.keys():
                propper_mapping[field_name] = course_data[3]
    propper_mapping["Total_Compulsory"] = credit_dict["COURSE_MATH_CREDIT"]
    return propper_mapping

def create_notexist_mapping(field_dict: dict, classified_dict: dict, credit_dict: dict):
    ref_gened_uni = list(pd.read_excel("./course_classification/B.SC-MA 2561.xlsx", sheet_name="GenEd1")["COURSE CODE"])
    ref_gened_depa = list(pd.read_excel("./course_classification/B.SC-MA 2561.xlsx", sheet_name="GenEd2")["COURSE CODE"])
    ref_course_core = list(pd.read_excel("./course_classification/B.SC-MA 2561.xlsx", sheet_name="Elective1")["COURSE CODE"])
    ref_course_math = list(pd.read_excel("./course_classification/B.SC-MA 2561.xlsx", sheet_name="Elective2")["COURSE CODE"])
    ref_course_opt = list(pd.read_excel("./course_classification/B.SC-MA 2561.xlsx", sheet_name="Elective3")["COURSE CODE"])
    check_code = ref_gened_uni + ref_gened_depa + ref_course_core + ref_course_math + ref_course_opt

    proper_mapping = {}
    name_field = [key for key in field_dict.keys() if key != 'Existing_course']
    dict_keys = ['GENED_DEP', 'COURSE_OPT', 'ELECTIVE']
    credit_keys = ['GENED_DEP_CREDIT', 'COURSE_OPT_CREDIT', 'ELECTIVE_CREDIT']
    
    for key, name in enumerate(name_field):
        field = field_dict[name]
        class_dict = classified_dict[dict_keys[key]]
        class_dict = [course for course in class_dict if course[0] not in check_code]
        credit = credit_dict[credit_keys[key]]

        for i in range(len(class_dict)):
            proper_mapping[field['course_code'][i]] = class_dict[i][0]
            proper_mapping[field['credit'][i]] = class_dict[i][2]
            proper_mapping[field['grade'][i]] = class_dict[i][3]

        proper_mapping[field['total'][0]] = str(credit)

    return proper_mapping

if __name__ == "__main__":
    sample_data = {
        'SCPY191': [('1', 'A'), 'INTRODUCTORY PHYSICS LAB'],
        'SCPY157': [('3', 'A'), 'PHYSICS I'],
        'SCMA118': [('3', 'C'), 'CALCULUS'],
        'SCCH103': [('3', 'A'), 'GENERAL CHEMISTRY I'],
        'SCBI121': [('2', 'B'), 'GENERAL BIOLOGY I'],
        'SCBI102': [('1', 'A'), 'BIOLOGY LABORATORY I'],
        'MUGE100': [('3', 'S'), 'GENERAL ED FOR HUMAN DEVELOP'],
        'LATH100': [('3', 'S'), 'ARTS OF USING THAI LANG IN COM'],
        'LAEN103': [('3', 'O'), 'ENGLISH LEVEL I'],
        'SHSS123': [('2', 'O'), 'DECIS MAK IN MANAGE FOR ENTRE'],
        'SHHU169': [('2', 'O'), 'AMAZING THAI ROYAL TEMPLE'],
        'SCPY158': [('3', 'C+'), 'PHYSICS II'],
        'SCMA168': [('3', 'A'), 'ODE'],
        'SCCH107': [('1', 'S'), 'GENERAL CHEMISTRY LAB'],
        'SCCH104': [('3', 'B+'), 'GENERAL CHEMISTRY II'],
        'SCBI122': [('3', 'B'), 'GENERAL BIOLOGY II'],
        'SCBI104': [('1', 'B'), 'BIOLOGY LABORATORY II'],
        'LAEN104': [('3', 'O'), 'ENGLISH LEVEL II'],
        'SCMA280': [('3', 'A'), 'PROBABILITY'],
        'SCMA251': [('3', 'A'), 'LINEAR  ALGEBRA'],
        'SCMA240': [('3', 'A'), 'COMPUTER PROGRAMMING'],
        'SCMA212': [('3', 'A'), 'CAL'],
        'SCMA211': [('3', 'A'), 'PRINCIPLES OF MATHS'],
        'LAEN136': [('3', 'S'), 'READ'],
        'SCMA447': [('3', 'A'), 'DATA MINING'],
        'SCMA284': [('3', 'A'), 'STATISTICS'],
        'SCMA263': [('3', 'A'), 'DIFFERENTIAL EQUATIONS'],
        'SCMA248': [('3', 'A'), 'INTRODUCTION TO DATA  SCIENECE'],
        'SCMA221': [('3', 'A'), 'VECTOR ANALYSIS'],
        'SCMA215': [('3', 'C+'), 'ADVANCED CALCULUS'],
        'LAEN222': [('2', 'S'), 'EFFECTIVE PRESENTATIONS IN ENG'],
        'SCMA483': [('3', 'A'), 'LINEAR REGRESSION ANALYSIS'],
        'SCMA475': [('3', 'A'), 'OPERATIONS RESEARCH'],
        'SCMA444': [('3', 'A'), 'MATHEMATICS FOR AI'],
        'SCMA342': [('3', 'B'), 'NUMERICAL ANALYSIS'],
        'SCMA322': [('3', 'A'), 'MATHEMATICAL ANALYSIS'],
        'SCMA311': [('2', 'S'), 'UNDERSTANDING OTHERS'],
        'SCMA247': [('3', 'A'), 'DATA STRUCT IN MATH'],
        'SCMA492': [('3', 'A'), 'SPECIAL TOPICS IV'],
        'SCMA491': [('3', 'A'), 'SPECIAL TOPICS III'],
        'SCMA482': [('3', 'A'), 'TIME SERIES METHOD'],
        'SCMA354': [('3', 'A'), 'ABSTRACT ALGEBRA I'],
        'SCMA341': [('3', 'A'), 'DESIGN'],
        'SCMA320': [('3', 'B+'), 'COMPLEX VARIABLES']
    }
    # export_summary(sample_data, credit_dict={"TOTAL":10})
    # extract_fied_name(sample_data)
