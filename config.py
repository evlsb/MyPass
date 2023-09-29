class Configuration(object):
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    #SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://myuser:myuser@localhost/ovpn?auth_plugin=mysql_native_password'
    SQLALCHEMY_DATABASE_URI = 'postgresql://admin:admin@localhost:5432/flask_db'
    SECRET_KEY = 'Fjcm()3472'

    ### Flask-security
    SECURITY_PASSWORD_SALT = 'salt'
    # SECURITY_PASSWORD_HASH = 'sha512_crypt'