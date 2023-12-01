import logging

import httpx
from flask import Flask, g, request, make_response, session, redirect
from flask import Flask, request, render_template, session, jsonify
from flask_oidc import OpenIDConnect

from os.path import join, dirname, realpath
import requests

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

@app.route("/game/<playlist_id>/<int:question_number>")
async def game_test(playlist_id, question_number):
    game = await backend_request("game/" + playlist_id)
    songs = game["songs"]
    song_to_guess = game["actual_song"]

    if question_number >= 10:
        return redirect("/home")

    return render_template("game.html", playlist_id=playlist_id, question_number=question_number, songs=songs, song_to_guess=song_to_guess)

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
            return redirect(url_for("home"))
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