from datetime import datetime

from passlib.context import CryptContext
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9eeff939ad5a"
down_revision: str | None = "5d23185707bf"
branch_labels = None
depends_on = None

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

USERS = [
    {"email": "admin@example.com", "password": "admin123"},
    {"email": "user1@example.com", "password": "user123"},
]


def upgrade() -> None:
    conn = op.get_bind()
    for u in USERS:
        conn.execute(
            sa.text(
                """
                INSERT INTO users (email, password_hash, created_at)
                SELECT :email, :password_hash, :created_at
                WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = :email_check)
                """
            ),
            {
                "email": u["email"],
                "password_hash": pwd.hash(u["password"]),
                "created_at": datetime.utcnow(),
                "email_check": u["email"],
            },
        )


def downgrade() -> None:
    conn = op.get_bind()
    emails = [u["email"] for u in USERS]
    stmt = sa.text("DELETE FROM users WHERE email IN :emails").bindparams(
        sa.bindparam("emails", value=emails, expanding=True)
    )
    conn.execute(stmt)
