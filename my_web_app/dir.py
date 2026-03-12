import os

# Root directory
project_name = "crypto_webapp"
base_path = os.path.join(os.getcwd(), project_name)

# Directory structure
dirs = [
    "app",
    "app/templates",
    "app/static",
    "app/static/css",
    "app/static/js",
    "instance",
    "migrations"
]

# Files to create with placeholder content
files = {
    "run.py": "# Entry point for Flask app\n\nfrom app import create_app\n\napp = create_app()\n\nif __name__ == '__main__':\n    app.run(debug=True)",
    "app/__init__.py": "# Flask app factory\n\nfrom flask import Flask\nfrom flask_sqlalchemy import SQLAlchemy\nfrom flask_login import LoginManager\n\ndb = SQLAlchemy()\nlogin_manager = LoginManager()\nlogin_manager.login_view = 'login'\n\ndef create_app():\n    app = Flask(__name__)\n    app.config.from_pyfile('../instance/config.py')\n\n    db.init_app(app)\n    login_manager.init_app(app)\n\n    from . import routes\n    app.register_blueprint(routes.bp)\n\n    return app",
    "app/routes.py": "# Flask routes\n\nfrom flask import Blueprint, render_template, redirect, url_for\n\nbp = Blueprint('routes', __name__)\n\n@bp.route('/')\ndef home():\n    return render_template('home.html')\n\n@bp.route('/login')\ndef login():\n    return render_template('login.html')\n\n@bp.route('/signup')\ndef signup():\n    return render_template('signup.html')",
    "app/models.py": "# Database models\n\nfrom . import db\nfrom flask_login import UserMixin\n\nclass User(UserMixin, db.Model):\n    id = db.Column(db.Integer, primary_key=True)\n    username = db.Column(db.String(150), nullable=False, unique=True)\n    email = db.Column(db.String(150), nullable=False, unique=True)\n    password = db.Column(db.String(150), nullable=False)",
    "app/forms.py": "# WTForms for login/signup\n\nfrom flask_wtf import FlaskForm\nfrom wtforms import StringField, PasswordField, SubmitField\nfrom wtforms.validators import InputRequired, Email, Length\n\nclass LoginForm(FlaskForm):\n    email = StringField('Email', validators=[InputRequired(), Email()])\n    password = PasswordField('Password', validators=[InputRequired()])\n    submit = SubmitField('Login')\n\nclass SignupForm(FlaskForm):\n    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=150)])\n    email = StringField('Email', validators=[InputRequired(), Email()])\n    password = PasswordField('Password', validators=[InputRequired(), Length(min=6)])\n    submit = SubmitField('Sign Up')",
    "app/templates/base.html": "<!-- Base template -->\n<!DOCTYPE html>\n<html>\n<head>\n    <title>{% block title %}Crypto WebApp{% endblock %}</title>\n    <link rel='stylesheet' href='{{ url_for(\"static\", filename=\"css/style.css\") }}'>\n</head>\n<body>\n    {% block content %}{% endblock %}\n</body>\n</html>",
    "app/templates/home.html": "{% extends 'base.html' %}\n{% block title %}Home{% endblock %}\n{% block content %}\n<h1>Welcome to Crypto WebApp</h1>\n<a href='/login'>Login</a> | <a href='/signup'>Signup</a>\n{% endblock %}",
    "app/templates/login.html": "{% extends 'base.html' %}\n{% block title %}Login{% endblock %}\n{% block content %}\n<h2>Login</h2>\n<form method='POST'>\n    {{ form.hidden_tag() }}\n    {{ form.email.label }} {{ form.email() }}<br>\n    {{ form.password.label }} {{ form.password() }}<br>\n    {{ form.submit() }}\n</form>\n{% endblock %}",
    "app/templates/signup.html": "{% extends 'base.html' %}\n{% block title %}Signup{% endblock %}\n{% block content %}\n<h2>Signup</h2>\n<form method='POST'>\n    {{ form.hidden_tag() }}\n    {{ form.username.label }} {{ form.username() }}<br>\n    {{ form.email.label }} {{ form.email() }}<br>\n    {{ form.password.label }} {{ form.password() }}<br>\n    {{ form.submit() }}\n</form>\n{% endblock %}",
    "instance/config.py": "# Configuration file\n\nSECRET_KEY = 'your-secret-key'\nSQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'\nSQLALCHEMY_TRACK_MODIFICATIONS = False",
    "requirements.txt": "Flask\nFlask-WTF\nFlask-Login\nFlask-SQLAlchemy"
}

# Create directories
for dir_path in dirs:
    os.makedirs(os.path.join(base_path, dir_path), exist_ok=True)

# Create files with placeholder content
for filepath, content in files.items():
    full_path = os.path.join(base_path, filepath)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print(f"✅ Flask project structure for '{project_name}' created successfully.")
