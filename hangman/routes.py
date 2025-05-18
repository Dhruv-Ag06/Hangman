from flask import  render_template, request, redirect, url_for, flash, Blueprint, session
from flask_login import  login_user, logout_user, current_user,login_required
from hangman.forms import LoginForm, RegistrationForm, RequestResetForm, ResetPasswordForm, UpdateAccountForm
from hangman.models import User,Game,Unauthenticated_User
from hangman.utils import send_reset_email, send_confirmation_email,save_picture, serialise, deserialise, schedule_user_removal

from hangman.logic import Hangman

user=Blueprint('user',__name__)

from hangman import db,login_manager,bcrypt

@user.route("/")
@user.route("/about")
def about():
    if current_user.is_authenticated:
        return redirect(url_for('user.home'))
    return render_template("about.html")

@user.route('/home')
@login_required
def home():
    return render_template('home.html')

@user.route('/rules')
def rules():
    return render_template('rules.html')

@user.route("/profile",methods=["POST","GET"])
def profile():
    player_games=Game.query.filter_by(player=current_user)
    return render_template('profile.html',user=current_user,games=player_games.order_by(Game.date_played.desc()).all(),games_played=player_games.count())

@user.route("/register",methods=["POST","GET"])
def register():
    form=RegistrationForm()
    
    if form.validate_on_submit():  

        hashed_password=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        if not User.query.filter_by(email=form.email.data).first() and not Unauthenticated_User.query.filter_by(email=form.email.data).first() :
            user=Unauthenticated_User(username=form.username.data,email= form.email.data, password=hashed_password)
            send_confirmation_email(user)
            db.session.add(user)
            db.session.commit()
            schedule_user_removal(user)
            flash("Your account has been created! You are now able to log in after email confirmation", 'success')
            return redirect(url_for('user.login'))
        elif User.query.filter_by(email=form.email.data).first():
            flash('Email already exists.', 'danger')
            return redirect(url_for('user.register'))
        elif Unauthenticated_User.query.filter_by(email=form.email.data).first():
            flash('Email already registered. Please check your email for a confirmation link.', 'danger')
            return redirect(url_for('user.login'))
        
    return render_template('register.html', form=form)

@user.route("/confirm/<token>",methods=["GET","POST"])
def confirm_email(token):
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    email=Unauthenticated_User.verify_confirmation_token(token)
    if User.query.filter_by(email=email).first():
        flash('Account already confirmed. Please log in.', 'success')
        return redirect(url_for('user.login'))
    if not email:
        flash("Invalid or expired token", 'danger')
        return redirect(url_for('user.register'))
    user=Unauthenticated_User.query.filter_by(email=email).first()

    if user:
        new_user=User(email=user.email,username=user.username,password=user.password)
        db.session.add(new_user)
        db.session.commit()
        db.session.delete(user)
        db.session.commit()
        flash("Your account has been confirmed! You are now able to log in", 'success')
        return render_template('confirm_email.html')
    flash("Something went wrong. Please try again.","danger")
    return redirect(url_for("user.register"))


@user.route("/login",methods=["POST","GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('user.home'))
    form = LoginForm()
    if form.validate_on_submit():
        #user(email,id,username)
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user,remember=form.remember.data)
            flash('You have been logged in!', 'success')
            next_page=request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('user.home'))
        else:
            flash('Login Unsuccessful.Please check email and password','danger')
    return render_template('login.html', form=form)

@user.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('user.about'))

@user.route("/update",methods=["POST","GET"])
@login_required
def update():
    form=UpdateAccountForm()    
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.picture=picture_file
        current_user.username=form.username.data
        current_user.email=form.email.data
        db.session.commit()
        flash("Your account has been updated!","success")
        return redirect(url_for("user.profile"))
    elif request.method=="GET":
        form.username.data=current_user.username
        form.email.data=current_user.email
    picture=url_for('static',filename='profile_pics/'+current_user.picture)
    return render_template("account.html",title="Account",picture=picture,form=form)

@user.route("/reset_password",methods=["GET","POST"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form=RequestResetForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash("An email has been sent with instructions to reset your password.","info")
        return redirect(url_for("user.login"))
    return render_template("reset_request.html",title="Reset Password",form=form,legend="Reset Password")

@user.route("/reset_password/<token>",methods=["GET","POST"])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    user=User.verify_reset_token(token)
    if not user:
        flash("Invalid or expired token", "warning")
        return redirect(url_for("user.reset_request"))
    form=ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password=hashed_password
        db.session.commit()
        flash(f"Your password has been updated!You are now able to login", "success")
        return redirect(url_for("user.login"))
    return render_template("reset_token.html",title="Reset Password",form=form,legend="Reset Password")

@login_required
@user.route("/play",methods=["GET","POST"])
def play():
    if request.method=="GET":
        if 'game' not in session: 
            session['game'] = serialise(Hangman()) # Initialize the game in the session 
    game = deserialise(session['game']) 
    if request.method == 'POST' and not game.game_over: 
        guess = request.form.get('guess').casefold()
        if guess in game.guessed or guess in game.guessed_letters:
            flash("You have already tried that guess. Please enter a new guess.","danger")
        elif not guess.isalpha():
            flash("Thats not a valid guess. Please enter a letter.","danger")
        else:
            game.check_guess(guess) 
            game.check_win() 
            session['game'] = serialise(game) 
            session.modified = True 
            if game.win: 
                game=Game(word=game.word,player=User.query.filter_by(username=current_user.username).first(),status="won")   
                db.session.add(game)
                db.session.commit()             
                session.pop('game',None)
                return render_template('win.html', word=game.word) 
            elif game.game_over: 
                game=Game(word=game.word,player=User.query.filter_by(username=current_user.username).first())   
                db.session.add(game)
                db.session.commit()             
                session.pop('game',None)
                return render_template('lose.html',word=game.word) 
    return render_template('play.html', 
                            word=' '.join(game.guessed), 
                            incorrect_guesses=' '.join(game.guessed_letters),
                            hangman_drawing=game.draw_hangman())
    