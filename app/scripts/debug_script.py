import os
print(">>> ENV DUMP:", {
    "POSTGRES_USER": os.getenv("POSTGRES_USER"),
    "POSTGRES_PASSWORD": os.getenv("POSTGRES_PASSWORD"),
    "POSTGRES_DB": os.getenv("POSTGRES_DB"),
    "DATABASE_URL": os.getenv("DATABASE_URL")
})
