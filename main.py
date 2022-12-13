import os

os.system("flask run")
os.system("flask db init")
os.system("flask db migrate")
os.system("flask db upgrade")


from app import app, db
from app.models import User

u = User(username='demo', email='demo@example.com')
u.set_password("demo")
db.session.add(u)
db.session.commit()
