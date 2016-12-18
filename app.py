from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config.from_object('config')
app.secret_key = 'super secret key'

db = SQLAlchemy(app)

import models