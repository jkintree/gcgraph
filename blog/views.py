from models import User, get_todays_recent_posts
from flask import Flask, request, session, redirect, url_for, render_template, flash

app = Flask(__name__)

@app.route('/')
def index():
    posts = get_todays_recent_posts()
    return render_template('index.html', posts=posts)

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        fname = request.form['fname']
        if len(username) < 1:
            flash('Your username must be at least one character.')
        elif len(password) < 5:
            flash('Your password must be at least 5 characters.')
	elif len(fname) < 2:
	    flash('Your First name must be at least 2 characters.')
        elif not User(username).register(password, fname):
            flash('A user with that username already exists.')
        else:
            session['username'] = username
            flash('Logged in.')
            return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/add_person', methods=['GET','POST'])
def add_person():
    if request.method == 'POST':
        username = request.form['username']
	gcemail = request.form['gcemail']
        password = request.form['password']
        fname = request.form['fname']
        lname = request.form['lname']
        postalcode = request.form['postalcode']
        zcountry = request.form['zcountry']
        if len(username) < 1:
            flash('Your username must be at least one character.')
        elif len(password) < 5:
            flash('Your password must be at least 5 characters.')
	elif len(fname) < 2:
	    flash('Your First name must be at least 2 characters.')
	elif len(lname) < 2:
	    flash('Your Last name must be at least 2 characters.')
	elif len(postalcode) < 5:
	    flash('Your Postal Code name must be at least 5 characters.')
	elif len(zcountry) < 2:
	    flash('Your Country must be at least 2 characters.')
        elif not User(session['username']).add_person(username, gcemail, password, fname, lname, postalcode, zcountry):
            flash('A user with that username already exists.')
        else:
            flash('Person Added.')
            return redirect(url_for('index'))
    return render_template('add_person.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not User(username).verify_password(password):
            flash('Invalid login.')
        else:
            session['username'] = username
            flash('Logged in.')
            return redirect(url_for('index'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Logged out.')
    return redirect(url_for('index'))

@app.route('/add_post', methods=['POST'])
def add_post():
    title = request.form['title']
    tags = request.form['tags']
    text = request.form['text']
    fname = request.form['fname']

    if not title or not tags or not text:
        if not title:
            flash('You must give your post a title.')
        if not tags:
            flash('You must give your post at least one tag.')
        if not text:
            flash('You must give your post a text body.')
    else:
        User(session['username']).add_post(title, tags, text, fname)

    return redirect(url_for('index'))

@app.route('/like_post/<post_id>')
def like_post(post_id):
    username = session.get('username')

    if not username:
        flash('You must be logged in to like a post.')
        return redirect(url_for('login'))

    User(username).like_post(post_id)

    flash('Liked post.')
    return redirect(request.referrer)

@app.route('/profile/<username>')
def profile(username):
    logged_in_username = session.get('username')
    user_being_viewed_username = username

    user_being_viewed = User(user_being_viewed_username)
    posts = user_being_viewed.get_recent_posts()

    similar = []
    common = []

    if logged_in_username:
        logged_in_user = User(logged_in_username)

        if logged_in_user.username == user_being_viewed.username:
            similar = logged_in_user.get_similar_users()
        else:
            common = logged_in_user.get_commonality_of_user(user_being_viewed)

    return render_template(
        'profile.html',
        username=username,
        posts=posts,
        similar=similar,
        common=common
    )
