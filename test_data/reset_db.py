from app import app, db
from app.models.prop_firm import PropFirm


def reset_database():
    with app.app_context():
        # Drop all tables
        db.drop_all()
        
        # Create all tables with new schema
        db.create_all()
        
        # Create default prop firms with all required fields
        default_firms = [
            PropFirm(
                name="Alpha Trading",
                full_balance=100000.0,
                available_balance=100000.0,
                dowdown_percentage=1.0,
                is_active=True,
                username="alpha_user",
                password="default_pass",
                ip_address="127.0.0.1",
                port=8080,
                platform_type="MT4"
            ),
            PropFirm(
                name="Beta Capital",
                full_balance=250000.0,
                available_balance=250000.0,
                dowdown_percentage=1.0,
                is_active=True,
                username="beta_user",
                password="default_pass",
                ip_address="127.0.0.1",
                port=8081,
                platform_type="MT5"
            )
        ]
        
        for firm in default_firms:
            db.session.add(firm)
        
        db.session.commit()
        print("Database reset complete with default prop firms!")

if __name__ == "__main__":
    reset_database() 