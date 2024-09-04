from flask import Flask, render_template, url_for

app = Flask(__name__)

# Sample student scores data (replace with actual data retrieval logic)

@app.route('/')
def dash():
    return render_template("dashboard.html")
@app.route('/settings')
def settings():
    return  render_template("settings.html")




if __name__ == '__main__':
    app.run(debug=True)
