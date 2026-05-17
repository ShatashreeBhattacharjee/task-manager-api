from datetime import timedelta
class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:052005%40Sb@localhost:5432/taskmanager'
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    JWT_SECRET_KEY='Your-secret-key-change-this'
    JWT_ACCESS_TOKEN_EXPIRES=timedelta(hours=1)


