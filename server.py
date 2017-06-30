from flask import Flask, request, redirect, render_template, session, flash
from validations import formIsValid
from mysqlconnection import MySQLConnector
from flask_bcrypt import Bcrypt
import datetime
app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key="secretsrunsdeep"
mysql = MySQLConnector(app, 'wall')



def printMessages():
    getMsgs = "SELECT messages.id, messages.message, messages.created_at, messages.user_id, users.first_name, users.last_name FROM messages LEFT JOIN users ON messages.user_id = users.id"
    messages = mysql.query_db(getMsgs)
    return messages


def printComments():
    getComments = "SELECT comments.id, comments.comment, comments.created_at, comments.message_id, comments.user_id, messages.id, users.first_name, users.last_name FROM comments LEFT JOIN users ON comments.user_id = users.id LEFT JOIN messages ON comments.message_id = messages.id"
    comments = mysql.query_db(getComments)
    return comments

def getAllPosts():
    messages = printMessages()
    comments = printComments()
    commentList={}
    container=[]
    for comment in comments:
        commentinfo = {
            'message_id':comment['message_id'],
            'created_at':comment['created_at'].strftime("%B %d, %Y %I:%M %p"),
            'first_name':comment['first_name'],
            'last_name':comment['last_name'],
            'comment':comment['comment']
        }
        if comment['message_id'] in commentList:
            commentList[comment['message_id']].append(commentinfo)
        else:
            commentList[comment['message_id']]=[commentinfo]
    for message in messages:
        messageinfo = {
            'message_id':message['id'],
            'first_name':message['first_name'],
            'last_name':message['last_name'],
            'message':message['message'],
            'created_at':message['created_at'].strftime("%B %d, %Y %I:%M %p")
        }
        if message['id'] in commentList:
            messageinfo['comments']= commentList[message['id']]
        container.append(messageinfo)
    return container




@app.route('/')
def index():
    if session['first_name']==None:
        session['first_name'] = ''
    if session['last_name']==None:
        session['last_name'] = ''
    if session['email']==None:
        session['email'] = ''
    if session['password']==None:
        session['password'] = ''

    if session['loggedin']==None:
        session['loggedin'] = False
    return render_template('/index.html')


@app.route('/register', methods=['POST'])
def register():
    state = formIsValid(request.form)
    if (state['isValid']):

        password = bcrypt.generate_password_hash(request.form['password'])
        query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (:first_name, :last_name, :email, :password, NOW(), NOW())"
        data = {
            'first_name' : request.form['first_name'],
            'last_name' : request.form['last_name'],
            'email': request.form['email'],
            'password': password
            }
        result=mysql.query_db(query, data)

        query2 = "SELECT * FROM users WHERE id = :id"
        data2={'id' : result}
        user = mysql.query_db(query2, data2)
        session['id']= user[0]
        return render_template('/wall.html', user=user[0])
    else:
        for error in state['errors']:
            flash(error)
            return redirect('/')

@app.route('/login', methods=['POST'])
def login():
    password = request.form['password']
    query = "SELECT * FROM users WHERE email = :email LIMIT 1"
    data = {
        'email': request.form['email'],
    }
    result= mysql.query_db(query, data)

    if bcrypt.check_password_hash(result[0]['password'], password):
        session['id'] = result[0]['id']
        return redirect('/wall')
    else:
        flash("Couldn't find you.")
        return redirect('/')

@app.route('/logout')
def logout():
    session['first_name']=''
    session['last_name']=''
    session['email']=''
    session['password']=''
    session['comfirm_password']=''
    session['id']=''
    session['loggedin']=False
    return redirect('/')

@app.route('/postMsg', methods=['POST'])
def post():
    postingMessage = request.form['message']
    query = "INSERT INTO messages (user_id, message, created_at, updated_at) VALUES (:id, :message, now(), now())"
    data={
        'id':session['id'],
        'message':postingMessage
    }
    mysql.query_db(query, data)
    return redirect('/wall')

@app.route('/postComment/<id>', methods=['POST'])
def postcomment(id):
    postingComment = request.form['comment']
    query = "INSERT INTO comments (message_id, user_id, comment, created_at, updated_at) VALUES (:messageid, :userid, :comment, now(), now())"
    data={
        'userid':session['id'],
        'comment':postingComment,
        'messageid':id
    }
    mysql.query_db(query, data)
    return redirect('/wall')

@app.route('/wall')
def wallRendered():
    id = session['id']
    query = "SELECT * FROM users WHERE id = :id"
    data = {'id':session['id']}
    user = mysql.query_db(query, data)
    print user[0]['first_name']
    messages = getAllPosts()
    return render_template('/wall.html', messages = messages, user = user)


app.run(debug=True)
