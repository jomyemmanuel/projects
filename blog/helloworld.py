import os
import re
import hashlib
import hmac
import random
import string

import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment( loader  = jinja2.FileSystemLoader( template_dir), autoescape = True)


SECRET = 'wohoo'

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(user):
    return user and USER_RE.match(user)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password and PASS_RE.match(password)

EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    return not email or EMAIL_RE.match(email)

def hash_str(s):
    return hmac.new(SECRET, s).hexdigest()

def make_secure_val(s):
    return "%s|%s" % (s, hash_str(s))

def check_secure_val(h):
    if h:
        val = h.split('|')[0]
        if h == make_secure_val(val):
            return val

def cookie_hash(h):
    return make_secure_val(str(h))

def make_salt():
    return ''.join(random.choice(string.letters) for x in xrange(5))

def make_pw_hash(name, pw, salt=None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + salt + pw).hexdigest()
    return '%s|%s' %(h,salt)

def valid_pw(name, pw, h):
    if h:
        salt = h.split('|')[1]
        return h == make_pw_hash(name, pw, salt)
       
class User(db.Model):
    user_name = db.StringProperty(required = True)
    pw_hash = db.StringProperty(required = True)
    email = db.StringProperty()

class Handler(webapp2.RequestHandler):
    def write( self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str( self, template, **params):
        params['user_main'] = self.user_main
    	t = jinja_env.get_template(template)
    	return t.render(params)

    def render(self, template, **kw):
    	self.write(self.render_str(template, **kw))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('name')
        self.user_main = uid

class MainHandler(Handler):
    def get(self):
        self.render("home.html")
        
class SignUp(Handler):
    def get(self):
        self.render("signup.html")
        
    def post(self):
        have_error = False
        user = self.request.get('user')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')
        params = dict(user = user, email = email)
        name = cookie_hash(user)
        pw_hash = make_pw_hash(str(user), password)
        
        if not valid_username(user):
            params['user_error'] = "Not a valid User Name!"
            have_error = True
        if not valid_password(password):
            params['password_error'] = "Not a valid Password!"
            have_error = True
        if password != verify:
            params['verify_error'] = "Password do not match!!"
            have_error = True
        if not valid_email(email):
            params['email_error'] = "Not a valid Email!"
            have_error = True

        exist = db.GqlQuery("select * from User where user_name = :1", str(user)).get()
        
        if not have_error:
            if exist:
                params['exist'] = "User already exits!"
                self.render("signup.html", **params)
            else:
                self.response.headers.add_header('Set-Cookie', 'name=%s; Path=/' % name)
                new_user = User(user_name = str(user), pw_hash = pw_hash, email = email)
                new_user.put()
                self.redirect('/blog')
        else:
            self.render("signup.html", **params)

class WelcomeHandler(Handler):
    def get(self):
        user = self.request.cookies.get('name')
        user = check_secure_val(user)
        if valid_username(user):
            self.render("welcome.html", user = user)
        else:
            self.redirect("/signup")

class Art(db.Model):
    title = db.StringProperty(required = True)
    textarea = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)


class Blog_New(Handler):
    def render_blog(self, title = "", textarea = "", error = ""):
        self.render("newpost.html", title = title, textarea = textarea, error = error)
    
    def get(self):
        if self.user_main:
            self.render_blog()
        else:
            self.redirect("/login")
        

    def post(self):
        if not self.user_main:
            self.redirect('/blog')
        title = self.request.get('title')
        textarea = self.request.get('textarea')

        if title and textarea:
            a = Art( title = title, textarea = textarea)
            a.put()
            self.redirect('/blog/%s' % str(a.key().id()))
        else:
            error = "Subject and Text are required fields"
            self.render_blog( title, textarea, error)

class Blog_Posted(Handler):
    def get(self, post_id):
        key = db.Key.from_path('Art', int(post_id))
        arts = db.get(key)

        if not arts:
            self.error(404)
            return

        self.render("posted.html", arts = arts)

class BlogHandler(Handler):
    def get(self):
        arts = db.GqlQuery("select * from Art order by created desc limit 10")
        self.render("blog.html", arts = arts)

class Login(Handler):
    def get(self):
        self.render("login.html")

    def post(self):
        user_name = self.request.get("user_name")
        password = self.request.get("password")
        valid = db.GqlQuery("select * from User where user_name = :1", str(user_name)).get()
        if valid and valid.user_name == str(user_name) and valid_pw(str(user_name), password, valid.pw_hash):
                name = cookie_hash(user_name)
                self.response.headers.add_header('Set-Cookie', 'name=%s; Path=/' % name)
                self.redirect("/blog")
        else:
            error = "Invalid User Name or Password!"
            self.render("login.html", user_name = user_name, error = error)

class Logout(Handler):
    def get(self):
        self.response.headers.add_header('Set-Cookie', 'name=; Path=/')
        self.redirect("/blog")


app = webapp2.WSGIApplication([
                                ('/', MainHandler),
                                ('/signup', SignUp),
                                ('/blog/newpost/?', Blog_New),
                                ('/welcome/?', WelcomeHandler),
                                ('/blog/([0-9]+)',Blog_Posted),
                                ('/blog/?', BlogHandler),
                                ('/login', Login),
                                ('/logout', Logout),
        ], debug=True)


