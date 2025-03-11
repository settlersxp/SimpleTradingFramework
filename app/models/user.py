from app import db
from datetime import datetime

# Many-to-many relationship table between users and prop firms
user_prop_firm = db.Table('user_prop_firm',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('prop_firm_id', db.Integer, db.ForeignKey('prop_firms.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)  # Plain text for now
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with prop firms
    prop_firms = db.relationship('PropFirm', secondary=user_prop_firm, 
                                 backref=db.backref('users', lazy='dynamic'))
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'prop_firms': [pf.id for pf in self.prop_firms]
        }
    
    def add_prop_firm(self, prop_firm):
        if prop_firm not in self.prop_firms:
            self.prop_firms.append(prop_firm)
            return True
        return False
    
    def remove_prop_firm(self, prop_firm):
        if prop_firm in self.prop_firms:
            self.prop_firms.remove(prop_firm)
            return True
        return False
