from getpass import getpass
from app.orm_database import SessionLocal
from app.models import ApiUser
from app.auth.security import hash_password


db = SessionLocal()

try:
    username = input("Enter admin username: ").strip()
    password = getpass("Enter admin password: ")

    if not username or not password:
        raise ValueError("Username and password cannot be empty.")

    existing_user = (
        db.query(ApiUser)
        .filter(ApiUser.username == username)
        .first()
    )

    if existing_user:
        raise ValueError("This username already exists.")

    hashed_password = hash_password(password)

    admin = ApiUser(
        school_id=1,
        username=username,
        password_hash=hashed_password,
        role="admin",
    )

    db.add(admin)
    db.commit()

    print("GPS admin account created successfully.")

except Exception as e:
    db.rollback()
    print("Error:", e)

finally:
    db.close()