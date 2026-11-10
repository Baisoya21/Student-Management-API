from getpass import getpass

from app.orm_database import SessionLocal
from app.models import ApiUser
from app.auth.security import hash_password


db = SessionLocal()

try:
    username = input("Enter username: ").strip()
    password = getpass("Enter password: ")

    school_id = int(input("Enter school ID (1 = GPS, 2 = SVS): "))
    role = input("Enter role (admin/viewer): ").strip().lower()

    if not username or not password:
        raise ValueError("Username and password cannot be empty.")

    if school_id not in [1, 2]:
        raise ValueError("Invalid school ID.")

    if role not in ["admin", "viewer"]:
        raise ValueError("Role must be admin or viewer.")

    existing_user = (
        db.query(ApiUser)
        .filter(ApiUser.username == username)
        .first()
    )

    if existing_user:
        raise ValueError("This username already exists.")

    user = ApiUser(
        school_id=school_id,
        username=username,
        password_hash=hash_password(password),
        role=role,
    )

    db.add(user)
    db.commit()

    print(f"{role.capitalize()} account created successfully.")

except Exception as error:
    db.rollback()
    print("Error:", error)

finally:
    db.close()