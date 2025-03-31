from app import db, TimezoneAwareModel
from datetime import datetime
from typing import List, TYPE_CHECKING
from sqlalchemy import select

if TYPE_CHECKING:
    from app.models.user import User

# Association table between users and trading strategies
user_trading_strategy = db.Table(
    "user_trading_strategy",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column(
        "trading_strategy_id",
        db.Integer,
        db.ForeignKey("trading_strategies.id"),
        primary_key=True,
    ),
    db.Column("created_at", db.DateTime, default=datetime.utcnow),
)


class TradingStrategy(TimezoneAwareModel):
    __tablename__ = "trading_strategies"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self):
        return f"<TradingStrategy {self.name}>"

    def get_users(self) -> List["User"]:
        """Get all users associated with this trading strategy"""
        from app.models.user import User

        stmt = (
            select(User)
            .join(user_trading_strategy)
            .where(user_trading_strategy.c.trading_strategy_id == self.id)
        )
        return db.session.execute(stmt).scalars().all()

    def add_user(self, user):
        """Add a user to this trading strategy"""
        if not self.id:
            # Save the trading strategy first if it doesn't have an ID
            db.session.add(self)
            db.session.flush()

        # Check if relationship already exists
        stmt = select(user_trading_strategy).where(
            user_trading_strategy.c.user_id == user.id,
            user_trading_strategy.c.trading_strategy_id == self.id,
        )
        exists = db.session.execute(stmt).first() is not None

        if not exists:
            # Create the association
            db.session.execute(
                user_trading_strategy.insert().values(
                    user_id=user.id,
                    trading_strategy_id=self.id,
                    created_at=datetime.utcnow(),
                )
            )
            return True
        return False

    def remove_user(self, user):
        """Remove a user from this trading strategy"""
        result = db.session.execute(
            user_trading_strategy.delete().where(
                user_trading_strategy.c.user_id == user.id,
                user_trading_strategy.c.trading_strategy_id == self.id,
            )
        )
        return result.rowcount > 0

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.get_datetime_in_timezone(self.created_at).strftime(
                "%Y-%m-%d %H:%M:%S %z"
            ),
            "updated_at": self.get_datetime_in_timezone(self.updated_at).strftime(
                "%Y-%m-%d %H:%M:%S %z"
            ),
        }
