from app import app
from models import House

with app.app_context():

    houses = House.query.all()

    for house in houses:

        print("ID:", house.id)
        print("Title:", house.title)
        print("Price:", house.price)
        print("City:", house.city)
        print("------------------")