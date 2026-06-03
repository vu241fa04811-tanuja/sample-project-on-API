from flask import Flask,jsonify,request,g
from pymongo import MongoClient
from bcrypt import hashpw,gensalt,checkpw
import  jwt
import time
from functools import wraps


app=Flask(__name__)

client=MongoClient('mongodb+srv://ASCII_6321:tanuja6321@cluster0.kte2ajk.mongodb.net/?appName=Cluster0')
db=client["jwt"]
users_collection=db["users"]
app.config["SECRET_KEY"]="king"
@app.route("/")
def home():
    return "hello"

@app.route('/signup', methods=["POST"])
def signup():
    data=request.get_json();
    #user=data.get("email")
    #users_collection.find_one({"email":user})
    #if user:
    #    return "already registered"

    hashed_pass=hashpw(data.get("password").encode("utf-8"),gensalt())

    new_user={
        "name":data.get("name"),
        "email":data.get("email"),
        "password":hashed_pass,
        "role":data.get("role","user")
    }
    users_collection.insert_one(new_user)
    return "user created successfully"

@app.route('/login', methods=["POST"])
def login():
    data=request.get_json();
    email=data.get("email")
    password=data.get("password")
    user=users_collection.find_one({"email":email})
    if not user:
        return jsonify({"message":"invalid user"})
    matched_pass=checkpw(password.encode("utf-8"), user["password"])
    if not matched_pass:
        return jsonify({"message":"invalid"})
    payload={
            "name":user["name"],
            "email":email,
            "role":user["role"],
            "exp":int(time.time())+360000
    }
    token=jwt.encode(payload,app.config["SECRET_KEY"],algorithm="HS256")
    return jsonify({"message":"login successfully", "token":token})
def require_auth(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):

        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return jsonify({
                "error": "Missing or invalid authorization header"
            }), 401

        token = auth_header.split(" ")[1]

        try:

            claims = jwt.decode(
                token,
                app.config["SECRET_KEY"],
                algorithms=["HS256"]
            )

            g.user_claims = claims

            return f(*args, **kwargs)

        except Exception as e:

            return jsonify({
                "error": str(e)
            }), 401

    return decorated_function

def role_auth(req_role):

    def decorator(f):

        @wraps(f)
        def decorated(*args, **kwargs):

            user_role = g.user_claims.get("role")

            if user_role != req_role:
                return jsonify({"message":"access denied"})

            return f(*args, **kwargs)

        return decorated

    return decorator


@app.route('/profile')
@require_auth
@role_auth("admin")

def profile():
    name=g.user_claims.get("name")

    return jsonify({
        "message": "Welcome to Profile",
        "name":name,
        "role":g.user_claims.get("role")
       
    })

if __name__=="__main__":
    app.run(debug=True)