#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


# GET /restaurants
@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    restaurants_data = [restaurant.to_dict(only=('id', 'name', 'address')) for restaurant in restaurants]
    return make_response(jsonify(restaurants_data), 200)


# GET /restaurants/<int:id>
@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant_by_id(id):
    restaurant = Restaurant.query.filter(Restaurant.id == id).first()
    
    if restaurant:
        restaurant_data = restaurant.to_dict(only=('id', 'name', 'address', 'restaurant_pizzas'))
        return make_response(jsonify(restaurant_data), 200)
    else:
        return make_response(jsonify({"error": "Restaurant not found"}), 404)


# DELETE /restaurants/<int:id>
@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    restaurant = Restaurant.query.filter(Restaurant.id == id).first()
    
    if restaurant:
        db.session.delete(restaurant)
        db.session.commit()
        return make_response('', 204)
    else:
        return make_response(jsonify({"error": "Restaurant not found"}), 404)


# GET /pizzas
@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()
    pizzas_data = [pizza.to_dict(only=('id', 'name', 'ingredients')) for pizza in pizzas]
    return make_response(jsonify(pizzas_data), 200)


# POST /restaurant_pizzas
@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    data = request.get_json()
    
    try:
        # Create new RestaurantPizza
        new_restaurant_pizza = RestaurantPizza(
            price=data.get('price'),
            pizza_id=data.get('pizza_id'),
            restaurant_id=data.get('restaurant_id')
        )
        
        db.session.add(new_restaurant_pizza)
        db.session.commit()
        
        # Return the new RestaurantPizza with nested data
        response_data = new_restaurant_pizza.to_dict(only=('id', 'price', 'pizza_id', 'restaurant_id', 'pizza', 'restaurant'))
        return make_response(jsonify(response_data), 201)
        
    except ValueError as e:
        return make_response(jsonify({"errors": ["validation errors"]}), 400)
    except Exception as e:
        return make_response(jsonify({"errors": ["validation errors"]}), 400)


if __name__ == "__main__":
    app.run(port=5555, debug=True)