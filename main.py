from flask import Flask, request, render_template, redirect, url_for, session, current_app, flash
from flaskext.mysql import MySQL
from flask_bootstrap import Bootstrap
from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from collections import defaultdict
import yaml
import datetime
import os 
import secrets
import sys

app = Flask(__name__)
app.config['SECRET_KEY'] = 'bigsecret!'

Bootstrap(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

mysql = MySQL()
dab = yaml.load(open('db.yaml'))
app.config['MYSQL_DATABASE_USER'] = dab['user']
app.config['MYSQL_DATABASE_PASSWORD'] = dab['password']
app.config['MYSQL_DATABASE_DB'] = dab['database']
app.config['MYSQL_DATABASE_HOST'] = dab['host']
mysql.init_app(app)


@login_manager.user_loader
def load_user(ID):
    cursor.execute('SELECT * from User where username="%s" ' % (ID)) #Fetching data for username from User table
    return cursor.fetchone()


conn = mysql.connect()
cursor = conn.cursor()

def save_photo(photo):
    rand_hex  = secrets.token_hex(10)
    _, file_extention = os.path.splitext(photo.filename)
    file_name = rand_hex + file_extention
    file_path = os.path.join(current_app.root_path, 'static/images/p_img', file_name)
    photo.save(file_path)
    return file_name

@app.route('/', methods=['GET', 'POST'])
def signup():
    conn = mysql.connect()
    cursor = conn.cursor()
    if request.method == "POST":
        
        # image = save_photo(request.files['image'])
        name = request.form.get('name')
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('pass')
        mobile = request.form.get('mobile')
        city = request.form.get('city')
        state = request.form.get('state')
        country = request.form.get('country')
        image = "ex.png"
        hashed_password = generate_password_hash(password, method='sha256')
        date = str(datetime.datetime.now())
        gender = request.form.get('gender')
        DOB = str(request.form.get('DOB'))
        Bio = str(request.form.get('Bio'))
        cursor.execute("INSERT INTO User(Name, username, Bio, Date_Created, DOB, Gender, Email, Password, image) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)",(name, username, Bio, date, DOB, gender, email, hashed_password, image)) #Inserting a new user to User table
        conn.commit() 
        cursor.execute('SELECT * from User where username="%s" ' % (username)) #Fetching data from User table for a username
        data = cursor.fetchone()
        cursor.execute("INSERT INTO Mobile(USER_ID, mobile) VALUES(%s, %s)", (data[0], mobile)) #Inserting a new user with mobile number to Mobile table
        conn.commit()
        cursor.execute("INSERT INTO Address(USER_ID, city, state, country) VALUES(%s, %s, %s, %s)", (data[0], city, state, country)) #Inserting a new user with address to Address table
        conn.commit()
        cursor.close()
        return redirect('/login')
    return render_template('signup.html')

@app.route('/pimg/<ID>', methods=['GET', 'POST'])
def pimg(ID):
    conn = mysql.connect()
    cursor = conn.cursor()
    if('user' in session):
        if request.method == "POST":
            image = request.files['image']
            img = save_photo(image)
            if('.' in img):
                cursor.execute('UPDATE User SET image="%s" Where ID="%s" ' % (img, ID)) # Update command to update profile image element with new image for a user with ID
                conn.commit()
                cursor.close()
            else:
                flash('Error! No image chosen')
            return redirect('/profile')
    cursor.close()
    return render_template('login.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if('user' in session):
        return redirect('/logout')
    conn = mysql.connect()
    cursor = conn.cursor()
    if request.method == "POST":
        userDetails = request.form
        username = userDetails['username']
        password = userDetails['pass']
        cursor.execute('SELECT * from User where username="%s" ' % (username)) #Fetching data for username from User table
        user = cursor.fetchone()
        if(user):
            if(check_password_hash(user[8],password)):
                # login_user(user)
                session['user']  = user[0]
                return redirect(url_for('home'))
            else:
                flash('Invalid username or password!')   
    cursor.close()
    return render_template('login.html')

@app.route('/logout')
def logout():
    if('user' in session):
        session.pop('user')
    return redirect('/login')

@app.route("/profile")
def profilet():
    conn = mysql.connect()
    cursor = conn.cursor()
    if('user' in session):
        cursor.execute('SELECT * from User where ID="%s" ' % (session['user'])) #Fetching data for ID from User table
        user = cursor.fetchone()
        cursor.execute('SELECT * from Mobile where USER_ID="%s" ' % (session['user'])) #Fetching data for USER_ID from Mobile table
        mobile = cursor.fetchone()
        cursor.execute('SELECT * from Address where USER_ID="%s" ' % (session['user'])) #Fetching data for USER_ID from Address table
        address = cursor.fetchone()
        return render_template('profile.html', user=user, mobile=mobile, address=address)
    cursor.close()
    return redirect('/login')

@app.route('/home', methods=['GET', 'POST'])
def home():
    conn = mysql.connect()
    cursor = conn.cursor()
    if('user' in session):
        cursor.execute('SELECT * from Tweets') #Fetching all tweets from tweets table
        tweets = list(cursor.fetchall())
        cursor.execute('SELECT * from User where ID="%s" ' % (session['user'])) #Fetching data for ID from User table
        user = list(cursor.fetchone())
        cursor.execute('SELECT * from Mobile where USER_ID="%s" ' % (session['user'])) #Fetching data for USER_ID from Mobile table
        mobile = list(cursor.fetchone())
        cursor.execute('SELECT * from Address where USER_ID="%s" ' % (session['user'])) #Fetching data for USER_ID from Address table
        address = list(cursor.fetchone())
        cursor.execute('SELECT * from User') #Fetching data for all users from User table
        users = list(cursor.fetchall())
        cursor.execute('SELECT * from Following where USER_ID="%s" ' % (session['user'])) #Fetching data for USER_ID from Following table
        following = list(cursor.fetchall())
        cursor.execute('SELECT * from Likes') #Fetching data for all USER_IDs from Likes table
        likes = list(cursor.fetchall())
        tweets = tweets[::-1] 
        k = []
        frequency = {}
        for i in likes:
            k.append(i[0])
            if(i[0] in frequency):
                frequency[i[0]] += 1
            else:
                frequency[i[0]] = 1
        f = []
        c = []
        for i in following:
            f.append(i[1])
        for i in list(users):
            if(i[0] not in f):
                c.append(i)
        return render_template('home.html', users = users, tweets = tweets, user = user, mobile = mobile, address = address, likes = frequency, following = c)
    cursor.close()
    return redirect('/login')

@app.route('/tweet', methods=['GET', 'POST'])
def tweet():
    conn = mysql.connect()
    cursor = conn.cursor()
    if('user' in session):
        if request.method == "POST":
            tweet = request.form
            text = tweet['text']
            time = str(datetime.datetime.now())
            cursor.execute("INSERT INTO Tweets(USER_ID, text, time) VALUES(%s, %s, %s)", (session['user'], text, time)) #Inserting a new tweet for USER_ID of user with text and time to Tweets table
            conn.commit()
        return redirect('/home')
    cursor.close()
    return redirect('/login')    

@app.route('/like/<string:ID>', methods = ['GET', 'POST'])
def likes(ID):
    conn = mysql.connect()
    cursor = conn.cursor()
    if('user' in session):
        if request.method == "POST":
            cursor.execute('Select * from Likes where Tweet_ID="%s" and USER_ID="%s" ' % (ID, session['user'])) #Fetching data matching with USER_ID and TWEET_ID from Likes table
            data = list(cursor.fetchall())
            if(len(data) == 0):
                cursor.execute("INSERT INTO Likes(Tweet_ID, USER_ID) VALUES(%s, %s)", (ID, session['user'])) #Inserting like for USER_ID of user and Tweet_ID of tweet to Likes table
                conn.commit()
            # else:
            #     cursor.execute('DELETE FROM Likes where Tweet_ID="%s" ' % (ID))
            #     conn.commit()
        return redirect("/home")
    cursor.close()
    return redirect('/login')

@app.route('/comment', methods = ['GET', 'POST'])
def comment():
    conn = mysql.connect()
    cursor = conn.cursor()
    if('user' in session):
        # cursor.execute('SELECT * from Comments where Tweet_ID="%s"' % (ID))
        # comments = cursor.fetchall()
        cursor.execute('SELECT * from Address where USER_ID="%s" ' % (session['user'])) #Fetching data for USER_ID from Address table
        address = cursor.fetchone()
        cursor.execute('SELECT * from User where ID="%s" ' % (session['user'])) #Fetching data for ID from User table
        user = list(cursor.fetchone())
        return render_template("comment.html", user=user, address=address)
    cursor.close()
    return redirect('/login')


@app.route('/bookmark/<string:ID>', methods = ['GET', 'POST'])
def bookmark(ID):
    conn = mysql.connect()
    cursor = conn.cursor()
    if('user' in session):
        if request.method == "POST":
            cursor.execute('Select * from Bookmarks where Tweet_ID="%s" and USER_ID="%s" ' % (ID, session['user'])) #Fetching data matching with USER_ID and TWEET_ID from Bookmarks table
            data = list(cursor.fetchall())
            if(len(data) == 0):
                cursor.execute("INSERT INTO Bookmarks(Tweet_ID, USER_ID) VALUES(%s, %s)", (ID, session['user'])) #Inserting tweet for USER_ID of user and Tweet_ID of tweet to Bookmarks table
                conn.commit()
            return redirect('/home')
    cursor.close()
    return redirect('/login')

@app.route('/delete/<string:ID>', methods = ['GET', 'POST'])
def delete(ID):
    conn = mysql.connect()
    cursor = conn.cursor()
    if('user' in session):
        if request.method == "POST":
            cursor.execute('DELETE from Tweets where ID="%s"' % (ID)) #Deleting Tweet with ID from Tweets table
            conn.commit()
            return redirect('/mytweet')
    cursor.close()
    return redirect('/login')

@app.route('/follow/<string:ID>', methods = ['GET', 'POST'])
def follow(ID):
    conn = mysql.connect()
    cursor = conn.cursor()
    if('user' in session):
        if request.method == "POST":
            cursor.execute("INSERT INTO Followers(USER_ID, Following_ID) VALUES(%s, %s)", (ID, session['user'])) #Inserting data for USER_ID of user and Following_ID of other user to Followers table
            conn.commit()
            cursor.execute("INSERT INTO Following(USER_ID, Following_ID) VALUES(%s, %s)", (session['user'], ID)) #Inserting data for USER_ID of user and Following_ID of other user to Following table
            conn.commit()
        return redirect("/home")
    cursor.close()
    return redirect('/login')

@app.route('/followers')
def follower():
    conn = mysql.connect()
    cursor = conn.cursor()
    if('user' in session):
        cursor.execute('SELECT * from User where ID="%s" ' % (session['user'])) #Fetching data for ID from User table
        user = list(cursor.fetchone())
        cursor.execute('SELECT * from User') #Fetching all users from Users table
        users = list(cursor.fetchall())
        cursor.execute('SELECT * from Mobile where USER_ID="%s" ' % (session['user'])) #Fetching data for USER_ID from Mobile table
        mobile = cursor.fetchone()
        cursor.execute('SELECT * from Address where USER_ID="%s" ' % (session['user'])) #Fetching data for USER_ID from Address table
        address = cursor.fetchone()
        cursor.execute('SELECT * from Followers where USER_ID="%s" ' % (session['user'])) #Fetching data from Followers table for USER_ID
        follower_IDs = list(cursor.fetchall())
        followers = []
        followers1 = []
        for i in follower_IDs:
            followers1.append(i[1])
        for i in users:
            if i[0] in followers1:
                followers.append(i)
        cursor.execute('SELECT * from Following where USER_ID="%s" ' % (session['user'])) #Fetching data for ID from User table
        following_IDs = list(cursor.fetchall())
        following = []
        following1 = []
        for i in following_IDs:
            following1.append(i[1])
        for i in users:
            if i[0] in following1:
                following.append(i)
        return render_template('follower.html', user=user, mobile=mobile, address=address, followers=followers, following=following)
    cursor.close()
    return redirect('/login')

@app.route('/mytweet')
def mytweet():
    conn = mysql.connect()
    cursor = conn.cursor()
    if('user' in session):
        cursor.execute('SELECT * from User') #Fetching all users from Users table
        users = list(cursor.fetchall())
        cursor.execute('SELECT * from User where ID="%s" ' % (session['user'])) #Fetching data for ID from User table
        user = cursor.fetchone()
        cursor.execute('SELECT * from Mobile where USER_ID="%s" ' % (session['user'])) #Fetching data for USER_ID from Mobile table
        mobile = cursor.fetchone()
        cursor.execute('SELECT * from Address where USER_ID="%s" ' % (session['user'])) #Fetching data for USER_ID from Address table
        address = cursor.fetchone()
        cursor.execute('SELECT * from Tweets where USER_ID="%s" ' % (session['user'])) #Fetching tweet for USER_ID from tweets table
        tweets = list(cursor.fetchall())
        cursor.execute('SELECT * from Likes') #Fetching all likes from Likes table
        likes = list(cursor.fetchall())
        tweets = tweets[::-1]
        k = []
        frequency = {}
        for i in likes:
            k.append(i[0])
            if(i[0] in frequency):
                frequency[i[0]] += 1
            else:
                frequency[i[0]] = 1
        return render_template('mytweet.html', users=users, user=user, mobile=mobile, address=address, tweets=tweets, likes=frequency)
    cursor.close()
    return redirect('/login')

@app.route('/bookmarkt')
def bookmarkt():
    conn = mysql.connect()
    cursor = conn.cursor()
    if('user' in session):
        cursor.execute('SELECT * from User') #Fetching all users from Users table
        users = list(cursor.fetchall())
        cursor.execute('SELECT * from User where ID="%s" ' % (session['user'])) #Fetching data for ID from User table
        user = cursor.fetchone()
        cursor.execute('SELECT * from Mobile where USER_ID="%s" ' % (session['user'])) #Fetching data for USER_ID from Mobile table
        mobile = cursor.fetchone()
        cursor.execute('SELECT * from Address where USER_ID="%s" ' % (session['user'])) #Fetching data for USER_ID from Address table
        address = cursor.fetchone()
        cursor.execute('SELECT * from Tweets') #Fetching all tweets from tweets table
        tweets = list(cursor.fetchall())
        cursor.execute('SELECT * from Likes') #Fetching all likes from Likes table
        likes = list(cursor.fetchall())
        cursor.execute('select Tweet_ID from Bookmarks where USER_ID="%s" ' % (session['user'])) #Fetching bookmarked tweet for user with ID from Bookmarks table
        bookmarks = list(cursor.fetchall())
        b = []
        for i in bookmarks:
            b.append(i[0])
        bookmarks = tweets[::-1]
        tweets = []
        for i in bookmarks:
            if i[0] in b:
                tweets.append(i)
        print(tweets)
        k = []
        frequency = {}
        for i in likes:
            k.append(i[0])
            if(i[0] in frequency):
                frequency[i[0]] += 1
            else:
                frequency[i[0]] = 1
        return render_template('bookmark.html', users=users, user=user, mobile=mobile, address=address, tweets=tweets, likes=frequency)
    cursor.close()
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)