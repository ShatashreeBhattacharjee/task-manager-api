from datetime import datetime, timezone
from app import db

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
