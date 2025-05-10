#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import re
from function.extrating import extract_courses

def extract_course_codes(text):
    course_code_pattern = r'[A-Z]{4}\d{3}'
    
    course_codes = re.findall(course_code_pattern, text)
    
    corrected_course_codes = []
    for match in re.finditer(r'([A-Z]{4}\d{3})([A-Z]{2,})?', text):
        code = match.group(1)
        corrected_course_codes.append(code)
    
    return corrected_course_codes

def extract_course_credits(text):
    credit_pattern = r'\b\d+[ABCDOFSPU]\+?'
    
    lines = text.splitlines()
    credits = []

    for line in lines:
        if 'SEMESTER' in line:
            continue
        else:
            matches = re.findall(credit_pattern, line)
            credits.extend(matches) 
    
    numbers = [grade[0] for grade in credits if grade[0].isnumeric()]

    return numbers

def extract_course_grades(text):
    credit_pattern = r'\b\d+[ABCDOFSPU]\+?'
    
    lines = text.splitlines()
    credits = []

    for line in lines:
        if 'SEMESTER' in line:
            continue
        else:
            matches = re.findall(credit_pattern, line)
            credits.extend(matches) 
    
    grades = [grade[1:] for grade in credits]

    return grades

def extract_codes_credits_grades(text):
    course_codes = extract_course_codes(text)
    cre, gd = extract_course_credits(text), extract_course_grades(text)
    course_credits = [(cre, gd) for cre, gd in zip(cre, gd)]
    course_dict = {code: credit for code, credit in zip(course_codes, course_credits)}
    return course_dict

def extract_detail(text):
    dict1 = extract_codes_credits_grades(text)
    dict2 = extract_courses(text)

    dict1.update({key: [dict1[key], dict2[key]] if key in dict2 else dict1[key] for key in dict1})
    dict1.update({key: dict2[key] for key in dict2 if key not in dict1})

    ma_check_credits = {key: value for key, value in dict1.items() if isinstance(value, list)}
    
    return ma_check_credits