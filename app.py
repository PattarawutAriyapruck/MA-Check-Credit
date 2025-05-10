from flask import Flask, flash, redirect, render_template, request, url_for, session, send_file, after_this_request
from function.pdf_to_text_path import extract_text_from_pdf_path
from function.extract_details import extract_course_grades, extract_detail
from function.classification import get_information
from export_summary.fill_content import export_summary
import os

app = Flask(__name__)

app.secret_key = 'ma_check_credit_secret_key'

@app.route('/')
def home():
    return render_template('agree.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/submit', methods=['POST'])
def submit():
    degree = request.form.get('degree')
    if degree == "B.Sc. (Math)":
        is_distinct = False
    elif degree == "B.Sc. (Math) (Distinction)":
        is_distinct = True
    transcript = request.files['transcript']

    if transcript and transcript.filename.endswith('.pdf'):
        pdf_text = extract_text_from_pdf_path(transcript)
        detail = extract_detail(pdf_text)
        check_f = extract_course_grades(pdf_text)
        result_f = False if any(grade == 'F' for grade in check_f) else True
        try:
            classifeid, summary, suggest = get_information(detail, is_distinct = is_distinct)

            session['F'] = result_f
            session['degree'] = degree
            session['classifeid'] = classifeid
            session['summary'] = summary
            session['suggest'] = suggest

        except:
            return redirect(url_for('dashboard'))

        return redirect(url_for('OverallCreditMA'))
            
    else:
        flash("Please upload a valid PDF transcript.", "danger")
        return redirect(url_for('dashboard'))

@app.route('/OverallCreditMA')
def OverallCreditMA():
    total_credit_sum = session.get('summary')['TOTAL_CREDIT']
    total_credit_suggest = session.get('suggest')['TOTAL_CREDIT']

    gen_credit_sum = session.get('summary')['GENED_UNI_CREDIT'] + session.get('summary')['GENED_DEP_CREDIT']
    gen_credit_suggest = session.get('suggest')['GENED_UNI_CREDIT'] + session.get('suggest')['GENED_DEP_CREDIT']

    core_and_specific_credit_sum = session.get('summary')['COURSE_CORE_CREDIT'] + session.get('summary')['COURSE_MATH_CREDIT']
    core_and_specific_credit_suggest = session.get('suggest')['COURSE_CORE_CREDIT'] + session.get('suggest')['COURSE_MATH_CREDIT']

    major_credit_sum = session.get('summary')['COURSE_OPT_CREDIT']
    major_credit_suggest = session.get('suggest')['COURSE_OPT_CREDIT']

    free_credit_sum = session.get('summary')['ELECTIVE_CREDIT']
    free_credit_suggest = session.get('suggest')['ELECTIVE_CREDIT']

    return render_template("OverallCreditMA(NEW).html", total_credit_sum = total_credit_sum,
                           total_credit_suggest = total_credit_suggest, 
                           gen_credit_sum = gen_credit_sum, 
                           gen_credit_suggest =  gen_credit_suggest,
                           core_and_specific_credit_sum = core_and_specific_credit_sum, 
                           core_and_specific_credit_suggest = core_and_specific_credit_suggest, 
                           major_credit_sum =  major_credit_sum, 
                           major_credit_suggest = major_credit_suggest, 
                           free_credit_sum = free_credit_sum, 
                           free_credit_suggest = free_credit_suggest)

@app.route('/total_credit')
def total_credit():
    total_credit_data = session.get('classifeid')['TOTAL']
    return render_template('total_credit.html', total_credit_data = total_credit_data)

@app.route('/gen_ed')
def gen_ed():
    gen_ed = session.get('classifeid')['GENED_UNI'] + session.get('classifeid')['GENED_DEP']
    return render_template('gen_ed.html', gen_ed = gen_ed)

@app.route('/core_and_specific')
def core_and_specific():
    core_courses = session.get('classifeid')['COURSE_CORE']
    specific_courses = session.get('classifeid')['COURSE_MATH']
    return render_template('core_and_specific.html', core_courses = core_courses, specific_courses = specific_courses)

@app.route('/major')
def major():
    major_electives = session.get('classifeid')['COURSE_OPT']
    return render_template('major.html', major_electives = major_electives)

@app.route('/free')
def free():
    free_electives = session.get('classifeid')['ELECTIVE']
    return render_template('free.html', free_electives = free_electives)

@app.route('/dowload', methods=['GET', 'POST'])
def dowload_file():
    if session.get('F'):
        file_path = export_summary(session.get('classifeid'), session.get('summary'))

        @after_this_request
        def remove_file(response):
            try:
                os.remove(file_path)
            except Exception as e:
                app.logger.error(f"Error removing file {file_path}: {e}")
            return response
        
        flash("Download completed.", "success")
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name="BScMA_2561_ดาวน์โหลด.pdf"
            )
    else:
        flash("Unable to download PDF because you have a grade F in your transcript.", "danger")
        return redirect(url_for('OverallCreditMA'))

if __name__ == '__main__':
    app.run(debug=True)