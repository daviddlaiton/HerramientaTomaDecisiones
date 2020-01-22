import os

class Config:
    SECRET_KEY =  os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = "sqlite:///site.db"

    MAIL_SERVER = "pod51044.outlook.com"
    MAIL_PORT = 25
    MAIL_USE_TLS = True
    MAIL_USERNAME = "ad.laiton10@uniandes.edu.co"
    MAIL_PASSWORD = "flogin97"