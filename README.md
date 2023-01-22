# Furniture Shop 

A database and api endpoints in python-flask with sqlite as database.
There is also code to establish connection for MYSQL server commented outin lines 25-45
Furniture shop, has following 6 tables 

* Users 
* User_Profile
* Products
* Cart
* Order_details
* Orders_Pending_Approval

## Users Table

Users table has following 7 columns with following column names and datatypes

* "user_id" - datatype Integer - primary key
* "user_name" - String
* "email" - String - unique
* "password" - String
* "is_admin" - Boolean - with default value as False
* "is_active" - Boolean - with default value as True
* "public_id" = String - unique

Here, public id is a 50 digit unique id created with Universally unique identifier

## Products Table

Products table has following columns with following names and datatypes,

* "product_id" - Integer - primary key
* "product_name" - String
* "product_category" - String
* "price" - Float
* "quantity" - Integer

## User Profile Table

User Profile has following columns with following names and datatypes,
* "user_profile_id - Integer - primary_key
* "user_email" - String -  ForeignKey(users.email)
* "gender" - String
* "age" - Integer
* "profession" - String
* "mobile_number" - Integer - unique
* one - one relationship with "User" table

## Cart Table 

Cart Table has following columns with following names and datatypes,

* "cart_id" - Integer - Primary Key
* "user_email" - String - ForeignKey(users.email)
* "address" - String
* "pincode" - String
* "country" - String
* "state" - String
* "product_id" - Integer - ForeignKey("products.product_id"))
* "product_name" - String
* "order_status" - String
* "order_status_created_at" - DateTime
* "quantity" - Integer
* "final_price" - Float

## Orders Pending Approval Table

Order Pending table has following columns with following names and datatypes,

* "id" - Integer - primary key
* "cart_id" - Integer ForeignKey("cart.cart_id"))
* "product_id" - Integer - ForeignKey("products.product_id"))
* "order_created_at" - Column(DateTime, ForeignKey("cart.order_status_created_at"),
                              default=datetime.datetime.utcnow())
* "user_email" - Column(String, ForeignKey("users.email"))
* "order_status" - String - ForeignKey("cart.order_status"))
* "final_price" - Float - ForeignKey("cart.final_price"))

**Orders Pending table is created for admin to view pending orders seprately in a table.**

## Order Details Table

Order details table has following columns with following names and datatypes,

*   "cart_id" - Integer - ForeignKey("cart.cart_id"))
*  "order_id - Integer - Primary Key 
*  "product_id" Integer -  ForeignKey("products.product_id")
*  "order_created_at" - DateTime
*  "is_approved" - Boolean
*  "order_aproved_at"   - DateTime
*  "is_fullfilled" - Boolean
*  "order_fullfilled_at " - DateTime
*  "is_cancelled" - Boolean
*  "order_cancelled_at"  - DateTime
