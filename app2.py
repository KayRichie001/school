import datetime

from flask import Flask, render_template, request, redirect,jsonify, flash, url_for, send_from_directory, session, send_file
import sqlite3, os, database, document_functions, json,requests
import io
from requests.auth import HTTPBasicAuth
from reportlab.pdfgen import canvas
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'My_Secret_Key'
admission_no = None
TOTAL_FEES = 2000

@app.route('/', methods=['GET', 'POST'])
def login():
    global admission_no
    if request.method == 'POST':

        admission_no = request.form['admission_no']
        password = request.form['password']

        with sqlite3.connect('student.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*)
                FROM logins
                WHERE admission_no = ? AND password = ?
            ''', (admission_no, password))

            count = cursor.fetchone()[0]
            if count > 0:  # If the student exists,
                return redirect(url_for('home'))
            else:
                with sqlite3.connect('admin.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        SELECT COUNT(*)
                        FROM logins
                        WHERE position = ? AND password = ?
                    ''', (admission_no, password))

                    count = cursor.fetchone()[0]
                    if count > 0:
                        return redirect(url_for('admin_dashboard'))
                    else:
                        return render_template('login.html', error="Invalid admission number or password")
    return render_template('login.html')


@app.route('/home')
def home():
    return render_template('home.html', name=database.get_first_name(admission_no),
                           greeting=document_functions.greet_based_on_time(), admission_no=document_functions.replace_slash_with_dot(admission_no))


@app.route('/fee')
def fee():
    return render_template('fee.html')


@app.route('/examinations')
def examinations():
    return render_template("examtrend.html")


@app.route('/settings')
def settings():
    return render_template('settings.html')


@app.route('/logout')
def logout():
    return redirect(url_for('login'))


#_______________________________________________________________________________________
#=================================================================================#
#----------------ADMIN----------------------
# List of subjects (make sure the names match the ones in the HTML form)
subjects = ['mathematics', 'biology', 'chemistry', 'physics', 'geography', 'business', 'english', 'kiswahili', 'cre',
            'french']


@app.route('/admin_dash')
def admin_dashboard():
    admission_no = None
    return render_template("admin_dashboard.html", admission_no=admission_no)


@app.route('/submit_marks', methods=['POST'])
def submit_marks():
    # Extract marks from the form and put them into a list
    marks_list = [int(request.form[subject]) for subject in subjects]

    # For demonstration, let's print the marks list
    print("Marks List:", marks_list)
    admission_no = document_functions.replace_slash_with_slash(request.form['admission_no'])
    # You can now use marks_list for further processing, such as inserting into a database
    database.insert_marks(admission_no, marks_list)
    database.set_average(admission_no)

    return "Marks submitted successfully!"


@app.route('/submit_selection', methods=['GET', 'POST'])
def submit_selection():
    return redirect(url_for('enter_student_marks'))


@app.route('/submit_check', methods=['POST'])
def submit_check():
    marks_list = [int(request.form[subject]) for subject in subjects]
    database.insert_marks(document_functions.replace_slash_with_slash(request.form['admission_no']), marks_list)


if admission_no:
    ad = document_functions.replace_slash_with_dot(admission_no)


@app.route('/type_check')
def type_check():
    return render_template('type_check.html')


@app.route('/students', methods=['GET', 'POST'])
def view_students():
    year = request.form['year']
    term = int(request.form['term'])
    exam_type = request.form['type']
    grade = request.form['class']
    data = database.get_students_marks_filtered(year, term, exam_type, grade)

    return render_template('exam_list.html', students=data)


@app.route('/enter_marks/<admission_no>', methods=['GET', 'POST'])
def enter_student_marks(admission_no):
    admission_n = document_functions.replace_slash_with_slash(admission_no)
    year = request.form['year']
    term = int(request.form['term'])
    exam_type = request.form['type']
    database.insert_time(admission_n, year, term, exam_type)

    return render_template('enter_marks.html', admission_no=admission_n)


@app.route('/view_students_marks')
def view_students_marks():
    return render_template('view_students_marks.html', students=database.view_students())


@app.route('/<admission_no>')
def enter_marks(admission_no):
    admission_n = document_functions.replace_slash_with_slash(admission_no)
    return render_template('type_checker.html', admission_no=admission_no,
                           first_name=database.get_first_name(admission_n))


@app.route('/exam_list')
def students_results():
    return render_template('exam_list.html', students=database.get_all_students_exams())


#-------------Upload a Memo
# Set the directories for file uploads
BOOKS_FOLDER = 'static/uploads/books/'
IMAGES_FOLDER = 'static/uploads/images/'
app.config['BOOKS_FOLDER'] = BOOKS_FOLDER
app.config['IMAGES_FOLDER'] = IMAGES_FOLDER

# Ensure the upload folders exist
os.makedirs(BOOKS_FOLDER, exist_ok=True)
os.makedirs(IMAGES_FOLDER, exist_ok=True)


@app.route('/memo')
def index():
    # List all uploaded books with their front images
    books = []
    for filename in os.listdir(app.config['BOOKS_FOLDER']):
        image_name = os.path.splitext(filename)[0] + ".jpg"  # Assuming images are uploaded as .jpg
        image_path = os.path.join(app.config['IMAGES_FOLDER'], image_name)
        books.append({
            "filename": filename,
            "image": image_name if os.path.exists(image_path) else None
        })
    return render_template('index.html', books=books)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files.get('file')
        image = request.files.get('image')

        if file and file.filename.endswith('.pdf'):
            # Save the PDF book
            filepath = os.path.join(app.config['BOOKS_FOLDER'], file.filename)
            file.save(filepath)

            # Save the front image (if provided)
            if image and image.filename.endswith(('.jpg', '.jpeg', '.png')):
                image_name = os.path.splitext(file.filename)[0] + ".jpg"
                imagepath = os.path.join(app.config['IMAGES_FOLDER'], image_name)
                image.save(imagepath)

            return redirect(url_for('index'))

    return render_template('upload.html')


@app.route('/download/<filename>')
def download(filename):
    # Allow users to download the uploaded books
    return send_from_directory(app.config['BOOKS_FOLDER'], filename, as_attachment=True)


@app.route('/delete/<filename>', methods=['POST'])
def delete(filename):
    # Delete the PDF book and its front image
    book_path = os.path.join(app.config['BOOKS_FOLDER'], filename)
    image_name = os.path.splitext(filename)[0] + ".jpg"
    image_path = os.path.join(app.config['IMAGES_FOLDER'], image_name)

    if os.path.exists(book_path):
        os.remove(book_path)
    if os.path.exists(image_path):
        os.remove(image_path)

    return redirect(url_for('index'))


@app.route('/view_memo')
def view_memo():
    books = []
    for filename in os.listdir(app.config['BOOKS_FOLDER']):
        image_name = os.path.splitext(filename)[0] + ".jpg"  # Assuming images are uploaded as .jpg
        image_path = os.path.join(app.config['IMAGES_FOLDER'], image_name)
        books.append({
            "filename": filename,
            "image": image_name if os.path.exists(image_path) else None
        })
    return render_template("view_memo.html", books=books)


#------------Change Profile--------------
# app.secret_key = 'your_secret_key'
# # Set the upload folder
# UPLOAD_FOLDER = 'static/uploads/'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#
# # Ensure the upload directory exists
# if not os.path.exists(UPLOAD_FOLDER):
#     os.makedirs(UPLOAD_FOLDER)
#
# @app.route('/change_profile', methods=['GET', 'POST'])
# def change_profile():
#     if request.method == 'POST':
#         # Check if the post request has the file part
#         if 'profile_pic' not in request.files:
#             return 'No file part'
#         file = request.files['profile_pic']
#         if file.filename == '':
#             return 'No selected file'
#         if file:
#             # Save the file
#             filename = file.filename
#             file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#
#             # Store the filename in session or database (here, session for simplicity)
#             session['profile_picture'] = filename
#
#             return redirect(url_for('dashb'))
#     return render_template('change_profile.html')
def load_user_data(username):
    if os.path.exists('user_data.json'):
        with open('user_data.json', 'r') as f:
            try:
                data = json.load(f)
                return data.get(username, {"username": username, "profile_picture": None})
            except json.JSONDecodeError:
                return {"username": username, "profile_picture": None}
    else:
        return {"username": username, "profile_picture": None}


# Save user data to a JSON file
def save_user_data(username, user_data):
    data = {}
    if os.path.exists('user_data.json'):
        with open('user_data.json', 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                pass
    data[username] = user_data
    with open('user_data.json', 'w') as f:
        json.dump(data, f)


# Route for user profile
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    username = request.args.get('username')
    user_data = load_user_data(username)

    if request.method == 'POST':
        if 'profile_picture' in request.files:
            profile_picture = request.files['profile_picture']
            if profile_picture.filename != '':
                profile_pic_path = f'static/uploads/{username}_profile_picture.jpg'
                profile_picture.save(profile_pic_path)
                user_data['profile_picture'] = profile_pic_path
                save_user_data(username, user_data)
                return redirect(url_for('dashb', username=username))

    return render_template('dashboard.html', username=username, profile_picture=user_data['profile_picture'])


#----------------Change Password
@app.route('/change_password')
def change_password():
    return render_template('change_password.html')


@app.route('/compiler')
def compiler():
    return render_template('compiler.html')


@app.route('/manager')
def manager():
    return render_template('manager.html')


@app.route('/dash')
def dashb():
    # Get the profile picture from session or set a default one
    profile_picture = session.get('profile_picture', 'person1.png')
    username = request.args.get('username')
    user_data = load_user_data(username)
    admission=document_functions.replace_slash_with_dot(admission_no)
    if request.method == 'POST':
        if 'profile_picture' in request.files:
            profile_picture = request.files['profile_picture']
            if profile_picture.filename != '':
                profile_pic_path = f'static/uploads/{username}_profile_picture.jpg'
                profile_picture.save(profile_pic_path)
                user_data['profile_picture'] = profile_pic_path
                save_user_data(username, user_data)

    return render_template('dashboard.html', profile_picture=user_data['profile_picture'],admission_no=admission)


# @app.route('/dash')
# def dashb():
#     return render_template("dashboard.html")
#Route to display Students with Fee balances
@app.route('/students_with_balance')
def students_with_balance():
    students = database.get_students_with_balance()
    return render_template('students_with_balance.html', students=students)


#===============Add Student
@app.route('/add_or_remove')
def add_or_remove_student():
    return render_template("add_or_remove_student.html")


@app.route('/add_student')
def add():
    return render_template('add_student.html')


@app.route('/signup_success')
def signup_success():
    return render_template('signup_success.html')


@app.route('/submit_signup', methods=['POST'])
def submit_signup():
    first_name = request.form['first_name']
    middle_name = request.form['middle_name']
    last_name = request.form['last_name']
    age = request.form['age']
    gender = request.form['gender']
    grade = request.form['grade']
    sickness = request.form['sickness']
    treatment = request.form['treatment']
    admission_no = request.form['admission_no']
    existing_student = database.student_exist(admission_no)
    if existing_student:
        # Admission number already exists
        flash("Error: A student with this admission number already exists.", "error")
        return redirect(url_for('index'))

    database.add_someone(admission_no, first_name, middle_name, last_name, gender, age)
    database.add_level(admission_no, grade)
    database.put_ill_students(admission_no, sickness, treatment)
    database.add_login(admission_no, last_name)
    return redirect(url_for('signup_success'))


#=================Non Compliant Student
@app.route('/non_compliant_students')
def non_compliant_students():
    students = database.non_compliant_students()
    return render_template('non_compliant_students.html', students=students)


#===============Ill Students
@app.route('/health_issue')
def health_issue():
    students = database.get_ill_students()
    return render_template('health_issue.html', students=students)
#======================Fee Payment==============================================



def get_student_data(admission_number):
    conn = sqlite3.connect('fees.db')
    cursor = conn.cursor()
    cursor.execute('SELECT total_paid, remaining_balance FROM students WHERE admission_number = ?', (admission_number,))
    result = cursor.fetchone()
    conn.close()
    return result if result else (0, TOTAL_FEES)

def update_student_fees(admission_number, amount_paid):
    conn = sqlite3.connect('fees.db')
    cursor = conn.cursor()

    previous_total_paid, _ = get_student_data(admission_number)
    total_paid = previous_total_paid + amount_paid
    remaining_balance = TOTAL_FEES - total_paid

    cursor.execute('''
        INSERT INTO students (admission_number, total_paid, remaining_balance)
        VALUES (?, ?, ?)
        ON CONFLICT(admission_number)
        DO UPDATE SET total_paid = excluded.total_paid, remaining_balance = excluded.remaining_balance
    ''', (admission_number, total_paid, remaining_balance))

    # Record the transaction in payment_history with remaining balance
    date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('''
        INSERT INTO payment_history (admission_number, amount_paid, remaining_balance, date_time)
        VALUES (?, ?, ?, ?)
    ''', (admission_number, amount_paid, remaining_balance, date_time))

    conn.commit()
    conn.close()

    return total_paid, remaining_balance

def get_payment_history(admission_number):
    conn = sqlite3.connect('fees.db')
    cursor = conn.cursor()
    cursor.execute('SELECT amount_paid, remaining_balance, date_time FROM payment_history WHERE admission_number = ?', (admission_number,))
    history = cursor.fetchall()
    conn.close()
    return history

@app.route('/fee_payment')
def index1():
    return render_template('fees_payment.html')

@app.route('/submit', methods=['POST'])
def submit():
    admission_number = request.form['admissionNumber']
    fee_paid = float(request.form['feePaid'])

    total_paid, remaining_balance = update_student_fees(admission_number, fee_paid)

    return jsonify({
        'total_paid': total_paid,
        'remaining_balance': remaining_balance
    })

@app.route('/receipt/<admission_number>', methods=['GET'])
def download_receipt(admission_number):
    total_paid, remaining_balance = get_student_data(admission_number)

    # Generate PDF receipt
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)

    p.drawString(100, 750, f"Receipt for Admission Number: {document_functions.replace_slash_with_slash(admission_number)}")
    p.drawString(100, 730, f"Total Paid: sh.{total_paid} ")
    p.drawString(100, 710, f"Remaining Balance: sh.{remaining_balance} ")
    p.drawString(100, 690, "Thank you for your payment.")

    p.showPage()
    p.save()

    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"receipt_{admission_number}.pdf", mimetype='application/pdf')

@app.route('/history/<admission_number>', methods=['GET'])
def view_history(admission_number):
    admission_number = document_functions.replace_slash_with_slash(admission_number)
    history = get_payment_history(admission_number)
    return render_template('payment_history.html', history=history, admission_number=document_functions.replace_slash_with_dot(admission_number))

@app.route('/download_history/<admission_number>', methods=['GET'])
def download_history(admission_number):
    history = get_payment_history(document_functions.replace_slash_with_slash(admission_number))

    # Generate PDF for payment history in tabular form
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    width, height = p._pagesize

    p.drawString(100, height - 50, f"Payment History for Admission Number: {admission_number}")

    # Draw table headers
    x_offset = 100
    y_offset = height - 100
    p.drawString(x_offset, y_offset, "Amount Paid")
    p.drawString(x_offset + 150, y_offset, "Remaining Balance")
    p.drawString(x_offset + 300, y_offset, "Date & Time")
    y_offset -= 20

    # Draw table data
    for amount_paid, remaining_balance, date_time in history:
        p.drawString(x_offset, y_offset, f"sh.{amount_paid}")
        p.drawString(x_offset + 150, y_offset, f"sh.{remaining_balance} ")
        p.drawString(x_offset + 300, y_offset, date_time)
        y_offset -= 20
        if y_offset < 50:  # Start a new page if the content exceeds the page height
            p.showPage()
            y_offset = height - 50

    p.showPage()
    p.save()

    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"payment_history_{admission_number}.pdf", mimetype='application/pdf')


if __name__ == '__main__':
    if not os.path.exists('static/uploads'):
        os.makedirs('static/uploads')
    database.add_all_tables()
    app.run(debug=True)
