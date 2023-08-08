from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from random import randint

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy()  # create db extension
db.init_app(app)  # initialise app


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        # Method 1.
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            # Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            dictionary[column.name] = getattr(self, column.name)
        return dictionary

        # # Method 2. Altenatively use Dictionary Comprehension to do the same thing.
        # return {column.name: getattr(self, column.name) for column in self.__table__.columns}

with app.app_context():
    db.create_all()



def str_to_bool(v):
    if v in ['True', ' true', 'T', 't', 'Yes', 'yes', 'y', '1']:
        return True
    else:
        return False

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/random")
def random():
    if request.method == 'GET':
        max_id = Cafe.query.order_by(Cafe.id.desc()).first().id
        rand_cafe = randint(1, max_id)
        rand_cafe = Cafe.query.filter_by(id=rand_cafe).first()
        # alternative method:
        # cafes = db.session.query(Cafe).all()
        # random_cafe = random.choice(cafes)
        # return rand_cafe.name

        # can use dict method to jsonify
        dict_cafe = rand_cafe.to_dict()
        print(dict_cafe)
        return jsonify(cafe=rand_cafe.to_dict())

        #basic method
        # return jsonify(id=rand_cafe.id,
        #                name=rand_cafe.name,
        #                map_url=rand_cafe.map_url,
        #                img_url=rand_cafe.img_url,
        #                location=rand_cafe.location,
        #                seats=rand_cafe.seats,
        #                has_toilet=rand_cafe.has_toilet,
        #                has_wifi=rand_cafe.has_wifi,
        #                has_sockets=rand_cafe.has_sockets,
        #                can_take_calls=rand_cafe.can_take_calls,
        #                coffee_price=rand_cafe.coffee_price)

        # optional grouping of json
        # return jsonify(cafe={
        #     # Omit the id from the response
        #     # "id": random_cafe.id,
        #     "name": random_cafe.name,
        #     "map_url": random_cafe.map_url,
        #     "img_url": random_cafe.img_url,
        #     "location": random_cafe.location,
        #
        #     # Put some properties in a sub-category
        #     "amenities": {
        #         "seats": random_cafe.seats,
        #         "has_toilet": random_cafe.has_toilet,
        #         "has_wifi": random_cafe.has_wifi,
        #         "has_sockets": random_cafe.has_sockets,
        #         "can_take_calls": random_cafe.can_take_calls,
        #         "coffee_price": random_cafe.coffee_price,
        #     }
        # }
    return 'none'

@app.route("/all")
def all():
    cafes = db.session.query(Cafe).all()
    # cafe_list = []
    # for cafe in cafes:
    #     dict_cafe = cafe.to_dict()
    #     print(dict_cafe)
    #     cafe_list.append(dict_cafe)
    # return jsonify(cafes=cafe_list)
    return jsonify(cafes=[cafe.to_dict() for cafe in cafes])

@app.route("/search")
def search():
    location = request.args.get('loc')
    cafes = Cafe.query.filter_by(location=location)
    if cafes.first():
        return jsonify(cafes=[cafe.to_dict() for cafe in cafes])
    else:
        return jsonify(error={'Not Found':'No cafes at that location'})


@app.route("/add", methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        data = request.form.to_dict()
        print(data)
        if data:
            new_cafe = Cafe(name=request.form["name"],
                            map_url=request.form["map_url"],
                            img_url=request.form["img_url"],
                            location=request.form["location"],
                            seats=request.form["seats"],
                            has_toilet=str_to_bool(request.form["has_toilet"]),
                            has_wifi=str_to_bool(request.form["has_wifi"]),
                            has_sockets=str_to_bool(request.form["has_sockets"]),
                            can_take_calls=str_to_bool(request.form["can_take_calls"]),
                            coffee_price=request.form["coffee_price"]
                            )
            db.session.add(new_cafe)
            db.session.commit()
            return jsonify(response={'Success': 'Added cafe'})
        else:
            return jsonify(response={'error': 'Cafe not added, try again'})


@app.route("/update-price/<int:cafe_id>", methods=['PATCH'])
def update(cafe_id):
    new_price = request.args.get('new_price')
    print(cafe_id)
    if new_price:
        print('price received')
        max_id = Cafe.query.order_by(Cafe.id.desc()).first().id
        if cafe_id <= max_id and cafe_id > 0:
            # Note, could just try get the cafe from the SQL session, and
            # run 'if cafe' to check if the variable has any content
            print('id valid')
            cafe = db.session.query(Cafe).get(cafe_id)
            print(cafe.coffee_price)
            cafe.coffee_price = new_price
            db.session.commit()
            return jsonify(response={'Success': 'Price updated'})
        else:
            return jsonify(response={'Error': 'id invalid'})
    else:
        return jsonify(response={'Error': 'no new price received'})

@app.route("/report-closed/<int:cafe_id>", methods=['DELETE'])
def delete(cafe_id):
    api_key = request.args.get('api-key')
    if api_key == 'TopSecretAPIKey':
        cafe = db.session.query(Cafe).get(cafe_id)
        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response={'Success': 'Cafe deleted'})
        else:
            return jsonify(response={'Error': 'api-key invalid'})
    else:
        return jsonify(response={'Error': 'cafe id invalid'})


## HTTP GET - Read Record

## HTTP POST - Create Record

## HTTP PUT/PATCH - Update Record

## HTTP DELETE - Delete Record


if __name__ == '__main__':
    app.run(debug=True)
