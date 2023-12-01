import logging
import httpx
from flask import Flask, g, request, make_response, session, redirect, Request, Response, url_for
from flask import Flask, request, render_template, session, jsonify
from flask_oidc import OpenIDConnect
from os.path import join, dirname, realpath
import requests
import random


UPLOADS_PATH = join(dirname(realpath(__file__)), 'client_secrets.json')

logging.basicConfig(level=logging.DEBUG)


backend_url = "http://backend:8081/api/"

app = Flask(__name__,template_folder="templates", static_folder="static")

print(UPLOADS_PATH)
app.config.update({
    'SECRET_KEY': 'SomethingNotEntirelySecret',
    'TESTING': True,
    'DEBUG': True,
    'OIDC_CLIENT_SECRETS': UPLOADS_PATH,
    'OIDC_ID_TOKEN_COOKIE_SECURE': False,
    'OIDC_USER_INFO_ENABLED': True,
    'OIDC_OPENID_REALM': 'master',
    'OIDC_SCOPES': ['openid', 'email', 'profile'],
    'OIDC_INTROSPECTION_AUTH_METHOD': 'client_secret_post'
})

oidc = OpenIDConnect(app)

@app.before_request
def before_request():
    if oidc.user_loggedin:
        pass
    else:
        g.user = None

def get_user_data():

    user_data = None
    if oidc.user_loggedin:
        try:
            access_token = oidc.get_access_token()
            headers = {'Authorization': 'Bearer %s' % (access_token)}
            user_data = requests.get('http://backend:8081/user_data', headers=headers).json()
        except:
            user_data = "404"

    return user_data

@app.route("/")
def welcome():
    return render_template("welcome.html", userinfo=get_user_data())


@app.route("/home")
def home():
    return render_template("home.html", userinfo=get_user_data())


@app.route("/playlists")
async def display_playlists():
    top_playlists = await backend_request("playlists/top")

    top_playlists = top_playlists["playlists"]
    return render_template("new_playlist.html", userinfo=get_user_data(), top_playlists=top_playlists)


@app.route("/playlists/<int:id>")
def specific_playlists(id):
    return render_template("playlist_id.html", id_playlist=id)

@app.route("/songs/<int:id>")
def specific_songs(id):
    return render_template("song_id.html", id_song=id)

@app.route("/search_songs")
def search_songs():
    return render_template("search_songs.html")

@app.route("/add", methods=["POST"])
async def add_user():
    name = request.form["name"]
    username = request.form["username"]
    email = request.form["email"]
    password = request.form["password"]
    async with httpx.AsyncClient() as clientT:
        response = await clientT.get(backend_url + "user/add", params={"name": name, "username": username, "email": email, "password": password})

        if response.status_code == 200:
            return redirect("/home")
        else:
            return jsonify({"error": response.text})

@app.route("/profile")
@oidc.require_login
def display_userinfo():

    return render_template("profile.html", user_data = get_user_data()["data"])

@app.route("/login")
def login_page():
    return render_template("new_login.html")


@app.before_request
def create_auth_header():
    access_token = request.cookies.get("Authorization")
    if access_token:
        request.headers["Authorization"] = f"Bearer {access_token}"


@app.route('/log')
def hello_world():

    if oidc.user_loggedin:
        return ('Hello, %s, <a href="/private">See private</a> '
                '<a href="/logout">Log out</a>') % \
            oidc.user_getfield('preferred_username')
    else:
        return 'Welcome anonymous, <a href="/private">Log in</a>'


@app.route('/private')
@oidc.require_login
def hello_me():

    if oidc.user_loggedin:

        info = oidc.user_getinfo(['preferred_username', 'email', 'sub'])

        username = info.get('preferred_username')
        user_id = info.get('sub')

        # access_token = OAuth2Credentials.from_json(oidc.credentials_store[user_id]).access_token
        access_token = oidc.get_access_token()
        greeting = access_token
        headers = {'Authorization': f'Bearer {access_token}'}
        # YOLO
        greeting = requests.get('http://backend:8081/user_data', headers=headers).json()
        email = greeting["user_infos"]["email"]

    return ("""%s your email is %s and your user_id is %s!
               <ul>
                 <li><a href="/">Home</a></li>
                 <li><a href="//localhost:8080/auth/realms/master/account?referrer=flask-app&referrer_uri=http://localhost:5000/private&">Account</a></li>
                </ul>""" %
            (greeting, email, user_id))


@app.route('/logout')
def logout():
    """Performs local logout by removing the session cookie."""

    res = make_response('Hi, you have been logged out! <a href="/">Return</a>')
    session.clear()
    oidc.logout()
    requests.get("http://localhost:8080/auth/realms/master/protocol/openid-connect/logout")
    return res

async def backend_request(endpoint: str, params=None):
    async with httpx.AsyncClient() as clientT:
        response = await clientT.get(backend_url + endpoint,
                                     params=params)
        if response.status_code == 200:
            return response.json()

        else:
            return {"error": "error"}


@app.route("/import_playlist_spotify")
def import_playlist_spotify():
    return render_template("import_playlist_spotify.html")

@app.route("/import_playlist_spotify/<string:playlist_url_id>")
async def add_spotify_playlist(playlist_url_id: str):
    result = await backend_request("add_spotify_playlist/" + playlist_url_id)
    print("RESULT :", result)
    return result


## FONCTION DE JEU


@app.route("/game/check_answer/<string:song_id>")
async def check_answer(song_id :str):
    true_answer = request.cookies.get("true_answer")
    state = request.args.get('state')
    state_cookie = request.cookies.get("state")


    playlist_id = request.args.get('playlist_id')
    question_number = request.args.get('question_number')

    response = make_response(redirect("/game/" + str(playlist_id) + "/" + str(int(question_number)), code=303))

    if state == state_cookie and song_id == true_answer:
        current_score = request.cookies.get("score",0)
        current_score = int(current_score) + 1
        response.set_cookie("score", str(current_score), max_age=3600)
        response.set_cookie("state", "", max_age=3600)

    return response

@app.route("/game/<string:playlist_id>/<int:question_number>")
async def game_test(playlist_id: str, question_number: int):

    hash_random = random.getrandbits(128)

    if "question_number" not in request.cookies:
        question_number_cookie = 1
    else:
        question_number_cookie = request.cookies["question_number"]

    if int(question_number_cookie) != question_number:
        response = redirect(url_for("game_test", playlist_id=playlist_id, question_number=1), code=303)
        response.set_cookie("state", str(hash_random))
        response.set_cookie("question_number", "1", max_age=30)
        return response
    
    if question_number >= 11:
        score = request.cookies.get("score",0)
        response = make_response(render_template("result.html", score = score))
    
        response.set_cookie("question_number", "1", max_age=30)
        response.set_cookie("score", "0", max_age=3600)

        if int(question_number_cookie) >=10:
            return response
        else:
            return {"You tried to cheat!":"loser!"}
    



    
    game = await backend_request("game/" + playlist_id)

    songs = game["songs"]
    song_to_guess = game["actual_song"]

 
    response = make_response(render_template("game.html",
                                          playlist_id = playlist_id, 
                                          question_number = question_number,
                                          state = str(hash_random),
                                          songs = songs,
                                          song_to_guess= song_to_guess))

    response.set_cookie("question_number", str(question_number+1), max_age=3600)
    response.set_cookie("true_answer", str(song_to_guess['id']), max_age=300)
    response.set_cookie("state", str(hash_random), max_age=300)
    return response


