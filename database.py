import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Database configuration with automatic fallback to SQLite
DATABASE_URL = os.environ.get("DATABASE_URL")

# Always try SQLite first for reliability in Replit environment
if not DATABASE_URL or True:  # Force SQLite for stability
    DATABASE_URL = "sqlite:///./ai_detectors.db"
    print(f"📁 Using SQLite database: {DATABASE_URL}")

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class GeneratedToken(Base):
    """Historial de tokens generados"""
    __tablename__ = "generated_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True)
    email = Column(String)
    repo_name = Column(String)
    prefix = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    files_generated = Column(JSON)  # Lista de archivos generados

class Repository(Base):
    """Repositorios gestionados"""
    __tablename__ = "repositories"
    
    id = Column(Integer, primary_key=True, index=True)
    repo_name = Column(String, unique=True, index=True)
    email = Column(String)
    last_token_generated = Column(String, nullable=True)
    last_sync = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class CustomTemplate(Base):
    """Plantillas personalizadas de detección"""
    __tablename__ = "custom_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    template_content = Column(Text)
    language = Column(String, default="es")  # es, en, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AlertLog(Base):
    """Registro de alertas recibidas (simulación de monitoreo)"""
    __tablename__ = "alert_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String)
    ai_model = Column(String, nullable=True)
    ai_company = Column(String, nullable=True)
    purpose = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    received_at = Column(DateTime, default=datetime.utcnow)
    raw_data = Column(JSON, nullable=True)

# Create tables
def init_db():
    """Inicializar la base de datos"""
    Base.metadata.create_all(bind=engine)

# Database session helper
def get_db():
    """Obtener sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper functions
def save_generated_token(token, email, repo_name, prefix, files_list):
    """Guardar un token generado en el historial"""
    db = SessionLocal()
    try:
        generated = GeneratedToken(
            token=token,
            email=email,
            repo_name=repo_name,
            prefix=prefix,
            files_generated=files_list
        )
        db.add(generated)
        db.commit()
        db.refresh(generated)
        return generated
    finally:
        db.close()

def get_all_tokens(limit=50):
    """Obtener todos los tokens generados"""
    db = SessionLocal()
    try:
        return db.query(GeneratedToken).order_by(GeneratedToken.created_at.desc()).limit(limit).all()
    finally:
        db.close()

def get_all_repositories():
    """Obtener todos los repositorios"""
    db = SessionLocal()
    try:
        return db.query(Repository).order_by(Repository.created_at.desc()).all()
    finally:
        db.close()

def save_repository(repo_name, email):
    """Guardar o actualizar repositorio"""
    db = SessionLocal()
    try:
        existing = db.query(Repository).filter(Repository.repo_name == repo_name).first()
        if existing:
            existing.email = email
        else:
            repo = Repository(
                repo_name=repo_name,
                email=email
            )
            db.add(repo)
        db.commit()
    finally:
        db.close()

def get_custom_templates():
    """Obtener plantillas personalizadas"""
    db = SessionLocal()
    try:
        return db.query(CustomTemplate).order_by(CustomTemplate.created_at.desc()).all()
    finally:
        db.close()

def save_custom_template(name, content, language="es"):
    """Guardar plantilla personalizada"""
    db = SessionLocal()
    try:
        existing = db.query(CustomTemplate).filter(CustomTemplate.name == name).first()
        if existing:
            existing.template_content = content
            existing.language = language
            existing.updated_at = datetime.utcnow()
        else:
            template = CustomTemplate(
                name=name,
                template_content=content,
                language=language
            )
            db.add(template)
        db.commit()
    finally:
        db.close()

def get_alert_logs(limit=100):
    """Obtener logs de alertas"""
    db = SessionLocal()
    try:
        return db.query(AlertLog).order_by(AlertLog.received_at.desc()).limit(limit).all()
    finally:
        db.close()

def save_alert_log(token, ai_model=None, ai_company=None, purpose=None, ip_address=None, user_agent=None, raw_data=None):
    """Guardar log de alerta"""
    db = SessionLocal()
    try:
        alert = AlertLog(
            token=token,
            ai_model=ai_model,
            ai_company=ai_company,
            purpose=purpose,
            ip_address=ip_address,
            user_agent=user_agent,
            raw_data=raw_data
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)
        return alert
    finally:
        db.close()
