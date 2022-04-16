from flask import Flask,json,request
from flask import jsonify
from db_models.models import CarVal,DilerVal
from werkzeug.exceptions import BadRequest
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)

#config параметры
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1@localhost/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SECRET_KEY'] = app.secret_key
db=SQLAlchemy(app)


# Для MVC надо таблицы вынести в db_models, для удобства оставил здесь
class Dilers(db.Model):
    __tablename__ = "dilers"
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(100))
    address=db.Column(db.String(200))
    cars = db.relationship("Cars",backref="dilers",cascade="all, delete, delete-orphan")

    def __repr__(self):
        return f"""{self.id,self.name,self.address}"""

    @property
    def serialize(self)->dict:
        return {
            "id":self.id,
            "name":self.name,
            "address": self.address
        }


class Cars(db.Model):
    __tablename__ = "cars"
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(100),default="unknown" )
    sold = db.Column(db.Boolean(),default=False)
    year_of_manufacture=db.Column(db.Date())
    color = db.Column(db.String(50))
    broken = db.Column(db.Boolean(),default=False)
    price = db.Column(db.Integer,default=100000)
    num_owners = db.Column(db.Integer,default=0)
    diler_id = db.Column(
        db.Integer,db.ForeignKey('dilers.id',ondelete='cascade'),
        nullable=False
    )

    def __repr__(self):
        return f"""{
            self.id,self.name,self.sold,self.year_of_manufacture,
            self.color,self.broken,self.price,self.num_owners,self.diler_id
        }"""

    @property
    def serialize(self)->dict:
        return {
            "id" : self.id,
            "name" : self.name,
            "sold" : self.sold,
            "year_of_manufacture" : self.year_of_manufacture,
            "color" : self.color,
            "broken" : self.broken,
            "price" : self.price,
            "num_owners" : self.num_owners,
            "diler_id" : self.diler_id
        }
db.create_all()
db.init_app(app)

#роуты

#дилеры
@app.route('/',methods=["GET"])
@app.route('/dilers',methods=["POST","GET"])
def get_post_dilers():
    """Get or post data about dilers"""
    if request.method =="POST":
        dilerload = request.json
        dilerload = DilerVal.parse_obj(dilerload).dict()
        diler = Dilers(
            name=dilerload['name'],
            address=dilerload['address']
        )
        try:
            db.session.add(diler)
            db.session.commit()
        except Exception:
            raise BadRequest("Unsupported request parameter!")
        response = app.response_class(
            response=json.dumps(dilerload),
            status=201,
            mimetype="application/json"
        )
        return  response
    else:
        res=db.session.query(Dilers)
        res=[x.serialize for x in res.all()]
        res={"dilers_table":res}
        response = app.response_class(
            response=json.dumps(res),
            status=200,
            mimetype="application/json"
        )
        return  response

@app.route('/custom_diler/<val>',methods=["GET"])
def get_diler(val):
    """Get custom diler data"""
    res=val.split("=")
    if res[0]=="id":
        res=db.session.query(Dilers).filter_by(id=int(res[1]))
    elif res[0]=="name":
        res = db.session.query(Dilers).filter_by(name=res[1])
    elif res[0]=="address":
        res = db.session.query(Dilers).filter_by(address=res[1])
    else:
        raise BadRequest("Invalid parameter!")
    res = [x.serialize for x in res.all()]
    res = {"dilers_table": res}
    response = app.response_class(
        response=json.dumps(res),
        status=200,
        mimetype="application/json"
    )
    return response

@app.put("/custom_diler/<int:id>")
def update_diler(id):
    """Update current diler data"""
    dilerload = request.json
    print(id)
    try:
        dilerload = DilerVal.parse_obj(dilerload).dict()
        Dilers.query.filter_by(id=id).update(dilerload)
        db.session.commit()
    except Exception:
        raise BadRequest("Validation error!")
    response = app.response_class(
        response=json.dumps(dilerload),
        status=201,
        mimetype="application/json"
    )
    return response

@app.delete("/custom_diler/<int:id>")
def delete_diler(id):
    """Delete current diler data"""

    try:
        Dilers.query.filter_by(id=id).delete()
        db.session.commit()
    except Exception:
        raise BadRequest("Validation error!")
    return jsonify("Success")

#авто
@app.route('/cars',methods=["POST","GET"])
def get_post_cars():
    """Get or post data about cars"""
    if request.method =="POST":
        carsload = request.json
        carsload = CarVal.parse_obj(carsload).dict()
        car = Cars(
            name = carsload['name'],
            sold = carsload['sold'],
            year_of_manufacture=carsload['year_of_manufacture'],
            color = carsload['color'],
            broken = carsload['broken'],
            price = carsload['price'],
            num_owners = carsload['num_owners'],
            diler_id = carsload['diler_id']
        )
        try:
            db.session.add(car)
            db.session.commit()
        except Exception:
            raise BadRequest("Unsupported request parameter!")
        response = app.response_class(
            response=json.dumps(carsload),
            status=201,
            mimetype="application/json"
        )
        return response
    else:
        res=db.session.query(Cars)
        res=[x.serialize for x in res.all()]
        res={"cars_table":res}
        response = app.response_class(
            response=json.dumps(res),
            status=201,
            mimetype="application/json"
        )
        return response


@app.put("/custom_car/<int:id>")
def update_car(id):
    """Update current car data"""
    carload = request.json

    try:
        carload = CarVal.parse_obj(carload).dict()
        Cars.query.filter_by(id=id).update(carload)
        db.session.commit()
    except Exception:
        raise BadRequest("Validation error!")
    response = app.response_class(
        response=json.dumps(carload),
        status=201,
        mimetype="application/json"
    )
    return response

@app.delete("/custom_car/<int:id>")
def delete_car(id):
    """Delete current car data"""
    try:
        Cars.query.filter_by(id=id).delete()
        db.session.commit()
    except Exception:
        raise BadRequest("Validation error!")
    return jsonify("Success")

@app.route('/custom_car/<val>',methods=["GET"])
def get_car(val):
    """Get custom car data"""
    res=val.split("=")
    if res[0]=="id":
        res=db.session.query(Cars).filter_by(id=int(res[1]))
    elif res[0]=="name":
        res = db.session.query(Cars).filter_by(name=res[1])
    elif res[0]=="sold":
        res = db.session.query(Cars).filter_by(sold=True if res[1].lower()=="true" else False)
    elif res[0] == "color":
        res = db.session.query(Cars).filter_by(color=res[1])
    elif res[0] == "broken":
        res = db.session.query(Cars).filter_by(broken=True if res[1].lower()=="true" else False)
    elif res[0] == "price":
        res = db.session.query(Cars).filter_by(price=int(res[1]))
    elif res[0] == "num_owners":
        res = db.session.query(Cars).filter_by(num_owners=int(res[1]))
    elif res[0] == "diler_id":
        res = db.session.query(Cars).diler_id(num_owners=int(res[1]))
    else:
        raise BadRequest("Invalid parameter!")
    res = [x.serialize for x in res.all()]
    res = {"car_table": res}
    response = app.response_class(
        response=json.dumps(res),
        status=200,
        mimetype="application/json"
    )
    return response

if __name__ == '__main__':
    app.run()
