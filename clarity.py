from flask import Flask, make_response, send_file, session, request, redirect
import api
import json
import os
from werkzeug import secure_filename

UPLOAD_FOLDER = "./static/uploads/"
ALLOWED_EXTENSIONS = set(['csv'])

app = Flask(__name__)
app.config['SECRET_KEY'] = '24KJSF98325KJLSDF972saf29832LFjasf87FZKFJL78f7ds98FSDKLF'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/test")
def test():
    return _convert_to_JSON(api.top_students_struggling(1))


@app.route("/")
def index():
    return send_file("templates/index.html")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        csvfile = request.files['csvfile']
        if csvfile and allowed_file(csvfile.filename):
            filename = secure_filename(csvfile.filename)
            file_path = app.config['UPLOAD_FOLDER'] + filename
            csvfile.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    test_name = request.form.get("test_name")
    test_date = request.form.get("test_date")
    cohort_id = request.form["cohort"]
    api.parse_CSV(file_path, test_name, test_date, cohort_id)
    return redirect("/#/reports/")

@app.route('/upload2/', methods=['GET', 'POST'])
def upload_class_file():
    if request.method == 'POST':
        csvfile = request.files['studentfile']
        if csvfile and allowed_file(csvfile.filename):
            filename = secure_filename(csvfile.filename)
            file_path = app.config['UPLOAD_FOLDER'] + filename
            csvfile.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    class_name = request.form.get("class_name")
    teacher_id = session['user']
    cohort_id = api.add_new_cohort(class_name, teacher_id)
    user_type = "student"
    api.create_student_from_csv(file_path, cohort_id, user_type)

    return redirect("/#/reports/")

def _convert_to_JSON(result):
    """Convert result object to a JSON web request."""

    response = make_response(json.dumps(result))
    response.headers['Access-Control-Allow-Origin'] = "*"
    response.mimetype = "application/json"
    return response

@app.route("/api/addclass/", methods=['POST'])
def addclass():
    class_info = json.loads(request.data)
    cohort_name = (class_info.get("cohort")).get("name")
    teacher_id = session['user']
    cohort_id = api.add_new_cohort(cohort_name, teacher_id)
    list_of_students = class_info.get("students")
    for student in list_of_students:
        user_type = "student"
        first_name = student.get("first_name")
        last_name = student.get("last_name")
        student_id = api.create_student(user_type, first_name, last_name)
        api.add_student_to_cohort(student_id, cohort_id)
    return "Success"

@app.route("/api/getclasses/")
def get_cohorts():
    teacher_id = session['user']
    response = api.get_teacher_cohorts(teacher_id)
    return _convert_to_JSON(response)

@app.route("/api/allcohortspie/")
def all_cohorts_data_pie_chart():
    teacher_id = session['user']
    response = api.aggregate_most_recent_overall_cohort(teacher_id)
    return _convert_to_JSON(response)

@app.route("/api/allcohortstopfb/")
def all_cohorts_top_struggle_standards():
    teacher_id = session['user']
    response = api.top_struggle_standards_all_cohorts(teacher_id)
    return _convert_to_JSON(response)

@app.route("/api/allcohortsnorm/")
def all_cohorts_comp_to_norm():
    teacher_id = session['user']
    response = api.most_recent_comp_to_normscores_all_cohorts(teacher_id)
    return _convert_to_JSON(response)

@app.route("/api/allcohortcounts/")
def all_cohort_data():
    teacher_id = session['user']
    response = api.get_all_cohort_data_by_test(teacher_id)
    return _convert_to_JSON(response)

@app.route("/api/allcohortstudents/")
def all_cohorts_top_struggle_students():
    teacher_id = session['user']
    response = api.top_students_struggling(teacher_id)
    return _convert_to_JSON(response)

# @app.route("/api/singlecohortcounts/")
# def single_cohort_data():
#     cohort_id = request.args.get("id")
#     response = api.get_one_cohort_data_by_test(cohort_id)
#     return _convert_to_JSON(response)

# @app.route("/api/singlestudentcounts/")
# def single_student_data():
#     student_id = request.args.get("id")
#     response = api.get_one_student_data_by_test(student_id)
#     return _convert_to_JSON(response)

@app.route("/api/mostrecentall/")
def most_recent_all_by_standard():
    teacher_id = session['user']
    response = api.aggregate_most_recent_by_standard_overall_cohort(teacher_id)
    return _convert_to_JSON(response)

# @app.route("/api/mostrecentcohort/")
# def most_recent_single_cohort_by_standard():
#     cohort_id = request.args.get("id")
#     response = api.aggregate_most_recent_by_standard_single_cohort(cohort_id)
#     return _convert_to_JSON(response)


@app.route("/api/signup/", methods=['POST'])
def add_user():
    new_user = json.loads(request.data)
    user_type = "teacher"
    first_name = new_user.get("first_name")
    last_name = new_user.get("last_name")
    email = new_user.get("email")
    password = new_user.get("password")
    api.create_teacher_user(user_type, email, password, first_name, last_name)
    return "Success"

@app.route("/api/login/", methods=['POST'])
def login_user():
    user_to_login = json.loads(request.data)
    email = user_to_login.get("email")
    password = user_to_login.get("password")
    user = api.get_user(email, password)
    session['user'] = user.id
    return "Success"


@app.route("/api/logout/", methods=['POST'])
def process_logout():
    api.logout()


if __name__ == "__main__":
    app.run(debug = True)