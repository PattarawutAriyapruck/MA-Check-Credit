import pandas as pd

def course_classify(course_dict:dict, distinct:bool):
    enrolled_course = list(map(lambda a, b: [a, b[1], b[0][0], b[0][1]], list(course_dict.keys()), list(course_dict.values())))
    
    # วิชาเลือกศึกษาทั่วไป -> เป็นวิชาที่ทางมหาวิทยาลัยบังคับลงให้ครบแบ่งเป้็นวิชาที่มหาวิทยาลัยกำหนด และ วิชาที่หลักสูตรกำหนด ตัดเกรดแบบ O S U
    ref_gened_uni = pd.read_excel("./course_classification/B.SC-MA 2561.xlsx",
                                    sheet_name="GenEd1")
    ref_gened_depa = pd.read_excel("./course_classification/B.SC-MA 2561.xlsx",
                                    sheet_name="GenEd2")
    
    gened_uni = ref_gened_uni["COURSE CODE"].values
    gened_dep = ref_gened_depa["COURSE CODE"].values
    
    # วิชาเฉพาะ -> ประกอบไปด้วยวิชาบังคับและวิชาที่ภาคเปิดให้ลง
    ref_course_core = pd.read_excel("./course_classification/B.SC-MA 2561.xlsx",
                                    sheet_name="Elective1")
    ref_course_math = pd.read_excel("./course_classification/B.SC-MA 2561.xlsx",
                                    sheet_name="Elective2")
    ref_course_opt = pd.read_excel("./course_classification/B.SC-MA 2561.xlsx",
                                    sheet_name="Elective3")
    
    course_core = ref_course_core["COURSE CODE"].values
    if distinct: 
        course_math = ref_course_math["COURSE CODE"].values
    elif not distinct: 
        course_math = ref_course_math[ref_course_math["DISTINCT"] == 0]["COURSE CODE"].values
    course_opt = ref_course_opt["COURSE CODE"].values
    
    # วิชาเลือกเสรี -> ตัดเกรดแบบ A - F (วิชาทุกอย่างที่ไม่ใช่ทั่่วไปและวิชาเฉพาะ)
    ref_elective = pd.read_excel("./course_classification/B.SC-MA 2561.xlsx",
                                    sheet_name="FreeElective")
    
    elec_course = ref_elective["COURSE CODE"].values
    
    # Course filter
    gened_uni, enrolled_course = filter_course(enrolled_course=enrolled_course, reference=gened_uni)
    gened_dep, enrolled_course = filter_course(enrolled_course=enrolled_course, reference=gened_dep)
    course_core, enrolled_course = filter_course(enrolled_course=enrolled_course, reference=course_core)
    course_math, enrolled_course = filter_course(enrolled_course=enrolled_course, reference=course_math)
    gened_opt, course_opt, elec_course = filter_course(enrolled_course=enrolled_course)
    
    classified_dict = {
        "TOTAL": gened_uni + gened_dep + gened_opt + course_core + course_math + course_opt + elec_course,
        "GENED_UNI": gened_uni,
        "GENED_DEP": gened_dep + gened_opt,
        "COURSE_CORE": course_core,
        "COURSE_MATH": course_math,
        "COURSE_OPT": course_opt,
        "ELECTIVE": elec_course
        }
    
    return classified_dict

def filter_course(enrolled_course:list, reference:list = None):
    if reference is not None:
        reference = list(filter(lambda enroll: enroll[0] in reference, enrolled_course))
        for item in reference:
            enrolled_course = [entry for entry in enrolled_course if item[0] not in entry]
        return reference, enrolled_course
    elif reference is None:
        gened_opt = list(filter(lambda enroll: enroll[3] in ["O", "S", "U"], enrolled_course))
        course_opt = list(filter(lambda enroll: enroll[0][:4] == "SCMA", enrolled_course))
        remove_item = list(map(lambda course: course[0], gened_opt)) + list(map(lambda course: course[0], course_opt))
        for item in remove_item:
            enrolled_course = [entry for entry in enrolled_course if item not in entry]
        elec_course = enrolled_course
        return gened_opt, course_opt, elec_course

def credit_sum(course_dict:dict, distinct:bool):
    credit_dict = {
        "TOTAL_CREDIT": sum([int(nested[2]) for nested in course_dict["TOTAL"]]),
        "GENED_UNI_CREDIT": sum([int(nested[2]) for nested in course_dict["GENED_UNI"]]),
        "GENED_DEP_CREDIT": sum([int(nested[2]) for nested in course_dict["GENED_DEP"]]),
        "COURSE_CORE_CREDIT": sum([int(nested[2]) for nested in course_dict["COURSE_CORE"]]),
        "COURSE_MATH_CREDIT": sum([int(nested[2]) for nested in course_dict["COURSE_MATH"]]),
        "COURSE_OPT_CREDIT": sum([int(nested[2]) for nested in course_dict["COURSE_OPT"]]),
        "ELECTIVE_CREDIT": sum([int(nested[2]) for nested in course_dict["ELECTIVE"]])
    }
    if distinct:
        suggest_dict = {
            "TOTAL_CREDIT": 131 - credit_dict["TOTAL_CREDIT"],
            "GENED_UNI_CREDIT": 12 - credit_dict["GENED_UNI_CREDIT"],
            "GENED_DEP_CREDIT": 18 - credit_dict["GENED_DEP_CREDIT"],
            "COURSE_CORE_CREDIT": 27 - credit_dict["COURSE_CORE_CREDIT"],
            "COURSE_MATH_CREDIT": 51 - credit_dict["COURSE_MATH_CREDIT"],
            "COURSE_OPT_CREDIT": 17 - credit_dict["COURSE_OPT_CREDIT"],
            "ELECTIVE_CREDIT": 6 - credit_dict["ELECTIVE_CREDIT"]
        }
        exceed_limit = list(filter(lambda x: x[1] < 0, suggest_dict.items()))
        if exceed_limit:
            return verify_course(course_dict, credit_dict, suggest_dict, distinct)
    elif not distinct:
        suggest_dict = {
            "TOTAL_CREDIT": 130 - credit_dict["TOTAL_CREDIT"],
            "GENED_UNI_CREDIT": 12 - credit_dict["GENED_UNI_CREDIT"],
            "GENED_DEP_CREDIT": 18 - credit_dict["GENED_DEP_CREDIT"],
            "COURSE_CORE_CREDIT": 27 - credit_dict["COURSE_CORE_CREDIT"],
            "COURSE_MATH_CREDIT": 46 - credit_dict["COURSE_MATH_CREDIT"],
            "COURSE_OPT_CREDIT": 21 - credit_dict["COURSE_OPT_CREDIT"],
            "ELECTIVE_CREDIT": 6 - credit_dict["ELECTIVE_CREDIT"]
        }
        exceed_limit = list(filter(lambda x: x[1] < 0, suggest_dict.items()))
        if exceed_limit:
            return verify_course(course_dict, credit_dict, suggest_dict, distinct)
    return credit_dict, suggest_dict

def verify_course(course_dict:dict, credit_dict:dict, suggest_dict:dict, distinct:bool):
    if suggest_dict['TOTAL_CREDIT'] < 0:
        suggest_dict['TOTAL_CREDIT'] = 0
    exceed_limit = sorted(list(filter(lambda x: x[1] < 0, suggest_dict.items())))
    if sum([int(credit[2]) for credit in course_dict['ELECTIVE']]) == 6:
        for category, exceed_credit in exceed_limit:
                if exceed_credit < 0:
                    suggest_dict[category] = 0
        return credit_dict, suggest_dict
    for category, exceed_credit in exceed_limit:
        key = category.replace("_CREDIT", "")
        category_course = sorted(course_dict[key], key=lambda x: x[2])

        ref_gened_uni = pd.read_excel("./course_classification/B.SC-MA 2561.xlsx", sheet_name="GenEd1")
        ref_gened_depa = pd.read_excel("./course_classification/B.SC-MA 2561.xlsx", sheet_name="GenEd2")
        ref_course_core = pd.read_excel("./course_classification/B.SC-MA 2561.xlsx", sheet_name="Elective1")
        ref_course_math = pd.read_excel("./course_classification/B.SC-MA 2561.xlsx", sheet_name="Elective2")
        ref_course_opt = pd.read_excel("./course_classification/B.SC-MA 2561.xlsx", sheet_name="Elective3")
        check_code = list(ref_gened_uni["COURSE CODE"]) + list(ref_gened_depa["COURSE CODE"]) + list(ref_course_core["COURSE CODE"]) + list(ref_course_math["COURSE CODE"]) + list(ref_course_opt["COURSE CODE"])

        for code, name, credit, grade in category_course:
            if sum([int(credit[2]) for credit in course_dict['ELECTIVE']]) == 6:
                break
            if exceed_credit < 0:
                if code not in check_code:
                    course_info = [code, name, credit, grade]
                    exceed_credit += int(credit)
                    course_dict[key].remove(course_info)
                    course_dict['ELECTIVE'].append(course_info)
                else:
                    continue
            else:
                continue
    return credit_sum(course_dict, distinct)

def get_information(courses_data:dict, is_distinct:bool):
    classified_dict = course_classify(course_dict=courses_data, distinct=is_distinct)
    credit_dict, suggest_dict = credit_sum(course_dict=classified_dict, distinct=is_distinct)
    return classified_dict, credit_dict, suggest_dict

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
    
    """
    HOW TO USE FUNCTION
    
    You must input the data as dictionary like a sample data above that you will get from course_extraction function
    then use "get_information()" to get classifed_dictionary, summary_credit and sugesst_credit that you can you for
    display. 
    """
    classifeid, summary, suggest = get_information(courses_data=sample_data, is_distinct=True)
    print(f"Course Dictionary\n{classifeid}\
        \n\nCredit Dictionary\n{summary}\
        \n\nSuggest Dictionary\n{suggest}")
