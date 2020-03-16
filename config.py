import os

#environment variable
basedir = os.path.abspath(os.path.dirname(__file__))

TOP_LEVEL_DIR  = os.path.abspath(os.curdir)

#configuration
class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY") or "myseckey12345"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "sqlite:///" +  os.path.join(basedir, "new.db") 
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    #whoosh search congfig
    WHOOSH_BASE = 'whoosh' + os.path.join(basedir, 'new.db')
    #maximum display post per page config
    POSTS_PER_PAGE = 3
    COMMENTS_PER_PAGE = 2
    #flask mail config
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = os.environ.get('MAIL_PORT') or 587
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') or True
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL') or False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'myemail@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or "mypassword"
    #admin email
    ADMIN = 'myemail@gmail.com'
    #flask upload config
    UPLOADS_DEFAULT_DEST = TOP_LEVEL_DIR + '/app/static/'
    UPLOADS_DEFAULT_URL = 'https//localhost:5000/static/'

    UPLOADED_IMAGES_DEST = TOP_LEVEL_DIR  + '/app/static/'
    UPLOADED_IMAGES_URL = 'https//localhost:5000/static/'
   
    
