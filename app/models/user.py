from app import db
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import relationship
from typing import List, TYPE_CHECKING
import uuid

if TYPE_CHECKING:
    from app.models.prop_firm import PropFirm
    from app.models.trading_strategy import TradingStrategy

# Many-to-many relationship table between users and prop firms
user_prop_firm = db.Table(
    "user_prop_firm",
    db.Column(
        "user_id",
        db.Integer,
        db.ForeignKey("users.id"),
        primary_key=True,
    ),
    db.Column(
        "prop_firm_id",
        db.Integer,
        db.ForeignKey("prop_firms.id"),
        primary_key=True,
    ),
    db.Column(
        "created_at",
        db.DateTime,
        default=datetime.now(timezone.utc),
    ),
)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)  # Plain text for now
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )
    logged_at = db.Column(
        db.DateTime,
        default=datetime.now(timezone.utc),
    )
    token = db.Column(db.String(120), nullable=True)

    # Many-to-many relationship with prop firms
    prop_firms = relationship(
        "PropFirm", secondary=user_prop_firm, back_populates="users", lazy="dynamic"
    )

    def __repr__(self):
        return f"<User {self.email}>"

    def get_prop_firms(self) -> List["PropFirm"]:
        """
        Get prop firms for this user.

        Each returned PropFirm object has 'active_for_user' = True.
        This means the association exists.
        Access global status via 'prop_firm.is_active'.
        """
        prop_firms_list = list(self.prop_firms.all())

        for pf_object in prop_firms_list:
            pf_object.active_for_user = True  # Dynamically add attribute

        return prop_firms_list

    def add_prop_firm(self, prop_firm) -> bool:
        """Add a prop firm to this user"""
        if prop_firm not in self.prop_firms:
            self.prop_firms.append(prop_firm)
            return True
        return False

    def remove_prop_firm(self, prop_firm) -> bool:
        """Remove a prop firm from this user"""
        if prop_firm in self.prop_firms:
            self.prop_firms.remove(prop_firm)
            return True
        return False

    def get_trading_strategies(self) -> List["TradingStrategy"]:
        """Get all trading strategies associated with this user"""
        from app.models.trading_strategy import (
            TradingStrategy,
            user_trading_strategy,
        )

        stmt = (
            select(TradingStrategy)
            .join(user_trading_strategy)
            .where(user_trading_strategy.c.user_id == self.id)
        )
        return db.session.execute(stmt).scalars().all()

    def add_trading_strategy(self, trading_strategy):
        """Add a trading strategy to this user"""
        from app.models.trading_strategy import user_trading_strategy

        if not self.id:
            # Save the user first if it doesn't have an ID
            db.session.add(self)
            db.session.flush()

        # Check if relationship already exists
        stmt = select(user_trading_strategy).where(
            user_trading_strategy.c.user_id == self.id,
            user_trading_strategy.c.trading_strategy_id == trading_strategy.id,
        )
        exists = db.session.execute(stmt).first() is not None

        if not exists:
            # Create the association
            db.session.execute(
                user_trading_strategy.insert().values(
                    user_id=self.id,
                    trading_strategy_id=trading_strategy.id,
                    created_at=datetime.now(timezone.utc),
                )
            )
            return True
        return False

    def remove_trading_strategy(self, trading_strategy):
        """Remove a trading strategy from this user"""
        from app.models.trading_strategy import user_trading_strategy

        stmt = user_trading_strategy.delete().where(
            user_trading_strategy.c.user_id == self.id
        )
        stmt = stmt.where(
            user_trading_strategy.c.trading_strategy_id == trading_strategy.id
        )
        result = db.session.execute(stmt)
        return result.rowcount > 0

    def login_info(self):
        return {
            "id": self.id,
            "token": self.token,
            "logged_at": self.logged_at,
        }

    def full_user(self):
        prop_firms_details = []
        # get_prop_firms() returns PropFirms with .active_for_user
        for pf in self.get_prop_firms():
            prop_firms_details.append(
                {
                    "id": pf.id,
                    "name": pf.name,
                    "is_active_globally": pf.is_active,  # Global status
                    "active_for_user": pf.active_for_user,  # User association
                }
            )

        trading_strategies_ids = []
        for ts in self.get_trading_strategies():
            trading_strategies_ids.append(ts.id)

        return {
            "id": self.id,
            "email": self.email,
            "prop_firms": prop_firms_details,
            "trading_strategies": trading_strategies_ids,
        }

    def login(self):
        self.logged_at = datetime.now(timezone.utc)
        self.token = str(uuid.uuid4())
        db.session.commit()

    def logout(self):
        self.logged_at = None
        self.token = None
        db.session.commit()

    @staticmethod
    def get_user_by_token(token, user_id):
        return User.query.filter_by(id=user_id, token=token).first()
