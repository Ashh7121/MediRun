Clone the project:
git clone <your-repo-url>

Open the folder in VS Code.

Create their own Virtual Environment:
py -m venv venv

Activate it and install dependencies:
.\venv\Scripts\activate
pip install -r requirements.txt

Switch to their specific branch:
git checkout dev-alex (or whatever their name is)



delivery_app/
├── app.py              # Entry point
├── config.py           # Database URLs/Secret keys
├── requirements.txt    # List of dependencies
├── .gitignore          # Files to ignore
├── static/             # CSS, JS, and Images
│   ├── css/
│   └── js/
├── templates/          # HTML files
│   ├── base.html       # Parent template (Navbar/Footer)
│   ├── login.html      # Auth page
│   └── dashboard.html  # Delivery dashboard
└── models.py           # Database schemas (Drivers, Tasks, etc.)