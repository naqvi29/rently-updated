from ast import withitem
from flask import Flask, render_template,request,redirect,url_for,session
import pymongo
import os
from os.path import join, dirname, realpath
from PIL import Image
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId
from flask_mail import Mail, Message
import json

app = Flask(__name__)

# configure secret key for session protection)
app.secret_key = '_5#y2L"F4Q8z\n\xec]/'

# MONGOGB DATABASE CONNECTION
connection_url = "mongodb://localhost:27017/"
client = pymongo.MongoClient(connection_url)
# client.list_database_names()
database_name = "Rently"
db = client[database_name]

CARS_FOLDER = join(dirname(realpath(__file__)), 'static/images/cars')
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg',}
app.config['CARS_FOLDER'] = CARS_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS





# Mail server config.
app.config['MAIL_DEBUG'] = True
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
# app.config['MAIL_USERNAME'] = 'bookkingdom172@gmail.com'
app.config['MAIL_USERNAME'] = 'nasiralisw2@gmail.com'
# app.config['MAIL_PASSWORD'] = 'Book12345'
# app.config['MAIL_PASSWORD'] = 'fbijqpcqyeecdnam'
app.config['MAIL_PASSWORD'] = 'dnkhjkamexfwhzoz'
app.config['MAIL_DEFAULT_SENDER'] = ('nasiralisw2@gmail.com')
mail = Mail(app)

@app.route("/")
def index():
    if 'loggedin' in session:
        return render_template("index.html",loggedin = True,username=session['name'],type=session['type'],userid=session['userid'])
    else:
        return render_template("index.html")

@app.route("/about")
def about():
    if 'loggedin' in session:
        return render_template("about.html",loggedin = True,username=session['name'],type=session['type'],userid=session['userid'])
    else:
        return render_template("about.html")

@app.route("/contact",methods=['GET','POST'])
def contact():
    if request.method == 'POST':
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        number = request.form.get("number")
        msg = request.form.get("msg")
        db.messages.insert_one({
            "first_name":first_name,
            "last_name":last_name,
            "email":email,
            "number":number,
            "msg":msg
        })
        msg = Message("DriveNow | Message Received",sender='nasiralisw2@gmail.com', recipients=[email])
        msg.html = "<p>Dear "+first_name+" "+last_name+"</p><p style='margin-top:1%'>Thank you for contacting us. we will respond to you soon</p><p style='margin-top:1%'>Thank you</p><p style='margin-top:1%'>DriveNow</p>"
        mail.send(msg)
        msg = Message("DriveNow | New Message Received",sender='nasiralisw2@gmail.com', recipients=['nasiralisw2@gmail.com'])
        msg.html = "<p>Name: "+first_name+" "+last_name+"</p><p style='margin-top:1%'>Mail: "+email+"</p><p style='margin-top:1%'>Phone Number: "+number+"</p><p style='margin-top:1%'>Message: "+str(msg)+"</p>"
        mail.send(msg)
        if 'loggedin' in session:
            return render_template("contact.html",success=True,loggedin = True,username=session['name'],type=session['type'],userid=session['userid'])
        else:
            return render_template("contact.html",success=True)
    if 'loggedin' in session:
        return render_template("contact.html",loggedin = True,username=session['name'],type=session['type'],userid=session['userid'])
    else:
        return render_template("contact.html")




@app.route("/our-clients")
def our_clients():
    if 'loggedin' in session:
        return render_template("our-clients.html",loggedin = True,username=session['name'],type=session['type'],userid=session['userid'])
    else:
        return render_template("our-clients.html")

@app.route("/search-car")
def search_car():   
    if "category" in request.args:
        category = request.args.get("category")
        data = db.cars.find({"category":category})
    else:
        data = db.cars.find()
    if "pickup_location" in request.args:
        pickup_location = request.args.get("pickup_location")
        date = request.args.get("date")
        time = request.args.get("time")
        type = request.args.get("type")

    cars = []
    car_ids = []
    self_drive_cars=[]
    for i in data:
        # i.update({"_id":str(i["_id"])})
        if not i['full_day']:
            price_per_hour = float(i['price_per_day'])/float(12)
            price_per_hour_old = float(i['price_per_day_old'])/float(12)
        else:
            price_per_hour = float(i['price_per_day'])/float(i['full_day'])
            price_per_hour_old = float(i['price_per_day_old'])/float(i['full_day'])

        i.update({"_id":str(i["_id"]),"price_per_hour":round(price_per_hour, 2),"price_per_hour_old":round(price_per_hour_old, 2)})
        cars.append(i)
        id = i['_id']
        car_ids.append(id)
        if i['with_driver'] == False:
            self_drive_cars.append(i)


    if "category" in request.args:
        if "pickup_location" in request.args:
            if 'loggedin' in session:
                return render_template("search-car.html",category=category,cars=cars, car_ids=json.dumps(car_ids),self_drive_cars=self_drive_cars,loggedin = True,username=session['name'],type=session['type'],userid=session['userid'],pickup_location=pickup_location,date=date,time=time,day_type=type)
            else:
                return render_template("search-car.html",category=category,cars=cars,car_ids=json.dumps(car_ids),self_drive_cars=self_drive_cars,loggedin=False,pickup_location=pickup_location,date=date,time=time,day_type=type)
        else:

            if 'loggedin' in session:
                return render_template("search-car.html",category=category,cars=cars,car_ids=json.dumps(car_ids),self_drive_cars=self_drive_cars,loggedin = True,username=session['name'],type=session['type'],userid=session['userid'])
            else:
                return render_template("search-car.html",category=category,cars=cars,car_ids=json.dumps(car_ids),self_drive_cars=self_drive_cars,loggedin=False)
    else:
        if "pickup_location" in request.args:
            if 'loggedin' in session:
                return render_template("search-car.html",cars=cars, car_ids=json.dumps(car_ids),self_drive_cars=self_drive_cars,loggedin = True,username=session['name'],type=session['type'],userid=session['userid'],pickup_location=pickup_location,date=date,time=time,day_type=type)
            else:
                return render_template("search-car.html",cars=cars,car_ids=json.dumps(car_ids),self_drive_cars=self_drive_cars,loggedin=False,pickup_location=pickup_location,date=date,time=time,day_type=type)
        else:

            if 'loggedin' in session:
                return render_template("search-car.html",cars=cars,car_ids=json.dumps(car_ids),self_drive_cars=self_drive_cars,loggedin = True,username=session['name'],type=session['type'],userid=session['userid'])
            else:
                return render_template("search-car.html",cars=cars,car_ids=json.dumps(car_ids),self_drive_cars=self_drive_cars,loggedin=False)


@app.route("/signup",methods=['GET','POST'])
def signup():
    if request.method=='POST':
        name = request.form.get("name")
        phone = request.form.get("phone")
        email = request.form.get("email")
        password = request.form.get("password")
        # check if exists 
        phone_exist = db.users.find_one({"phone":phone})
        email_exist = db.users.find_one({"email":email})
        if phone_exist:
            e="Phone Number Already Registered!"
            return render_template("signup.html",error=e)
        if email_exist:
            e="Email Address Already Registered!"
            return render_template("signup.html",error=e)
        db.users.insert_one({"name":name,"phone":phone,"email":email,"password":password,"user_type":"user"})
        return render_template("login.html",success="Account Created Succesfully!")
    
    if 'loggedin' in session:
        return render_template("signup.html",loggedin = True,username=session['name'],type=session['type'],userid=session['userid'])
    else:
        return render_template("signup.html")

@app.route("/login",methods=['GET','POST'])
def login():
    if request.method=='POST':
        email = request.form.get("email")
        password = request.form.get("password")
        # check 
        
        exist = db.users.find_one({"email":email})
        if not exist:
            e="Invalid Email!"
            return render_template("login.html",error=e)
        if exist['password']!=password:
            e="Invalid Password!"
            return render_template("login.html",error=e)
        session['loggedin'] = True
        session['userid'] = str(exist["_id"])
        session['name'] = exist["name"]
        session['email'] = exist["email"]
        session['type'] = exist['user_type']
        return redirect(url_for("index"))

    else:
        if 'loggedin' in session:
            return render_template("login.html",loggedin = True,username=session['name'],type=session['type'],userid=session['userid'])
        else:
            return render_template("login.html")

@app.route("/logout")
def logout():
    try:
        tmp = session['type']
        session.pop('loggedin', None)
        session.pop('userid', None)
        session.pop('name', None)
        session.pop('email', None)
        session.pop('type', None)
        if tmp == "admin":
            return redirect(url_for("admin_login"))
        else:
            return redirect(url_for('index'))
    except Exception as e:
        return str(e)

@app.route("/userprofile/<string:id>")
def userprofile(id):
    if 'loggedin' in session:
        data = db.users.find_one({"_id":ObjectId(id)})
        return render_template("userprofile.html",loggedin = True,username=session['name'],type=session['type'],userid=session['userid'],data=data)
    else:
        return render_template("userprofile.html",data=data)

@app.route("/mybookings")
def mybookings():
    if 'loggedin' in session:
        return render_template("mybookings.html",loggedin = True,username=session['name'],type=session['type'],userid=session['userid'])
    else:
        return render_template("mybookings.html")

@app.route("/corporate-enquiries",methods=['GET','POST'])
def corporate_enquiries():
    if request.method == 'POST':
        name = request.form.get("name")
        email = request.form.get("email")
        number = request.form.get("number")
        address = request.form.get("address")
        location = request.form.get("location")
        cars = request.form.get("cars")
        days = request.form.get("days")
        purpose = request.form.get("purpose")
        details = request.form.get("details")
        db.corporate_inquiries.insert_one({
            "name":name,
            "email":email,
            "number":number,
            "address":address,
            "location":location,
            "cars":cars,
            "days":days,
            "purpose":purpose,
            "details":details
        })
        msg = Message("DriveNow | Inquiry Received",sender='nasiralisw2@gmail.com', recipients=[email])
        msg.html = "<p>Dear "+name+"</p><p style='margin-top:1%'>Thank you for your inquiry. we will respond to you soon</p><p style='margin-top:1%'>Thank you</p><p style='margin-top:1%'>DriveNow</p>"
        mail.send(msg)
        msg = Message("DriveNow | New Inquiry Received",sender='nasiralisw2@gmail.com', recipients=['nasiralisw2@gmail.com'])
        msg.html = "<p>Name: "+name+"</p><p style='margin-top:1%'>Email: "+email+"</p><p style='margin-top:1%'>Number: "+number+"</p><p style='margin-top:1%'>Address: "+address+"</p><p style='margin-top:1%'>location: "+location+"</p><p style='margin-top:1%'>No of Cars: "+cars+"</p><p style='margin-top:1%'>No of Days: "+days+"</p><p style='margin-top:1%'>Purpose Of Enquiry: "+purpose+"</p><p style='margin-top:1%'>Details: "+details+"</p>"
        mail.send(msg)
        if 'loggedin' in session:
            return render_template("corporate-enquiries.html",loggedin = True,username=session['name'],type=session['type'],userid=session['userid'])
        else:
            return render_template("corporate-enquiries.html",success=True)
    if 'loggedin' in session:
        return render_template("corporate-enquiries.html",loggedin = True,username=session['name'],type=session['type'],userid=session['userid'])
    else:
        return render_template("corporate-enquiries.html")


@app.route("/book-now/<string:id>/<string:type>",methods=['GET','POST'])
def book_now(id,type):
    
    if 'loggedin' in session:
        if request.method == 'POST':
            pickup_date = request.form.get("pickup_date")
            pickup_time = request.form.get("pickup_time")
            pickup_location = request.form.get("pickup_location")
            pickup_desc = request.form.get("pickup_desc")
            dropoff_location = request.form.get("dropoff_location")
            dropoff_desc = request.form.get("dropoff_desc")
            type = request.form.get("customRadio")
            city = request.form.get("customRadio4")
            print(pickup_date)
            print(pickup_time)
            print(pickup_location)
            print(pickup_desc)
            print(dropoff_location)
            print(dropoff_desc  )
            new_data = {
                "pickup_date":pickup_date,
                "pickup_time":pickup_time,
                "pickup_location":pickup_location,
                "pickup_desc":pickup_desc,
                "dropoff_location":dropoff_location,
                "dropoff_desc":dropoff_desc,
                "type":type,
                "city":city
            }
            db.bookings.insert_one(new_data)
            return render_template("index.html",booked=True)
        if "pickup_location" in request.args:
            pickup_location = request.args.get("pickup_location")
        else:
            pickup_location=None
        if "date" in request.args:
            date = request.args.get("date")
        else:
            date=None
        if "time" in request.args:
            time = request.args.get("time")
        else:
            time = None
        if "city" in request.args:
            city = request.args.get("city")
        else:
            city=None
        type2 = type.replace("_"," ")
        car = db.cars.find_one({"_id":ObjectId(id)})
        # car = car.update({"_id":str(car["_id"])})
        # return str(car)
        
        return render_template("book-now.html",booking_type=type2,booking_type_2=type,car_id=id,car=car,pickup_location=pickup_location,date=date,time=time,city=city,loggedin = True,username=session['name'],type=session['type'],userid=session['userid'])
    else:
        return "Please Login First.."

@app.route("/blog")
def blog():
    if 'loggedin' in session:
        return render_template("blog.html",loggedin = True,username=session['name'],type=session['type'],userid=session['userid'])
    else:
        return render_template("blog.html")

@app.route("/my-bookings")
def my_bookings():
    if 'loggedin' in session:
        data = db.bookings.find()
        active_bookings = []
        for i in data:
            i.update({"_id":str(i["_id"])})
            active_bookings.append(i)

        return render_template("mybookings.html",active_bookings=active_bookings,loggedin = True,username=session['name'],type=session['type'],userid=session['userid'])
    else:
        return str("Please Login to access this page")

# -x-x-x-x-x-x ADMIN DASH -x-x-x-x-x-x
@app.route("/admin")
def admin():
    if 'loggedin' in session:
        if session['type'] == 'admin':
            vehicles = db.cars.count_documents({})
            bookings = db.bookings.count_documents({})
            messages = db.messages.count_documents({})
            return render_template("admin-index.html",username=session['name'],vehicles=vehicles,bookings=bookings,messages=messages)
        else:
            return redirect(url_for("admin_login"))
    else:
        return redirect(url_for("admin_login"))

@app.route("/admin-login",methods=['GET','POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")
        exist = db.users.find_one({"email":email,"user_type":"admin"})
        print(exist)
        if exist:
            if password == exist['password']:
                # Let him login now as admin
                session['loggedin'] = True
                session['userid'] = str(exist["_id"])
                session['name'] = exist["name"]
                session['email'] = exist["email"]
                session['type'] = exist["user_type"]
                return redirect(url_for("admin"))
            else:
                return render_template("admin-login.html",error="Invalid Password!")
        else:
            return render_template("admin-login.html",error="Invalid Email!")

    if 'loggedin' in session:
        if session['type'] == 'admin':
            return redirect(url_for("admin"))
        else:
            return render_template("admin-login.html",error="Please Logout From User Account First!")
    else:
        return render_template("admin-login.html")

@app.route("/registered-vehicles")
def registered_vehicles():
    if 'loggedin' in session:
        if session['type'] == 'admin':
            data = db.cars.find()
            cars = []
            for i in data:
                i.update({"_id":str(i["_id"])})
                cars.append(i)
            return render_template("registered-vehicles.html",cars=cars,username=session['name'])
        else:
            return render_template("admin-login.html",error="Please Logout From User Account First!")
    else:
        return render_template("admin-login.html")

@app.route("/view-all-bookings")
def view_all_bookings():
    if 'loggedin' in session:
        if session['type'] == 'admin':
            data = db.bookings.find()
            bookings = []
            for i in data:
                i.update({"_id":str(i["_id"])})
                bookings.append(i)
            return render_template("all-bookings.html",bookings=bookings,username=session['name'])
        else:
            return render_template("admin-login.html",error="Please Logout From User Account First!")
    else:
        return render_template("admin-login.html")

@app.route("/view-all-inquires")
def view_all_inquires():
    if 'loggedin' in session:
        if session['type'] == 'admin':
            data = db.corporate_inquiries.find()
            List = []
            for i in data:
                i.update({"_id":str(i["_id"])})
                List.append(i)
            return render_template("inquiries.html",List=List,username=session['name'])
        else:
            return render_template("admin-login.html",error="Please Logout From User Account First!")
    else:
        return render_template("admin-login.html")

@app.route("/view-all-messages")
def view_all_messages():
    if 'loggedin' in session:
        if session['type'] == 'admin':
            data = db.messages.find()
            List = []
            for i in data:
                i.update({"_id":str(i["_id"])})
                List.append(i)
            return render_template("messages.html",List=List,username=session['name'])
        else:
            return render_template("admin-login.html",error="Please Logout From User Account First!")
    else:
        return render_template("admin-login.html")

@app.route("/view-all-subscribers")
def view_all_subscribers():
    if 'loggedin' in session:
        if session['type'] == 'admin':
            data = db.subscribers.find()
            List = []
            for i in data:
                i.update({"_id":str(i["_id"])})
                List.append(i)
            return render_template("subscribers.html",List=List,username=session['name'])
        else:
            return render_template("admin-login.html",error="Please Logout From User Account First!")
    else:
        return render_template("admin-login.html")

@app.route("/add-vehicle",methods=['GET','POST'])
def add_vehicle():
    if request.method == 'POST':
        name = request.form.get("name")
        price_per_day = float(request.form.get("price_per_day"))
        price_per_day_old = float(request.form.get("price_per_day_old"))
        city = request.form.get("city")
        with_driver = request.form.get("with_driver")
        if with_driver == "true":
            with_driver = True
        elif with_driver == "false":
            with_driver = False
        ac = request.form.get("ac")
        if ac == "true":
            ac = True
        elif ac == "false":
            ac = False
        if "out_city_cost" in request.form:
            out_city_cost = float(request.form.get("out_city_cost"))
        else:
            out_city_cost = None
        doors = int(request.form.get("doors"))
        transmission = request.form.get("transmission")
        if "overtime" in request.form:
            overtime = float(request.form.get("overtime"))
        else:
            overtime = None
        if "fuel_average" in request.form:
            fuel_average = float(request.form.get("fuel_average"))
        else:
            fuel_average = None
        if "full_day" in request.form:
            full_day = int(request.form.get("full_day"))
        else:
            full_day = None
        category = request.form.get("category")
        if 'pic' not in request.files:
            pic = None
        else:
            pic = request.files['pic']

        if pic and allowed_file(pic.filename):
                filename = secure_filename(pic.filename)
                pic.save(os.path.join(CARS_FOLDER, filename))
        print(name)
        print(price_per_day)
        print(city)
        print(with_driver)
        print(ac)
        print(doors)
        print(transmission)
        print(overtime)
        print(fuel_average)
        print(full_day)
        db.cars.insert_one({
            "name":name,
            "price_per_day":price_per_day,
            "price_per_day_old":price_per_day_old,
            "city":city,
            "with_driver":with_driver,
            "ac":ac,
            "doors":doors,
            "transmission":transmission,
            "overtime":overtime,
            "fuel_average":fuel_average,
            "full_day":full_day,
            "pic":filename,
            "category":category,
            "out_city_cost":out_city_cost
        })
        return redirect(url_for("registered_vehicles"))
    if 'loggedin' in session:
        if session['type'] == 'admin':
            return render_template("add-vehicle.html",username=session['name'])
        else:
            return render_template("admin-login.html",error="Please Logout From User Account First!")
    else:
        return render_template("admin-login.html")


@app.route("/edit-registered-vehicle/<string:id>",methods=['GET','POST'])
def edit_registered_vehicle(id):
    if request.method == 'POST':
        name = request.form.get("name")
        price_per_day_old = float(request.form.get("price_per_day_old"))
        price_per_day = float(request.form.get("price_per_day"))
        city = request.form.get("city")
        with_driver = request.form.get("with_driver")
        if with_driver == "true":
            with_driver = True
        elif with_driver == "false":
            with_driver = False
        ac = request.form.get("ac")
        if ac == "true":
            ac = True
        elif ac == "false":
            ac = False
        if "out_city_cost" in request.form:
            out_city_cost = float(request.form.get("out_city_cost"))
        else:
            out_city_cost = None
        doors = int(request.form.get("doors"))
        transmission = request.form.get("transmission")
        if "overtime" in request.form:
            overtime = float(request.form.get("overtime"))
        else:
            overtime=None
        if "fuel_average" in request.form:
            fuel_average = float(request.form.get("fuel_average"))
        else:
            fuel_average=None
        if "full_day" in request.form:
            full_day = int(request.form.get("full_day"))
        else:
            full_day=None
        if 'pic' not in request.files:
            pic = None
        else:
            pic = request.files['pic']
        

        if pic and allowed_file(pic.filename):
                filename = secure_filename(pic.filename)
                pic.save(os.path.join(CARS_FOLDER, filename))
        
        # Values to be updated.
        filter = { "_id": ObjectId(id) }
        if pic: 
            new_values = {
                '$set': {
                    "name": name,
                    "price_per_day_old": price_per_day_old,
                    "price_per_day": price_per_day,
                    "city": city,
                    "with_driver": with_driver,
                    "ac": ac,
                    "doors": doors,
                    "transmission": transmission,
                    "overtime": overtime,
                    "fuel_average":fuel_average,
                    "full_day": full_day,
                    "pic": filename,
                    "out_city_cost":out_city_cost
                }
            }
        else: 
            new_values = {
                '$set': {
                    "name": name,
                    "price_per_day_old": price_per_day_old,
                    "price_per_day": price_per_day,
                    "city": city,
                    "with_driver": with_driver,
                    "ac": ac,
                    "doors": doors,
                    "transmission": transmission,
                    "overtime": overtime,
                    "fuel_average":fuel_average,
                    "full_day": full_day,
                    "out_city_cost":out_city_cost
                }
            }
        db.cars.update_one(filter, new_values)
        return redirect(url_for("registered_vehicles"))
    if 'loggedin' in session:
        if session['type'] == 'admin':
            car = db.cars.find_one({"_id":ObjectId(id)})
            full_day = [8,12,24]
            return render_template("edit-vehicle.html",username=session['name'],car=car,full_day=full_day)
        else:
            return render_template("admin-login.html",error="Please Logout From User Account First!")
    else:
        return render_template("admin-login.html")

@app.route("/delete-registered-vehicle/<string:id>",methods=['GET'])
def delete_registered_vehicle(id):
    if 'loggedin' in session:
        if session['type'] == 'admin':
            query = {"_id":ObjectId(id)}
            exist = db.cars.find_one(query)
            if not exist:
                return str("Invalid Vehicle Id.. Or vehicle does not exist anymore")
            # deleted = exist['name'] + " Deleted Successfully!"
            db.cars.delete_one(query)
            return redirect(url_for("registered_vehicles"))
            # return redirect("/registered-vehicles?deleted=true")
            # data = db.cars.find()
            # cars = []
            # for i in data:
            #     i.update({"_id":str(i["_id"])})
            #     cars.append(i)
            # return render_template("registered-vehicles.html",cars=cars,username=session['name'],deleted=deleted)
        else:
            return render_template("admin-login.html",error="Please Logout From User Account First!")
    else:
        return render_template("admin-login.html")

@app.route("/delete-inquiry/<string:id>",methods=['GET'])
def delete_inquiry(id):
    if 'loggedin' in session:
        if session['type'] == 'admin':
            query = {"_id":ObjectId(id)}
            exist = db.corporate_inquiries.find_one(query)
            if not exist:
                return str("Invalid inquiry Id.. Or inquiry does not exist anymore")
            deleted = exist['name'] + " Deleted Successfully!"
            db.corporate_inquiries.delete_one(query)
            return redirect(url_for('view_all_inquires'))
        else:
            return render_template("admin-login.html",error="Please Logout From User Account First!")
    else:
        return render_template("admin-login.html")

@app.route("/delete-message/<string:id>",methods=['GET'])
def delete_message(id):
    if 'loggedin' in session:
        if session['type'] == 'admin':
            query = {"_id":ObjectId(id)}
            exist = db.messages.find_one(query)
            if not exist:
                return str("Invalid message Id.. Or message does not exist anymore")
            db.messages.delete_one(query)
            return redirect(url_for('view_all_messages'))
        else:
            return render_template("admin-login.html",error="Please Logout From User Account First!")
    else:
        return render_template("admin-login.html")

@app.route("/delete-subscriber/<string:id>",methods=['GET'])
def delete_subscriber(id):
    if 'loggedin' in session:
        if session['type'] == 'admin':
            query = {"_id":ObjectId(id)}
            exist = db.subscribers.find_one(query)
            if not exist:
                return str("Invalid subscriber Id.. Or subscribers does not exist anymore")
            db.subscribers.delete_one(query)
            return redirect(url_for('view_all_subscribers'))
        else:
            return render_template("admin-login.html",error="Please Logout From User Account First!")
    else:
        return render_template("admin-login.html")
@app.route("/subscribe")
def subscribe():
    # try:
    if "email" in request.args:
        email = request.args.get("email")
    else:
        email = None
    if email:
        exist = db.subscribers.find({"email":email})
        if not exist:
            db.subscribers.insert_one({"email":email})

        msg = Message("DriveNow",sender='nasiralisw2@gmail.com', recipients=[email])
        msg.html = "<p>Thanks for subscribing</p>"
        c
        msg = Message("DriveNow | New Subscriber",sender='nasiralisw2@gmail.com', recipients=['nasiralisw2@gmail.com'])
        msg.html = "<p>Email: "+email+"</p>"
        mail.send(msg)

        return redirect(url_for("index"))
    else:
        return redirect(url_for("index"))
    # except Exception as e:
    #     return str(e)






if __name__=='__main__':
    app.run(debug=True)