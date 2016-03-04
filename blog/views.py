from models import User, get_todays_recent_posts, get_people_added
from flask import Flask, request, session, redirect, url_for, render_template, flash

app = Flask(__name__)

@app.route('/')
def index():
    if session.get('gcemail'):
#        people = User(session['gcemail']).get_people_added()
        people = get_people_added(session.get('gcemail'))
        return render_template('index.html', people=people)
#        return render_template('register.html')
    return render_template('index.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        gcemail = request.form['gcemail']
        password = request.form['password']
	fname = request.form['fname']
	lname = request.form['lname']
	postalcode = request.form['postalcode']
	zcountry = request.form['zcountry']
        if len(gcemail) < 1:
            flash('Your Email Address must be at least one character.')
        elif len(password) < 5:
            flash('Your password must be at least 5 characters.')
        elif not User(gcemail).register(password, fname, lname, postalcode, zcountry):
            flash('A user with that email address already exists.')
        else:
            session['gcemail'] = gcemail
            flash('Logged in.')
            return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/add_person', methods=['GET','POST'])
def add_person():
    if request.method == 'POST':
	gcemail = request.form['gcemail']
        password = request.form['password']
        fname = request.form['fname']
        lname = request.form['lname']
        postalcode = request.form['postalcode']
        zcountry = request.form['zcountry']
        relationship = request.form['relationship']
        if len(gcemail) < 1:
            flash('Your email address must be at least one character.')
        elif len(password) < 5:
            flash('Your password must be at least 5 characters.')
	elif len(fname) < 2:
	    flash('Your First name must be at least 2 characters.')  # I need better validation instructions
	elif len(lname) < 2:
	    flash('Your Last name must be at least 2 characters.')
	elif len(postalcode) < 5:
	    flash('Your Postal Code name must be at least 5 characters.')
	elif len(zcountry) < 2:
	    flash('Your Country must be at least 2 characters.')
	elif len(relationship) < 2:
	    flash('Your Relationship must be at least 2 characters.')
        elif not User(session['gcemail']).add_person(gcemail, password, fname, lname, postalcode, zcountry, relationship):
            flash('A user with that email address already exists.')
        else:
            flash('Person Added.')
            return redirect(url_for('index'))
    return render_template('add_person.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        gcemail = request.form['gcemail']
        password = request.form['password']

        if not User(gcemail).verify_password(password):
            flash('Invalid login.')
        else:
            session['gcemail'] = gcemail
            flash('Logged in.')
            return redirect(url_for('index'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('gcemail', None)
    flash('Logged out.')
    return redirect(url_for('index'))

@app.route('/add_post', methods=['POST'])
def add_post():
    title = request.form['title']
    tags = request.form['tags']
    text = request.form['text']

    if not title or not tags or not text:
        if not title:
            flash('You must give your post a title.')
        if not tags:
            flash('You must give your post at least one tag.')
        if not text:
            flash('You must give your post a text body.')
    else:
        User(session['gcemail']).add_post(title, tags, text)

    return redirect(url_for('index'))

@app.route('/like_post/<post_id>')
def like_post(post_id):
    gcemail = session.get('gcemail')

    if not gcemail:
        flash('You must be logged in to like a post.')
        return redirect(url_for('login'))

    User(gcemail).like_post(post_id)

    flash('Liked post.')
    return redirect(request.referrer)

@app.route('/profile/<gcemail>')
def profile(gcemail):
    logged_in_gcemail = session.get('gcemail')
    user_being_viewed_gcemail = gcemail

    user_being_viewed = User(user_being_viewed_gcemail)
    posts = user_being_viewed.get_recent_posts()

    similar = []
    common = []

    if logged_in_gcemail:
        logged_in_user = User(logged_in_gcemail)

        if logged_in_user.gcemail == user_being_viewed.gcemail:
            similar = logged_in_user.get_similar_users()
        else:
            common = logged_in_user.get_commonality_of_user(user_being_viewed)

    return render_template(
        'profile.html',
        gcemail=gcemail,
        posts=posts,
        similar=similar,
        common=common
    )
