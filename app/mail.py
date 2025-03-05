from flask import (  Blueprint, render_template, request, flash, redirect, url_for, current_app)
from flask import Flask 
from dotenv import load_dotenv
from email.message import EmailMessage
import os
import ssl 
import smtplib 
from app.db import get_db

class Email:
    def __init__(self, email, name=None):
        self.email = email
        self.name = name

    def get(self):
        return {"email": self.email, "name": self.name}
    
class Content:
    def __init__(self, content_type, value):
        self.type = content_type
        self.value = value

    def get(self):
        return {"type": self.type, "value": self.value}

class To(Email):
    pass

class Mail:
    def __init__(self, from_email, to_emails, subject, content):
        self.from_email = from_email
        self.to_emails = to_emails if isinstance(to_emails, list) else [to_emails]
        self.subject = subject
        self.content = content

    def get(self):
        return {
            "from": self.from_email.get(),
            "to": [to.get() for to in self.to_emails],
            "subject": self.subject,
            "content": self.content.get()
        }

    

bp = Blueprint('mail', __name__, url_prefix='/' )

@bp.route('/', methods=['GET'])

def index():
    search = request.args.get('search')
    db, c = get_db()
    if search is None:
        c.execute("SELECT * FROM email")
    else:
        c.execute("SELECT *from email WHERE content like %s",('%' + search + '%',))

    mails = c.fetchall()

    return render_template('mails/index.html', mails = mails )

@bp.route('/create', methods =['GET','POST'])
def create():
    if request.method == 'POST':
        email = request.form.get('email')
        subject = request.form.get('subject')
        content = request.form.get('content')
        errors = []

        if not email:
            errors.append('Email es obligatorio')
        if not subject:
            errors.append('Subject es obligatorio')
        if not content:
            errors.append('Content es obligatorio')

        if len(errors) == 0:
            send(email, subject, content)
            db, c = get_db()
            c.execute("INSERT INTO email (email, subject, content) VALUES(%s, %s, %s)", (email, subject, content))
            db.commit()

            return redirect(url_for('mail.index'))
        else:
            for error in errors:
                flash(error)

    return render_template('mails/create.html')

def send(to, subject, content):
     

    PASSWORD = os.environ.get('PASSWORD_GMAIL')   

    from_email = Email(current_app.config['FROM_EMAIL'])
    from_email = 'd56181612@gmail.com' 
   
    to_email = To(to)
    content = Content('text/plain', content)
    mail= Mail(from_email, to_email, subject, content)

    from_email = mail.from_email
    to_email = to
    
    em = EmailMessage()
    em['From'] = from_email
    em['To'] =  to
    em['Subject'] = subject
    em.set_content(content.value)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context = context) as smtp:
        smtp.login(from_email, PASSWORD, )
        smtp.sendmail(from_email, to_email, em.as_string())



 