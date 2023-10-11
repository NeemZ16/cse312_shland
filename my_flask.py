from flask import Flask, request, Response, render_template, make_response, abort, redirect
from pymongo import MongoClient
import json
import bcrypt
import secrets
import hashlib
import sys

app = Flask(__name__, template_folder='public/templates')
app.config['ENV'] = 'development'
allowed_images = ["eagle.jpg", "flamingo.jpg", "apple.jpg"]


def escape_html(message):
    escaped_message = message.replace("&", "&amp;")
    escaped_message = escaped_message.replace(">", "&gt;")
    escaped_message = escaped_message.replace('"', "&quot;")
    escaped_message = escaped_message.replace("'", "&#39")
    escaped_message = escaped_message.replace("<", "&lt;")

    return escaped_message

# mongo_client = MongoClient("mongodb://mongo:27017")  # Docker testing
mongo_client = MongoClient("mongodb://localhost:27017")  # local testing
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
    if request.headers.get("Cookie") is not None:
        print("cookies exist", file=sys.stderr)
        if "auth_token" in request.headers.get("Cookie"):
            print("name is not guest", file=sys.stderr)

            cookie_kvps = {}
            cookies_as_list = request.headers.get("Cookie").split(";")
            for lines in cookies_as_list:
                cookie_kvp = lines.split("=")
                cookie_kvps[cookie_kvp[0].strip()] = cookie_kvp[1].strip()

            existing_auth_token = cookie_kvps["auth_token"]

            hashed_token = hashlib.sha256(existing_auth_token.encode("utf-8")).hexdigest()

            user = user_collection.find_one({"auth_token": hashed_token})

        if user:
            username = user["username"]
    else:
        print("user is guest", file=sys.stderr)
        username = "Guest"

    posts = db.posts.find()

    response = make_response(render_template('index.html', name=username, posts=posts))
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
    new_cookie = request.headers.get("Cookie", "visits=0")
    print("Existing cookie", file=sys.stderr)
    print(new_cookie, file=sys.stderr)

    cookie_kvps = {}
    if "Cookie" in request.headers and "visits" in new_cookie:

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

        # cookie_as_list = new_cookie.split(";")
        # print("cookies as list")
        # print(cookie_as_list)

        # for lines in cookie_as_list:
        #     cookie_kvp = lines.split("=")
        #     # print("lines")
        #     # print(cookie_kvp)
        #     cookie_kvps[cookie_kvp[0].strip()] = cookie_kvp[1].strip()

        # print("new cookie kvp's")
        # print(cookie_kvps)
        new_cookie = "visits=1"

        cookie_number = 1
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
    # user_collection = db["users"]
    print("registering")

    username = request.form.get("username_reg")
    password = request.form.get("password_reg")

    username = escape_html(username)

    found_user = user_collection.find_one({"username": username})

    if found_user is not None:
        print("users exist:")
        print(found_user)
        abort(401, 'user already exists')

    print("username")
    print(type(username))
    print(username)
    print("password")
    print(password)

    if username and password:
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        user_and_pass = {"username": username, "password": hashed}
        print("user and pass")
        print(user_and_pass)
        user_collection.insert_one(user_and_pass)

    print("made it past database")
    return redirect('http://localhost:8080', code=301)


@app.route('/login', methods=['POST'])
def login():

    print("logging in")

    username = request.form.get("username_login")
    password = request.form.get("password_login")

    username = escape_html(username)

    checking_cookie = request.headers.get("Cookie")
    if "Cookie" in request.headers and "auth_token" in checking_cookie:
        abort(401, 'Already logged in as a user')


    if username and password:
        db_pass = user_collection.find_one({"username": username})  # finds a specific user

        if db_pass:  # if that user exists

            hash_pass = db_pass["password"]  # grab whats stored as their password
            if bcrypt.checkpw(password.encode("utf-8"), hash_pass):  #if the passwords match
                auth_token = secrets.token_urlsafe(32)
                hashed_token = hashlib.sha256(auth_token.encode("utf-8")).hexdigest()
                user_collection.update_one({"username": username}, {"$set": {"auth_token": hashed_token}})


                response = redirect("/", code=302)
                token_cookie = f"auth_token={auth_token}; Max-Age=3600; HttpOnly"
                response.headers["Set-Cookie"] = token_cookie

                return response

            else:
                abort(400, "Incorrect Password")

        else:
            abort(400, "No password provided")

    else:
        abort(406, 'missing username or password')


@app.route('/create-post', methods=['POST'])
def create_post():
    if "auth_token" not in request.headers.get("Cookie"):
        abort(401, "Only authenticated users can create posts")

    hashedToken = hashlib.sha256(request.headers.get("Cookie")["auth_token"].encode("utf-8")).hexdigest()
    user = user_collection.find_one({"auth_token": hashedToken})

    if user:
        username = user['username']
    else:
        abort(401, "User authentication failed")

    title = escape_html(request.form.get('title'))
    description = escape_html(request.form.get("description"))

    post = {
        'title': title,
        'description': description,
        'username': username
    }
    db.posts.insert_one(post)

if __name__ == "__main__":
    # Please do not set debug=True in production
    app.run(host="0.0.0.0", port=8080)#, debug=True)