import re

def extract_courses(content):
    course_pattern = r'([A-Z]{4}\d{3})\s*([A-Z\s]+)'
    
    matches = re.findall(course_pattern, content)
    
    courses = []
    for match in matches:
        course_id, course_name = match
        courses.append((course_id, course_name.strip()))
    
    course_dict = {code:name for code, name in courses}
    
    return course_dict