from app.db.config import SessionLocal
from app.models.admin import Admin
from app.utils import get_password_hash
import secrets
import string

def seed_admin_user():
    db = SessionLocal()
    try:
        if not db.query(Admin).filter(Admin.username == "admin").first():
            password = '123123Aa'
            admin = Admin(
                username="admin",
                hashed_password=get_password_hash(password)
            )
            db.add(admin)
            db.commit()
            print("Usuário admin criado com sucesso! Senha: " + password)
        else:
            print("Usuário admin já existe.")
    except Exception as e:
        db.rollback()
        print("Erro ao criar seed:", e)
    finally:
        db.close()

if __name__ == "__main__":
    seed_admin_user()
