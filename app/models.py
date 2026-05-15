from datetime import datetime, timezone
from app import db
from werkzeug.security import generate_password_hash,check_password_hash

class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task = db.Column(db.String(300), nullable=False)
    done = db.Column(db.Boolean, default=False)

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self):
        return {
            "id": self.id,
            "task": self.task,
            "done": self.done,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
class User(db.Model):
    __tablename__="users"
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    username=db.Column(db.String(80),nullable=False,unique=True)
    password_hash=db.Column(db.String(200),nullable=False)

    created_at=db.Column(db.DateTime,
                         default=lambda: datetime.now(timezone.utc)
                         )
    def set_password(self,password):
        self.password_hash=generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.password_hash,password)
    def to_dict(self):
        return {
            "id":self.id,
            "username":self.username,
            "created_at":self.created_at.isoformat()
         }



