#!/usr/bin/env python
import os

class Config(object):
    BIND = '0.0.0.0'
    PORT = 7004
    DEBUG = True
    CSRF_ENABLED = True
    SECRET_KEY = 'zeevu$goof3thaNasdadasdasdasgrtry56y'
    APPLICATION_ROOT = ''
    CDN_BOOTSTRAP = "//maxcdn.bootstrapcdn.com/bootstrap/3.3.7"
    CDN_FONTAWESOME = "//maxcdn.bootstrapcdn.com/font-awesome/4.7.0"
    #CDN_COMMON = ''
    #CDN_DATATABLES = ''
    #CDN_MAVAPA = ''
    CLIENT_ID = 'k1rOkFCpQPUt1d2zb4q7ntCA'
    CLIENT_SECRET = 'SrcxrrFz5sLQtYAjghx9uqTH'
    REDIRECT_URI = 'https://donuts.example.com/mavapa/code/'
    MAVAPA_URL = 'https://accounts.example.com'
    
class Local(Config):
    STATIC = '/donuts/static'
    DEBUG = True
    APPLICATION_ROOT = '/donuts'
    MONGO_HOST = 'localhost'
    MONGO_USER = 'donutsAdmin'
    MONGO_PASSWORD = '12D0nuts78'
    MONGO_DB = 'donuts'
    MAVAPA_URL = 'http://localhost:7001/mavapa'
    CLIENT_ID = 'uq7kGEsHFLR3mlqSeIVErPQm'
    CLIENT_SECRET = '6qiyv9ItFs5WQuZu25sHhvls'
    REDIRECT_URI = 'http://localhost:7004/donuts/mavapa/code/'

class Staging(Config):
    DEBUG = True
    APPLICATION_ROOT = '/donuts'
    
class Development(Config):
    DEBUG = True
    APPLICATION_ROOT = '/donuts'
    
class Production(Config):
    MONGO_HOST = 'localhost'
    MONGO_USER = 'donutsAdmin'
    MONGO_PASSWORD = '12D0nuts78'
    MONGO_DB = 'donuts'
    
