from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from flask_marshmallow import Marshmallow
from datetime import date
from typing import List
from marshmallow import ValidationError
from sqlalchemy import select, delete






app = Flask(__name__) 
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Acc19947mec@localhost/ecommerce_api'


class Base(DeclarativeBase):
    pass 

db = SQLAlchemy(app, model_class=Base)
ma = Marshmallow(app)

#====================== MODELS ==============================================

class User(Base):
    
    __tablename__ = 'User' 

    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(225), nullable=False)
    email: Mapped[str] = mapped_column(db.String(225))
    address: Mapped[str] = mapped_column(db.String(225))
    
    orders: Mapped[List["Orders"]] = relationship(back_populates='user') 
    

order_products = db.Table(
    "Order_Products",
    Base.metadata, 
    db.Column('order_id', db.ForeignKey('orders.id')),
    db.Column('product_id', db.ForeignKey('products.id'))
)


class Orders(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(primary_key=True)
    order_date: Mapped[date] = mapped_column(db.Date, nullable=False)
   
    user_id: Mapped[int] = mapped_column(db.ForeignKey('User.id'))
    #creating a many-to-one relationship to Customer table
    user: Mapped["User"] = relationship("User", back_populates='orders')
 
    products: Mapped[List['Products']] = relationship(secondary=order_products, back_populates="orders")
    
class Products(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_name: Mapped[str] = mapped_column(db.String(255), nullable=False )
    price: Mapped[float] = mapped_column(db.Float, nullable=False)
    orders: Mapped[List['Orders']] = relationship(secondary=order_products, back_populates="products")
     
# Initialize the database & create tables
with app.app_context():
    # db.drop_all()
    
    db.create_all()
 
#============================ SCHEMAS ==================================

# Define User Schema
class UserSchema(ma.SQLAlchemyAutoSchema): 
    class Meta:
        model = User

class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Products

class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Orders
        include_fk = True 
        
user_schema = UserSchema()
users_schema = UserSchema(many=True)

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)

# =================== API ROUTES (WITH FLASK) ==============
@app.route('/')
def home():
    return "Home"

#=============== API ROUTES: Customer CRUD==================

# Create a customer with a POST request
@app.route("/users", methods=["POST"])
def add_user():
    try:
        user_data = user_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_user = User(name=user_data['name'], email=user_data['email'], address=user_data['address'])
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"Message": "New User added successfully!",
                    "user": user_schema.dump(new_user)}), 201
    
# Get all users using a GET method
@app.route("/users", methods=['GET'])
def get_users():
    query = select(User)
    result = db.session.execute(query).scalars() 
    users = result.all() 
    return users_schema.jsonify(users), 200

# Get specific user using a GET method and dynamic route
@app.route("/users/<int:id>", methods=['GET'])
def get_user(id):
    user = db.session.get(User, id)
    return user_schema.jsonify(user), 200
 
@app.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    user = db.session.get(User, id)

    if not user:
        return jsonify({"message": "Invalid id"}), 400
    
    try:
        user_data = user_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    user.name = user_data['name']
    user.email = user_data['email']
    user.address = user_data['address']    

    db.commit()
    return user_schema.load(User), 200 
    

#DELETE 
@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = db.session.get(User, id)

    if not user:
        return jsonify({"message": "Invalid user id"}), 400
    
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message" : f"succesfully deleted user {id}"}), 200 




#=============== API ROUTES: Products CRUD==================


@app.route('/products', methods=['POST'])
def create_product():
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_product = Products(product_name=product_data['product_name'], price=product_data['price'])
    db.session.add(new_product)
    db.session.commit()

    return jsonify({"Messages": "New Product added!",
                    "product": product_schema.dump(new_product)}), 201

@app.route("/products", methods=['GET'])
def get_products():
    query = select(Products)
    result = db.session.execute(query).scalars() 
    products = result.all() 
    return products_schema.jsonify(products)

@app.route("/products/<int:id>", methods=['GET'])
def get_product(id):
    product = db.session.get(Products, id)
    return product_schema.jsonify(product), 200

@app.route('/products/<int:id>', method=['PUT'])
def update_product(id):
    product = db.session.get(Products, id)

    if not product:
        return jsonify({"message": "Invalid id"}), 400
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    product.name = product_data['name']
    product.price = product_data['price']

    db.commit()
    return product_schema.load(Products), 200

#DELETE 
@app.route('/productss/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = db.session.get(Products, id)

    if not product:
        return jsonify({"message": "Invalid user id"}), 400
    
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message" : f"succesfully deleted product {id}"}), 200 




        


    

#=============== API ROUTES: Order Operations ==================
#CREATE an ORDER
@app.route('/orders', methods=['POST'])
def add_order():
    try:
        order_data = order_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    # Retrieve the user by its id.
    user = db.session.get(User, order_data['user_id'])
    
    # Check if the user exists.
    if user:
        new_order = Orders(order_date=order_data['order_date'], user_id = order_data['user_id'])

        db.session.add(new_order)
        db.session.commit()

        return jsonify({"Message": "New Order Placed!",
                        "order": order_schema.dump(new_order)}), 201
    else:
        return jsonify({"message": "Invalid user id"}), 400
    
#Get all orders for a user
@app.route('/users/int:user_id/orders', methods=['GET'])
def get_user_orders(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found."}), 400
        return orders_schema.jsonify(user.orders), 200

@app.route('/orders/int:order_id/products', methods=['GET'])
def get_order_products(order_id):
    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({"error": "Order not found."}), 400
        return products_schema.jsonify(order.products), 200




#ADD ITEM TO ORDER
@app.route('/orders/<int:order_id>/add_product/<int:product_id>', methods=['PUT'])
def add_product(order_id, product_id):
    order = db.session.get(Orders, order_id) 
    product = db.session.get(Products, product_id)

    if order and product: 
        if product not in order.products: 
            order.products.append(product) 
            db.session.commit() 
            return jsonify({"Message": "Successfully added item to order."}), 200
        else:
            return jsonify({"Message": "Item is already included in this order."}), 400
    else:
        return jsonify({"Message": "Invalid order id or product id."}), 400

#remove product from order
@app.route('/orders/<int:order_id>/remove_product/<int:product_id>', methods=['DELETE'])
def remove_product_from_order(order_id, product_id):
    order = db.session.get(Orders, order_id)
    product = db.session.get(Products, product_id)

    if order and product:
        if product in order.products:
            order.products.remove(product)
            db.session.commit()
            return jsonify({"Message": "Successfully removed product from order."}), 200
        else:
            return jsonify({"Message": "Product not found in order."}), 400
    else:
        return jsonify({"Message": "Invalid order id or product id."}), 400


               





if __name__ == '__main__':
    app.run(debug=True)
    



