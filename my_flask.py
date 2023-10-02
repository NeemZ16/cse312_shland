from flask import Flask, request, render_template, make_response, abort


app = Flask(__name__, template_folder='public/templates')
app.config['ENV'] = 'development'

allowed_images = ["eagle.jpg", "flamingo.jpg", "apple.jpg"]


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
    # print("Method:")
    # print(request.method)
    # print("Headers: ")
    # print(request.headers)

    response = make_response(render_template('index.html'))
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Content-Type"] = "text/html; charset=utf-8"
    response.headers["Content-Length"] = str(len(open("public/templates/index.html").read()))

    return response

@app.route('/style', methods=['GET'])
@app.route('/style.css', methods=['GET'])

def style():
    response = make_response(render_template('style.css'))
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Content-Type"] = "text/css; charset=utf-8"
    response.headers["Content-Length"] = str(len(open("public/templates/style.css").read()))

    return response

@app.route('/javascript', methods=['GET'])
@app.route('/functions.js', methods=['GET'])

def javascript():
    response = make_response(render_template('functions.js'))
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Content-Type"] = "text/javascript; charset=utf-8"
    response.headers["Content-Length"] = str(len(bytes(open("public/templates/functions.js").read(), 'utf-8')))

    return response

@app.route('/static/<image>', methods=['GET'])

def send_image(image):

    if (return_image(f"/static/{image}") == 1):
        abort(404)

    image_bytes = open(f"public/static/{image}", "rb").read()
    response = make_response(image_bytes)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Content-Type"] = "image/jpeg"
    image_length = str(len((open(f"public/static/{image}", "rb").read())))
    response.headers["Content-Length"] = image_length

    return response


# @app.route('/static/eagle.jpg', methods=['GET'])
#
# def send_eagle():
#     image_bytes = open("public/static/eagle.jpg", "rb").read()
#     response = make_response(image_bytes)
#     response.headers["X-Content-Type-Options"] = "nosniff"
#     response.headers["Content-Type"] = "image/jpeg"
#     # response.headers["Content-Length"] = str(len((open("static/eagle.jpg", "rb").read())))
#     image_length = str(len((open("public/static/eagle.jpg", "rb").read())))
#     # print(response.headers["Content-Length"])
#     response.headers["Content-Length"] = image_length
#     # print(response.headers["Content-Length"])
#
#     return response
#
# @app.route('/static/flamingo.jpg', methods=['GET'])
#
# def send_flamingo():
#     image_bytes = open("public/static/flamingo.jpg", "rb").read()
#     response = make_response(image_bytes)
#     response.headers["X-Content-Type-Options"] = "nosniff"
#     response.headers["Content-Type"] = "image/jpeg"
#     image_length = str(len((open("public/static/flamingo.jpg", "rb").read())))
#     # print(response.headers["Content-Length"])
#     response.headers["Content-Length"] = image_length
#     # print(response.headers["Content-Length"])
#
#     # response.headers["Content-Length"] = str(len((open("static/flamingo.jpg", "rb").read())))
#
#     return response

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





if __name__ == "__main__":
     # Please do not set debug=True in production
     app.run(host="0.0.0.0", port=8080, debug=True)
