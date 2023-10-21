from flask import Flask, request, Response, current_app, render_template, make_response, abort, redirect
from pymongo import MongoClient
import json
import bcrypt
import secrets
import hashlib
import sys
from bson import ObjectId

'''
Resources:
https://testdriven.io/tips/e3ecc90d-0612-4d48-bf51-2323e913e17b/#:~:text=Flask%20automatically%20creates%20a%20static,.0.1%3A5000%2Flogo.

'''

# DB AND ALLOWED IMAGE SET UP -----------------------------------------
mongo_client = MongoClient("mongodb://mongo:27017")  # Docker testing
# mongo_client = MongoClient("mongodb://localhost:27017")  # local testing
db = mongo_client["cse312"]
# db.create_collection('users')
# db.create_collection('posts')
user_collection = db["users"]
post_collection = db["posts"]

print('hello, printing mongo colletcions (local testing)')
print(db.list_collection_names())

allowed_images = ["eagle.jpg", "flamingo.jpg", "apple.jpg"]

# create instance of the class
# __name__ is convenient shortcut to pass application's module/package
app = Flask(__name__, template_folder='public/templates')

# HELPER FUNCS --------------------------------------------------------
def escape_html(message):
    escaped_message = message.replace("&", "&amp;")
    escaped_message = escaped_message.replace(">", "&gt;")
    escaped_message = escaped_message.replace('"', "&quot;")
    escaped_message = escaped_message.replace("'", "&#39")
    escaped_message = escaped_message.replace("<", "&lt;")

    return escaped_message


# PATHS (TEMPLATE/IMAGE RENDERING) ------------------------------------
# route() func tells Flask what URL should trigger the function
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
                username = "Guest"
        else:
            username = "Guest"
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
    if (image not in allowed_images):
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
    authCookie = request.headers.get("Cookie")
    if not authCookie or "auth_token" not in authCookie:
        abort(401, "Only authenticated users can create posts")

    authToken = None
    cookies = {}
    if authCookie:
        pairs = authCookie.split(';')
        for cookie in pairs:
            key, value = cookie.strip().split("=", 1)
            cookies[key] = value

    if "auth_token" in cookies:
        authToken = cookies["auth_token"]
    else:
        abort(401, "User authentication failed")

    hashedToken = hashlib.sha256(authToken.encode("utf-8")).hexdigest()
    user = user_collection.find_one({"auth_token": hashedToken})

    #since grabbing username from DB, is it enough to get away with security check?
    if user:
        username = user['username']
    else:
        abort(401, "User authentication failed")

    title = escape_html(request.form.get('title'))
    description = escape_html(request.form.get("description"))

    post = {
        'title': title,
        'description': description,
        'username': username, # may change to 'poster'
        'like-count': 0, # added like count
        'likers': [] # list of objects i.e., {'name': True/False}
    }

    db.posts.insert_one(post)

    # get id (i dont think we need this rn)
    # cursor = db.posts.find(post)
    # objectID = cursor['_id']
    # print(str(objectID))

    return redirect('http://localhost:8080', code=301)

@app.route('/get-posts', methods=['GET'])
def get_posts():
    posts = list(db.posts.find())
    for post in posts:
        post['_id'] = str(post['_id'])
    return json.dumps(posts), 200, {'Content-Type': 'application/json', "X-Content-Type-Options": "nosniff"}

@app.route('/like-post', methods=['POST'])
def like_post():
    # authenticate user
    authCookie = request.headers.get("Cookie")
    if not authCookie or "auth_token" not in authCookie:
        abort(401, "Only authenticated users can like posts")

    authToken = None
    cookies = {}
    if authCookie:
        pairs = authCookie.split(';')
        for cookie in pairs:
            key, value = cookie.strip().split("=", 1)
            cookies[key] = value

    if "auth_token" in cookies:
        authToken = cookies["auth_token"]
    else:
        abort(401, "User authentication failed")

    hashedToken = hashlib.sha256(authToken.encode("utf-8")).hexdigest()
    user = user_collection.find_one({"auth_token": hashedToken})

    if user:
        username = user['username']
        # update the post's like in db
        # get post id (from request body) and db.posts.find_one({"_id": postID})
        body = request.get_json(force=True)         # should get json from payload
        postID = body["_id"]
        post = db.posts.find_one({"_id": postID})

        # if username in likers of post: decrement like count and remove username from likers
        # else increment like count and add username to likers
        if post:
            count = post['like-count']
            likers = post['likers']
            if username in likers:
                count -= 1
                likers.remove(username)
            else:
                count += 1
                likers.append(username)

            # db.posts.update_one with the new like count and likers
            db.posts.update_one({'_id': postID}, {'$set': {'likers': likers, 'like-count': count}})

    else:
        abort(401, "User authentication failed")

    return redirect('http://localhost:8080', code=301)


# @app.route('/get_likes', method=['GET'])
# def get_likes():
#     pass


if __name__ == "__main__":
    # Please do not set debug=True in production
    app.run(host="0.0.0.0", port=8080, debug=True)