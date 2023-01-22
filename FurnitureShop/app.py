from flask import Flask,jsonify,request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column,Integer,String, Float, Boolean, ForeignKey,Table,DateTime, create_engine
from sqlalchemy.orm import declarative_base, relationship,backref
import os
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from flask_mail import Mail,Message
from random import *
from sqlalchemy import exc
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import jwt
import datetime
from functools import wraps


app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:///'+os.path.join(basedir,'furnitureShop.db')
app.config['JWT_SECRET_KEY'] = 'super-secret'
app.config['SECRET_KEY'] = 'thisissecret'


# user = 'k'
# password = 'Kruthik007'
# host = '127.0.0.1'
# port = 3306
# database = 'furnitureShop'

# try:
#
#     # GET THE CONNECTION OBJECT (ENGINE) FOR THE DATABASE
#     db_my = create_engine(
#         url="mysql+pymysql://{0}:{1}@{2}:{3}/{4}".format(
#             user, password, host, port, database
#         ))
#     # db_my.create_all()
#     print(
#         f"Connection to the {host} for user {user} created successfully.")
# except Exception as ex:
#     print("Connection could not be made due to the following error: \n", ex)

# url="mysql+pymysql://{0}:{1}@{2}:{3}/{4}".format(user, password, host, port, database)
# app.config['SQLALCHEMY_DATABASE_URI'] = url


db = SQLAlchemy(app)
ma = Marshmallow(app)
jwt_t = JWTManager(app)
mail = Mail(app)


otp=randint(000000,999999)

#--------------------------- Tables -----------------------------
class User(db.Model):
    __tablename__ = 'users'
    user_id  = Column(Integer, primary_key = True)
    user_name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
    is_admin = Column(Boolean,unique=False,default=False)
    is_active = is_active = Column(Boolean, unique=False,default=True)
    public_id = db.Column(db.String(50), unique=True)

class Products(db.Model):
    __tablename__ = 'products'
    product_id  = Column(Integer, primary_key = True)
    product_name = Column(String)
    product_category = Column(String)
    price = Column(Float)
    quantity = Column(Integer)


class User_Profile(db.Model):
    __tablename__= 'user_profile'
    user_profile_id = Column(Integer,primary_key=True)
    #user_id = Column(Integer,ForeignKey("users.user_id"))
    user_email = Column(String, ForeignKey("users.email"),unique=True)
    gender = Column(String)
    age = Column(Integer)
    profession = Column(String)
    mobile_number = Column(db.Integer,unique=True)
    parent = relationship("User",backref = backref("child",uselist=False))


class Cart(db.Model):
    __tablename__ = "cart"
    # add final price to it and create an intermediatery table
    cart_id = Column(Integer,primary_key = True) # change this line to cart_id
    user_email = Column(String, ForeignKey("users.email"))
    address = Column(String)
    pincode = Column(Integer)
    state = Column(String)
    country = Column(String)
    product_id = Column(Integer, ForeignKey("products.product_id"))
    product_name = Column(String)
    order_status = Column(String)
    order_status_created_at = Column(DateTime, default=datetime.datetime.now())
    # product = Column(Integer, ForeignKey("products.product_id"))
    quantity = Column(Integer,default=1)
    final_price = Column(Float)


class Order_Details(db.Model):
    __tablename__ = "orders.detail"
    user_email = Column(String, ForeignKey("users.email"))
    cart_id = Column(Integer,ForeignKey("cart.cart_id"))
    order_id = Column(Integer, primary_key=True,unique=True)
    product_id = Column(Integer, ForeignKey("products.product_id"))
    order_created_at = Column(DateTime, default=None)
    is_approved = Column(Boolean, default=False)
    order_aproved_at = Column(DateTime, default=None)
    is_fullfilled = Column(Boolean, default=False)
    order_fullfilled_at = Column(DateTime, default=None)
    is_cancelled = Column(Boolean, default=False)
    order_cancelled_at = Column(DateTime, default=None)


class Orders_Pending_Approval(db.Model):
    __tablename__ = "orders_pending_approval"
    id = Column(Integer,primary_key = True)
    cart_id = Column(Integer,ForeignKey("cart.cart_id"))
    product_id = Column(Integer, ForeignKey("products.product_id"))
    order_created_at = Column(DateTime, ForeignKey("cart.order_status_created_at"),
                              default=datetime.datetime.utcnow())
    user_email = Column(String, ForeignKey("users.email"))
    order_status = Column(String, ForeignKey("cart.order_status"))
    final_price = Column(Float,ForeignKey("cart.final_price"))

class CartSchema(ma.Schema):
    class Meta:
        fields =('order_id','user_email','address','pincode',
                 'state','country','product_id','product_name','order_status',
                 'order_status_created_at','quantity')


class OrdersSchema(ma.Schema):
    class Meta:
        fields = ('order_created_at', 'is_approved', 'order_aproved_at',
        'is_fullfilled', 'order_fullfilled_at', 'is_cancelled', 'order_cancelled_at','Final_price')

class UserSchema(ma.Schema):
    class Meta:
        fields=('user_id','user_name','is_admin','is_active','email','password','public_id')

class UserProfileSchema(ma.Schema):
    class Meta:
        fields=('user_profile_id','user_email','gender','age','profession','mobile_number','parent')


class ProductsSchema(ma.Schema):
    class Meta:
        fields=('product_id','product_name','product_category','price','quantity')

user_schema = UserSchema()
up_schema = UserProfileSchema()
p_schema = ProductsSchema()
cart_schema = CartSchema()

# ---------------------------------------- Flask command Line Commands ----------------------------------

@app.cli.command('db_create')
def db_create():
    db.create_all()
    print('Database Created!')

@app.cli.command('db_drop')
def db_drop():
    db.drop_all()
    print('Database Dropped!')


@app.cli.command('db_seed')
def db_seed():

    wooden_chair = Products(product_name= "Wooden chair",product_category="chair",price=1000,quantity=10)
    recliner_chair = Products(product_name="Recliner chair", product_category="chair", price=30000, quantity=14)
    sofa_chair = Products(product_name="Soofa chair", product_category="chair", price=20000, quantity=30)
    dinning_table = Products(product_name="Dinning Table", product_category="table", price=40000, quantity=5)
    study_table = Products(product_name="Study Table", product_category="table", price=3000, quantity=30)
    wardrobe = Products(product_name="Wardrobe", product_category="wardrobe", price=7000, quantity=10)

    db.session.add(wooden_chair)
    db.session.add(recliner_chair)
    db.session.add(sofa_chair)
    db.session.add(dinning_table)
    db.session.add(study_table)
    db.session.add(wardrobe)

    test_user_1 = User(user_name="Kruthik",is_admin=True,is_active = True,public_id=str(uuid.uuid4()),
                       email="kruthik@gmail.com",password = generate_password_hash('Pass@123', method='sha256'))
    test_user_2 = User(user_name="Karthik", is_admin=False, is_active=True, public_id=str(uuid.uuid4()),
                       email="karthik@gmail.com",password=generate_password_hash('Pass@123', method='sha256'))
    test_user_3 = User(user_name="Karan", is_admin=False, is_active=False, public_id=str(uuid.uuid4()),
                       email="karan@gmail.com",password=generate_password_hash('Pass@123', method='sha256'))
    test_user_4 = User(user_name="Koushik",is_admin = True,is_active=False, public_id=str(uuid.uuid4()),
                       email="koushik@gmail.com",password=generate_password_hash('Pass@123', method='sha256'))

    db.session.add(test_user_1)
    db.session.add(test_user_2)
    db.session.add(test_user_3)
    db.session.add(test_user_4)

    kruthik = User_Profile(user_email="kruthik@gmail.com", gender="Male",
                           age=20, profession="Student", mobile_number="1234567890")
    karan = User_Profile(user_email="karan@gmail.com", gender="Male",
                           age=20, profession="IT", mobile_number="1234567809")
    db.session.add(kruthik)
    db.session.add(karan)

    db.session.commit()
    print("Database Seeded!")



# -------------------------------------- Common Area ------------------------------------------



def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message' : 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'message' : 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated


# -------------------------------------- ADMIN AREA --------------------------------------------------


@app.route('/edit-customer-profile',methods=['POST'])
@token_required
def edit_customer_profile(current_user):
    if not current_user.is_admin:
        return jsonify({'message': 'Cannot perform that function!'})

    user_email = request.form['user_email']
    test = User.query.filter_by(email=user_email).first()
    test_userProfile = User_Profile.query.filter_by(user_email=user_email).first()


    if test and not test_userProfile:
        return jsonify(message="Data profile does not exist")


    if test and test_userProfile:

        try:
            test_userProfile.user_email = request.form['user_email']
            test_userProfile.gender = request.form['gender']
            test_userProfile.age = request.form['age']
            test_userProfile.profession = request.form['profession']
            test_userProfile.mobile_number = request.form['mobile_number']
            db.session.commit()
            return jsonify(message="Data has been updated"), 200
        except exc.IntegrityError:
            return jsonify(message="Mobile number exists in our database!"), 409

    else:
        return jsonify(message="Data cannot be inserted. Invalid Email"), 401


    return jsonify(message="edit-customer-profile")


@app.route('/deactivate-user',methods=['POST'])
@token_required
def deactivate_user(current_user):
    if not current_user.is_admin:
        return jsonify(message='Cannot perform that function!')
    user_email = request.form['user_email']
    test = User.query.filter_by(email=user_email).first()
    if not test:
        return jsonify(message="No User Found")
    if test.is_active:
        test.is_active = False
        db.session.commit()
    else:
        return jsonify("User is already deactivated")
    return jsonify(message = "User has been deactivated")


@app.route('/activate-user',methods=['PUT'])
@token_required
def activate_user(current_user):
    if not current_user.is_admin:
        return jsonify(message='Cannot perform that function!')
    user_email = request.form['user_email']
    test = User.query.filter_by(email=user_email).first()
    if not test:
        return jsonify(message="No User Found")
    if not test.is_active:
        test.is_active = True
        db.session.commit()
    else:
        return jsonify(message="User is already active")
    #return jsonify(message = "User has been deactivated")
    return jsonify(message = "User has been activated")


@app.route('/all-orders-pending',methods=['GET'])
@token_required
def all_orders_pending(current_user):
    if not current_user.is_admin:
        return jsonify(message='Cannot perform that function!')
    admin = Orders_Pending_Approval.query.all()
    output=[]
    for i in admin:
        admin_order_approval = {}
        admin_order_approval['id'] = i.id
        admin_order_approval['cart_id'] = i.cart_id
        admin_order_approval['final_price'] = i.final_price
        admin_order_approval['order_created_at'] = i.order_created_at
        admin_order_approval['order_status'] = i.order_status
        admin_order_approval['product_id'] = i.product_id
        admin_order_approval['user_email'] = i.user_email
        output.append(admin_order_approval)
    return jsonify(output)


@app.route('/approve-customer-order',methods=['PUT'])
@token_required
def approve_customer_order(current_user):
    if not current_user.is_admin:
        return jsonify(message='Cannot perform that function!')

    cart_id = request.headers['cart_id']
    admin_order_approval = Orders_Pending_Approval.query.filter_by(cart_id=cart_id).first()
    order_details = Order_Details.query.filter_by(cart_id=cart_id).first()
    cart = Cart.query.filter_by(cart_id=cart_id).first()

    if cart_id == "" and cart:
        return jsonify(message = "Invalid id")
    elif cart.order_status == "order_placed":
        cart.order_status = "order_approved"
        order_details.is_approved = True
        order_details.order_aproved_at = datetime.datetime.now()

        db.session.delete(admin_order_approval)
        db.session.commit()
    else:
        return jsonify(message="Order has been cancelled")

    return jsonify(message="Customer order has been approved")


@app.route('/fullfilled-customer-order',methods=['PUT'])
@token_required
def fullfilled_customer_order(current_user):

    if not current_user.is_admin:
        return jsonify(message='Cannot perform that function!')

    cart_id = request.headers['cart_id']
    admin_order_approval = Orders_Pending_Approval.query.filter_by(cart_id=cart_id).first()
    cart = Cart.query.filter_by(cart_id=cart_id).first()
    order_details = Order_Details.query.filter_by(cart_id=cart_id).first()

    if cart_id == "" and cart:
        return jsonify(message = "Invalid id")
    elif cart.order_status == "order_approved":
        cart.order_status = "order_fullfilled"
        order_details.order_fullfilled_at = datetime.datetime.now()
        order_details.is_fullfilled = True
        db.session.commit()
    elif cart.order_status == "cancelled":
        return jsonify(message="Order has been cancelled")
    else:
        return jsonify(message="Order is still not approved by admin")

    return jsonify(message="Customer order has been fullfilled")



# -------------------------------------- CUSTOMER AREA -----------------------------------------------





#Customer SignUp
@app.route('/register',methods=['POST'])
def register():
    email = request.form['email']
    test = User.query.filter_by(email=email).first()
    if test:
        return jsonify(message='Email already exists'),409
    else:
        user_name = request.form['user_name']
        hashed_password = generate_password_hash(request.form['password'], method='sha256')
        user = User(user_name=user_name,password=hashed_password,email=email)
        db.session.add(user)
        db.session.commit()
        return jsonify(message='User has been created'),201


#Creating Customer Profile
@app.route("/create-user-profile",methods=['POST'])
def create_user_profile():
    user_email= request.form['user_email']
    test = User.query.filter_by(email=user_email).first()
    test_userProfile = User_Profile.query.filter_by(user_email=user_email).first()
    if test and not test_userProfile:
        try:
            gender = request.form['gender']
            age = request.form['age']
            profession = request.form['profession']
            mobile_number = request.form['mobile_number']
            profile = User_Profile(user_email=user_email, gender=gender, age=age,
                                   profession=profession, mobile_number=mobile_number)
            db.session.add(profile)
            db.session.commit()
            return jsonify(message="Data has been inserted"), 200
        except exc.IntegrityError:
            return jsonify(message="Mobile number exists in our database!"),409


    if test and test_userProfile:
        return jsonify(message="Profile exists in our database!")
    else:
        return jsonify(message="Data cannot be inserted. Invalid Email"),401


# Customer Login
@app.route('/login',methods=['POST'])
def login():
    hashed_password = False
    email = request.form['email']
    password = request.form['password']
    test = User.query.filter_by(email=email).first()

    if test:
        db_password = User.query.filter_by(email=email).first()
        hashed_password = check_password_hash(db_password.password, password)
        # return jsonify(message=hashed_password)

        if hashed_password:
            user = User.query.filter_by(email=email).first()
            access_token = jwt.encode(
                {'public_id': user.public_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},
                app.config['SECRET_KEY'])

            #return access_token.decode('UTF-8')
            return jsonify(message={'token' : access_token,
                                    'Status': 'Login Successful'}, )
        else:
            return jsonify(message="Invalid email or password"), 401

    else:
        return jsonify(message="Invalid email or password"),401


@app.route('/product-catalog')
@token_required
def get_product_catalog(current_user):
    products_catalog = Products.query.all()
    users = User.query.all()
    output = []
    for i in products_catalog:
    # for u in users:
        product_data={}
        # product_data['user_email'] = u.email
        product_data['product_id'] = i.product_id
        product_data['product_name']=i.product_name
        product_data['product_category'] = i.product_category
        product_data['price'] = i.price
        product_data['quantity'] = i.quantity
        output.append(product_data)
    return jsonify({'products':output})


@app.route('/place-order',methods=['POST'])
@token_required
def place_order(current_user):
    # return jsonify(current_user.email )
    cart = Cart.query.filter_by(user_email=current_user.email).first()
    # try:
    if (request.form['address']== "" or request.form['pincode'] =="" or request.form['state'] =="" or
            request.form['country'] == "" or request.form['product_name'] == ""):
        return jsonify(message ="Values missing"),404

    if (int(request.form['quantity'])==0):
        return jsonify(message ="invalid quantity"),404
    # except:
    #     return jsonify(message="Table not updated"), 400
    product = Products.query.filter_by(product_name = request.form['product_name']).first()
    valid_quantity = product.quantity - int(request.form['quantity'])
    # return jsonify(valid_quantity)
    if valid_quantity>0:
        product.quantity = valid_quantity
        # return jsonify(product.quantity)
        user_email = current_user.email
        address = request.form['address']
        pincode = request.form['pincode']
        state = request.form['state']
        country = request.form['country']
        product_id = product.product_id  # change this line
        product_name = request.form['product_name']  # change this line
        order_status = "order_placed"
        order_status_created_at = datetime.datetime.utcnow()
        quantity = request.form['quantity']
        final_price = (float(quantity) * product.price)

        cart = Cart(user_email=user_email, address=address, pincode=pincode, state=state, country=country,
                    product_id=product_id, product_name=product_name, order_status=order_status,
                    order_status_created_at=order_status_created_at, quantity=quantity,
                    final_price=final_price)
        db.session.add(cart)
        db.session.commit()
        # try:
        #
        # except:
        #     return jsonify(message = "Successfully added table to cart table")

        admin_order_approval = Orders_Pending_Approval(cart_id=cart.cart_id, product_id=product_id,
                                                       order_created_at=order_status_created_at,
                                                       user_email=current_user.email,
                                                       order_status="order_placed",
                                                       final_price=final_price
                                                       )
        db.session.add(admin_order_approval)
        db.session.commit()

        user_email = current_user.email
        cart_id = cart.cart_id
        product_id = admin_order_approval.product_id
        order_created_at = admin_order_approval.order_created_at


        order_details = Order_Details(user_email=user_email, cart_id=cart_id, product_id=product_id,
                                      order_created_at=order_created_at)
        db.session.add(order_details)
        db.session.commit()

        return jsonify(message="Record added to table")
    else:
        return jsonify(message="Sorry we are sold out")


@app.route('/cancel-order',methods=['PUT'])
@token_required
def cancel_order(current_user):

    cart_id = request.headers['cart_id']
    cart = Cart.query.filter_by(cart_id=cart_id).first()
    admin_order_approval = Orders_Pending_Approval.query.filter_by(cart_id=cart_id).first()
    order_details = Order_Details.query.filter_by(cart_id=cart_id).first()

    if cart_id == "" and cart:
        return jsonify(message = "Invalid Order id")
    if cart.order_status == "order_placed":
        cart.order_status = "order_cancelled"
        db.session.delete(admin_order_approval)

        order_details.order_cancelled_at = datetime.datetime.now()
        order_details.is_cancelled = True
        db.session.commit()
        return jsonify(message="Order has been cancelled")
    elif cart.order_status == "approved":
        return jsonify(message="Order cannot be cancelled as it is been approved by the seller, here is your order number "
                               + str(cart.cart_id))
    else:
        return jsonify(message= "Order has already been cancelled")


@app.route("/order-history",methods=['GET'])
@token_required
def order_history(current_user):

    #cart_id = request.headers['cart_id']
    cart = Cart.query.filter_by(user_email = current_user.email)
    output=[]
    for i in cart:
        temp = {}
        temp['product_name'] = i.product_name
        temp["product_id"] = i.product_id
        temp["order_status"] = i.order_status
        temp["final_price"] = i.final_price
        temp["address"] = i.address + i.state + i.country
        output.append(temp)
    return jsonify(output)

if __name__=="__main__":
    app.run()