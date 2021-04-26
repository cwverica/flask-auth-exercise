from flask import Flask, flash, request, redirect, render_template, session
from models import db, connect_db, User, Feedback
from forms import RegistrationForm, LoginForm, FeedbackForm
from flask_debugtoolbar import DebugToolbarExtension
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql:///user_auth')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.debug = False

connect_db(app)

app.config['SECRET_KEY'] = os.eviron.get("SECRET_KEY", "notsosecretIguess")
debug = DebugToolbarExtension(app)


################################################
# user routes
################################################

@app.route('/')
def redirect_to_register():
    return redirect('/register')

@app.route('/register', methods=["GET", "POST"])
def show_registration():
    form = RegistrationForm()

    if form.validate_on_submit():
        first_name = form.first_name.data
        username = form.username.data
        user = User.register(username,
                    form.password.data,
                    form.email.data,
                    first_name,
                    form.last_name.data)

        db.session.add(user)
        db.session.commit()

        session['username'] = username
        flash(f'Welcome, {first_name}!', 'success')
        return redirect(f'/users/{username}')
    
    return render_template('register.html', form=form)

@app.route('/login', methods=["POST", "GET"])
def show_login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter(User.username == form.username.data).first()
        if user:
            validated = User.authenticate(user.username, form.password.data)
            if validated:
                session['username'] = validated.username
                flash(f'Welcome back, {validated.first_name}.', 'info')
                return redirect(f'/users/{validated.username}')
            else:
                flash(f'Password invalid', 'danger')
                return redirect('/login')
        else:
            flash(f'Sorry, could not find {form.username.data}', 'warning')
            return redirect('/login')
    
    return render_template('login.html', form=form)

@app.route('/secret')
def show_secret():
    if session.get('username', None):
        return render_template("secret.html")

    flash(f'You must be logged in to view that page', 'danger')
    return redirect('/login')

@app.route('/users/<username>')
def show_user_page(username):
    if session.get('username', None):
        current_user = session['username']
        user = User.query.get_or_404(username)
        if username == current_user:
            return render_template('userpage.html', user=user)
        else:
            flash('You are not authorized to view this page', 'warning')
            return redirect(f'/users/{current_user}')

    flash('You must be logged in to view this page', 'danger')
    return redirect('/login')

@app.route('/logout')
def logout():
    if session.get('username', None):
        session.pop('username')
    return redirect('/login')

@app.route('/users/<username>/delete', methods=["POST"])
def delete_user(username):
    if session.get('username', None):
        current_user = session['username']
        user = Users.query.filter(User.username == username).first()
        if user:
            if user.username==current_user:
                db.session.delete(user)
                db.commit()
                session.pop('username')
                return redirect('/')
            else:
                flash('You do not have the authorization to do that', 'danger')
        else:
            flash('Could not find user', 'warning')
        return redirect(f'/users/{current_user}')
    else:
        flash('Please log in', 'info')
        return redirect('/')


################################################
# feedback routes
################################################

@app.route('/users/<username>/feedback/add', methods=["POST", "GET"])
def create_feedback(username):
    if session.get('username', None):
        current_user = session['username']
        form = FeedbackForm()
        if form.validate_on_submit():
            entry = Feedback(title=form.title.data,
                            content=form.content.data,
                            username=current_user)
            db.session.add(entry)
            db.session.commit()
            flash('Entry created', 'success')
            return redirect(f'/users/{current_user}')
        else:
            user = User.query.filter(User.username == username).first()
            if user:
                if user.username == current_user:
                    return render_template('feedback_form.html', title='New',
                     form=form, user=user)
                else:
                    flash('You are not authorized to edit that', 'danger')
            else:
                flash('Cannot find that user', 'warning')
            return redirect(f'/users/{current_user}')
    else: 
        flash('Please log in', 'info')
        return redirect('/')

@app.route('/feedback/<int:id>/update', methods=["POST", "GET"])
def update_feedback(id):
    if session.get('username', None):
        current_user = session['username']
        feedback = Feedback.query.filter(Feedback.id==id).first()
        if feedback:
            form = FeedbackForm(obj=feedback)
            if form.validate_on_submit():
                feedback.title=form.title.data
                feedback.content=form.content.data
                db.session.commit()
                flash('Entry updated', 'success')
                return redirect(f'/users/{current_user}')
            else:
                if feedback.user.username == current_user:
                    return render_template('feedback_form.html', title='Edit',
                    form=form, user=feedback.user)
                else:
                    flash('You are not authorized to edit that', 'danger')
        else:
            flash('Cannot find that feedback entry', 'warning')
        return redirect(f'/users/{current_user}')  
    else: 
        flash('Please log in', 'info')
        return redirect('/')          

@app.route('/feedback/<int:id>/delete', methods=["POST"])
def delete_feedback(id):
    if session.get('username', None):
        current_user = session['username']
        feedback = Feedback.query.filter(Feedback.id==id).first()
        if feedback:
            if feedback.user.username == current_user:
                db.session.delete(feedback)
                db.session.commit()
                flash('Feedback entry deleted', 'success')
            else:
                flash('You are not authorized to delete that', 'danger')
        else:
            flash('Cannot find that feedback entry', 'warning')
        return redirect(f'/users/{current_user}')
    else:
        flash('Please log in', 'info')
        return redirect('/') 
        
