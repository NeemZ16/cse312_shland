from flask import Flask, request, render_template, make_response, abort, redirect
from pymongo import MongoClient
import json
import bcrypt
import secrets
import hashlib

app = Flask(__name__, template_folder='public/templates')
app.config['ENV'] = 'development'

allowed_images = ["eagle.jpg", "flamingo.jpg", "apple.jpg"]

mongo_client = MongoClient("mongo")
db = mongo_client["cse312"]
user_collection = db["users"]

def return_image(path):
    path_as_array = path.split("/")
    if (path_as_array[-1] in allowed_images):
        print("valid image request")
        return 0
    return 1


@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
@app.route('/index.html', methods=['GET'])


def index():
    response = make_response(render_template('index.html'))
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Content-Type"] = "text/html; charset=utf-8"
    # response.headers["Content-Length"] = str(len(open("public/templates/index.html").read()))

    return response

@app.route('/style', methods=['GET'])
@app.route('/style.css', methods=['GET'])

def style():
    response = make_response(render_template('style.css'))
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Content-Type"] = "text/css; charset=utf-8"
    # response.headers["Content-Length"] = str(len(open("public/templates/style.css").read()))

    return response

@app.route('/javascript', methods=['GET'])
@app.route('/functions.js', methods=['GET'])

def javascript():
    response = make_response(render_template('functions.js'))
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Content-Type"] = "text/javascript; charset=utf-8"
    # response.headers["Content-Length"] = str(len(bytes(open("public/templates/functions.js").read(), 'utf-8')))

    return response

@app.route('/static/<image>', methods=['GET'])

def send_image(image):

    if (return_image(f"/static/{image}") == 1):
        abort(404)

    image_bytes = open(f"public/static/{image}", "rb").read()
    response = make_response(image_bytes)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Content-Type"] = "image/jpeg"
    # image_length = str(len((open(f"public/static/{image}", "rb").read())))
    # response.headers["Content-Length"] = image_length

    return response

@app.route('/visit-counter', methods=['GET'])
def send_cookie():

    new_cookie = request.headers.get("Cookie","visits=1; Max-Age=3600; Path=/visit-counter")

    cookie_kvps={}
    if "Cookie" in request.headers:

        cookie_as_list = new_cookie.split(";")

        for lines in cookie_as_list:
            cookie_kvp = lines.split("=")
            cookie_kvps[cookie_kvp[0].strip()] = cookie_kvp[1].strip()

        cookie_number = cookie_kvps["visits"]
        cookie_number = int(cookie_number) + 1

        cookie_kvps["visits"] = cookie_number

        new_cookie = ""

        for key_piece in cookie_kvps:
            new_cookie += " "
            new_cookie += key_piece
            new_cookie += "="
            new_cookie += str(cookie_kvps[key_piece])
            new_cookie += ";"

        new_cookie = new_cookie.rstrip(new_cookie[-1])
    else:
        # print("cookie does not exist")

        cookie_as_list = new_cookie.split(";")
        # print("cookies as list")
        # print(cookie_as_list)

        for lines in cookie_as_list:
            cookie_kvp = lines.split("=")
            # print("lines")
            # print(cookie_kvp)
            cookie_kvps[cookie_kvp[0].strip()] = cookie_kvp[1].strip()

        # print("new cookie kvp's")
        # print(cookie_kvps)

        cookie_number = cookie_kvps["visits"]
    # print("new_visit_count")
    # print(cookie_number)
    # print("new_cookie")
    # print(new_cookie)
    new_cookie = new_cookie + '; Max-Age=3600; Path=/visit-counter'

    response = make_response(str(cookie_number))
    response.mimetype = "text/plain; charset=utf-8"
    response.headers["Set-Cookie"] = new_cookie
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Content-Length"] = str(len(str(cookie_number)))

    return response



@app.route('/register', methods=['POST'])
def register():
    username = request.form.get("username_reg")
    password = request.form.get("password_reg")
   
    if username and password:
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        user_collection.insert_one({"username": username, "password": hashed})

    return redirect('/', code = 301)

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get("username_login")
    password = request.form.get("password_login")

    #need to debug this
    if "Cookie" in request.headers:
        cookies = request.headers["Cookie"]
        listofc = cookies.split(";")
        listofitems =  listofc.split("=")
        if "auth_token" in listofitems:
            indexofkey = listofitems.index("auth_token")
            token = listofitems[indexofkey+1]
            hashed_token =  bcrypt.hashpw(token.encode("utf-8"))
            user = user_collection.find_one({"auth_token": hashed_token})
            if user:
                return redirect(f"/?name={user}", code=302)


    if username and password:
        db_pass = user_collection.find_one({"username": username})

        if db_pass:
            hash_pass = db_pass["password"]
            if bcrypt.checkpw(password.encode("utf-8"), hash_pass):
                auth_token = secrets.token_urlsafe(32)
                hashed_token = hashlib.sha256(auth_token.encode("utf-8")).hexdigest()
                user_collection.update_one({"username": username}, {"$set": {"auth_token": hashed_token}})
                response = redirect(f"/?name={username}", code=302)
                token_cookie = str(auth_token) + '; Max-Age=3600; Path=/'
                response.headers["Set-Cookie"] = token_cookie

                return response

        return "HTTP/1.1 401 Unauthorized\r\n\r\nIncorrect username or password", 401



if __name__ == "__main__":
     # Please do not set debug=True in production
     app.run(host="0.0.0.0", port=27017, debug=True)
