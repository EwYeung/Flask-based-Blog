import os

from flask import Flask, request, render_template, redirect, url_for, flash, jsonify, make_response
#from esconfig import elasticSearch 
#from pymongo import MongoClient
from config import *
import redis
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from markupsafe import escape
from werkzeug.security import generate_password_hash as gpwh
from werkzeug.security import check_password_hash as cpwh
from utils import *


app = Flask(__name__)
jwt = JWTManager(app)
app.secret_key = '123456'
#client = MongoClient('mongodb://localhost:27017')
#db = client['usrdb']
#es = Elasticsearch("http://localhost:9200")
es = elasticSearch(index_name='posts')

@jwt.unauthorized_loader
def unauth_redirect(error_msg): 
    response = redirect(url_for('login'))
    response.headers['msg'] = error_msg
    #response = jsonify({'msg':error_msg})
    return response


@app.route('/', methods = ['GET', 'POST'])
def home():
    #return '<h1>HomePage</h1>' 
    return render_template("homePage.html")


@app.route('/register', methods = ['GET','POST'])
def register(): 
    if request.method == 'POST':
        username = request.form['username']
        password = gpwh(request.form['password'])
        #second validation
        #sec_pw = request.form['secpw']
        #if not cpwh(password, sec_pw):
        #    pass #
        #    flash('Should be same as first one')
        ##insertion
        if db.users.find_one({"username":username}) == None:
            uid = get_new_id("users")
            db.users.insert_one(
                {
                    "_id":uid,
                    "name":username, 
                    "password":password, 
                    "blogs":[], #pid
                    "following":[], #uid
                    "subscriber":[] #uid
                }
            ) 
            flash('Registration successful!', 'success')
            return redirect(url_for('login'))
        flash("Username Existed")
        return redirect(url_for('register'))
    return render_template("register.html")


@app.route('/login', methods = ['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        existed = db.users.find_one({"name":username})
        if existed == None:
            flash('Enter valid username')
            return redirect(url_for('login'))
        password = request.form["password"]
        if not cpwh(existed["password"], password):
            flash('Wrong Password')
            return redirect(url_for('login'))
        access_token = create_access_token(identity=username)  ## id? name?
        response = redirect(url_for('home')) 
        response.headers["Authorization"] = f"Bearer {access_token}"
        return response
    return render_template('login.html')

# Personal Page => Post,Browse
@app.route('/user/<int:uid>', methods = ['GET',  'POST'])
@jwt_required()
def personal_page(uid):
    current_usr = db.users.find_one({'name':get_jwt_identity()})
    status = 0
    if current_usr["_id"] == uid: status = 1
    user = db.users.find_one({"_id":uid})
    if user == None:
        return jsonify({'error':'User isn\'t existed'}), 404
    return render_template("personal_page.html",user = user,status=status)

## APIs
@app.route('/api/publish', methods = ['GET','POST'])
@jwt_required()
def pub():
    current_username = get_jwt_identity()
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        pid = get_new_id('post')
        db.post.insert_one(
            {
                "_id":pid,
                "time":os.system('date +"%Y-%m-%d %H:%M:%S"'),
                "title":title,
                "author":current_username,
                "content":content,
                "comment":[], #comment uid time
                "like": [],  #uid:time
                "repost":[]  #pid time 
            } 
        )
        return redirect(url_for('post', pid = pid))
    return render_template('publish.html')


@app.route('/post/<int:pid>', methods = ['GET', 'POST'])
@jwt_required()
def show_post(pid):
    blog = db.post.find_one({"_id":pid})
    if blog == None:
        r = make_response('Post is NOt exist')
        r.status = 404
        return r
    return render_template('post.html', blog = blog)
    
@app.route('/api/search/<str:query>', methods=['GET', 'POST'])
@jwt_required()
def search_page(query):
    data = es.search(query)
    address_data = data['hits']['hits']
    address_list = []
    for item in address_data: 
        address_list.append(item['_source'])
    new_data = jsonify(address_list)
    return make_response(new_data, content_type='application/json')

@app.route('/api/like/<int:pid>',methods = ['GET', 'POST'])
@jwt_required()
def like(pid):
    current_user = db.users.find_one({"name":get_jwt_identity()})
    uid = current_user["_id"]
    db.post.update_one({"_id":pid},{'$push':{'like':{"uid":uid, "time":os.system('date +"%Y-%m-%d %H:%M:%S"')}}})
    return None

@app.route('/api/subscribe/<int:uid>', methods = ['GET','POST'])
@jwt_required()
def subscribe(uid):
    current_user = db.user.find_one({"name":get_jwt_identity()})
    current_id = current_user["_id"]
    db.users.update_one({"_id":uid}, {'$push':{"subscribe":current_id}})
    db.users.update_one({"_id":current_id},{'$push':{'following':uid}})
    #find_and_update
    return None

@app.route('/api/repo/<int:pid>', methods = ['GET','POST'])
@jwt_required()
def repo(pid):
    current_username = get_jwt_identity()
    og_post = db.post.find_one({"_id":pid})
    if request.method == 'POST':
        repo_id = get_new_id('post')
        content = f"{request.form['content']}#{og_post["author"]}:{og_post["content"]}"
        db.post.insert_one(
                {
                    "_id":repo_id,
                    "time":os.system('date+"%Y-%m-%d %H:%M:%S"'),
                    "title":None,
                    "author":current_username,
                    "content":content,
                    "comment":[], #comment uid time
                    "like": [],  #uid:time
                    "repost":[]  #pid time 
                } 
            )
        return redirect(url_for('show_post', pid = repo_id))
    return None

@app.route('/api/comment/<int:pid>', methods = ['GET', 'POST'])
@jwt_required()
def commnent(pid):
    current_username = get_jwt_identity()
    current_user = db.users.find_one({"name":current_username})
    if request.method == 'POST':
        comment = request.form['comment']
        db.post.update_one({"_id":pid}, {"$push":{"comment":{"uid":current_user["_id"], "time":os.system('date +"%Y-%m-%d %H:%M:%S"'), "content":comment}}})
        return redirect(url_for('show_post', pid = pid))
    return None


if __name__ == '__main__':
    app.run(debug=True)


