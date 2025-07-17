from app.database.db import engine
from app.models.pipeline import Base

Base.metadata.create_all(bind=engine)
print("MySQL DB initialized.")
