# entry point
# The most important file. It directs traffic. 
# When a user clicks a link, 
# app.py decides which page to show them or what data to grab 
# from the database.

# app.py
from flask import Flask, render_template
from config import Config
from models import db

app = Flask(__name__)
app.config.from_object(Config)

# Link the database instance to this Flask application
db.init_app(app)

# MVP Core Route
@app.route('/')
def dashboard():
    # This renders your templates/dashboard.html file
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)