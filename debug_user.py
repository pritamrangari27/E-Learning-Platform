from app import create_app
from app.models import User

app = create_app('development')
with app.app_context():
    # Check if user pritam25 exists
    user = User.query.filter_by(username='pritam25').first()
    if user:
        print(f"✓ User found: {user.username}")
        print(f"  Full Name: {user.full_name}")
        print(f"  Email: {user.email}")
        print(f"  Role: {user.role}")
        # Test password
        pwd_check = user.check_password('123456')
        print(f"  Password '123456' matches: {pwd_check}")
    else:
        print("✗ User 'pritam25' NOT found in database")
    
    print("\nAll users in database:")
    all_users = User.query.all()
    for u in all_users:
        print(f"  - {u.username} ({u.full_name})")
    print(f"Total users: {len(all_users)}")
