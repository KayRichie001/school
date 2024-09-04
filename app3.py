# from flask import Flask, request, render_template
# import database
# import document_functions
#
# app = Flask(__name__)
#
# # List of subjects (make sure the names match the ones in the HTML form)
# subjects = ['mathematics', 'biology', 'chemistry', 'physics', 'geography', 'business', 'english', 'kiswahili', 'cre',
#             'french']
# @app.route('/')
# def admin_dashboard():
#     admission_no = None
#     return render_template("admin_dashboard.html",admission_no=admission_no)
#
# @app.route('/submit_marks', methods=['POST'])
# def submit_marks():
#     # Extract marks from the form and put them into a list
#     marks_list = [int(request.form[subject]) for subject in subjects]
#
#     # For demonstration, let's print the marks list
#     print("Marks List:", marks_list)
#
#     # You can now use marks_list for further processing, such as inserting into a database
#     database.insert_marks(request.form['admission_no'],marks_list)
#     return "Marks submitted successfully!"
#
# @app.route('/students')
# def view_students():
#     students=database.get_students_and_subjects()
#
#     return render_template('view_students.html', students=students)
#
# # @app.route('/enter_marks')
# # def enter_marks():
# #     return render_template('enter_marks.html')
# @app.route('/view_students_marks')
# def view_students_marks():
#     return render_template('view_students_marks.html', students=database.view_students())
# @app.route('/enter_marks/<admission_no>')
# def enter_marks(admission_no):
#     admission_n=document_functions.replace_slash_with_slash(admission_no)
#     print(admission_n)
#     return render_template('enter_marks.html', admission_no=admission_n)
#
#
# if __name__ == '__main__':
#     app.run(debug=True)
