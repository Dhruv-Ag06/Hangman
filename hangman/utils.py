from flask_mail import Mail, Message
from flask import url_for, current_app
import secrets,os,json,random,pickle
from PIL import Image
from datetime import datetime,timedelta
from apscheduler.triggers.date import DateTrigger

with open(r'C:\Users\Dhruv\OneDrive\ドキュメント\GitHub\Hangman\hangman\static\word_list.json', 'r') as f:
    word_list = json.load(f)
def get_random_word():
    return random.choice(word_list)

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path=os.path.join(current_app.root_path,'static/profile_pics',picture_fn)
    image=Image.open(form_picture)
    image.thumbnail((125,125))
    image.save(picture_path)
    return picture_fn

reset_mail=Mail()
def send_reset_email(user):
    token=user.get_reset_token()
    msg = Message('Password Reset Request', recipients=[user.email], sender = current_app.config['MAIL_DEFAULT_SENDER'])
    msg.body=f'''To reset your password, visit the following link:
{url_for('user.reset_token',token=token,_external=True)}

If you did not make this request then please ignore this email and no changes will be made
'''
    reset_mail.send(msg)

confirmation_mail=Mail()
def send_confirmation_email(user):
    token=user.get_confirmation_token()
    msg = Message('Email confirmation Request', recipients=[user.email], sender = current_app.config['MAIL_DEFAULT_SENDER'])
    msg.body=f'''To confirm your email, click the following link and enter this token ({token}):
{url_for('user.confirm_email',token=token,_external=True)}

If you did not make this request then please ignore this email and no changes will be made
'''
    confirmation_mail.send(msg)

def serialise(game): 
    return pickle.dumps(game) 

def deserialise(game_data): 
    return pickle.loads(game_data)


from hangman import db,scheduler
from hangman.models import Unauthenticated_User
def remove_unverified_user(user: Unauthenticated_User): 
    time_threshold = datetime.utcnow() - timedelta(seconds=1800) # Set your desired timeframe 
    if user and user.created_at<time_threshold:
        db.session.delete(user) 
    db.session.commit()
def schedule_user_removal(user): 
    removal_time = user.created_at + timedelta(minutes=30) 
    trigger = DateTrigger(run_date=removal_time) 
    scheduler.add_job(remove_unverified_user, trigger, args=[user.id])
    scheduler.start()
