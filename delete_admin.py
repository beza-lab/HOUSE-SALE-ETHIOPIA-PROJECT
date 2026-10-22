from app import app
from models import db, User

with app.app_context():

    admin = User.query.filter_by(
        username="admin"
    ).first()

    if admin:

        db.session.delete(admin)
        db.session.commit()

        print("Admin deleted")

    else:

        print("Admin not found")