from datetime import timedelta
import os
class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL',
                                             'postgresql://postgres:newpassword123@localhost:5432/taskmanager')
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    JWT_SECRET_KEY='Your-secret-key-change-this'
    JWT_ACCESS_TOKEN_EXPIRES=timedelta(hours=1)


