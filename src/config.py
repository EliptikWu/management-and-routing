"""
Configuración de la aplicación usando Pydantic Settings
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Configuración de la aplicación desde variables de entorno"""
    
    # Base de datos
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 3306
    DATABASE_NAME: str = "ordenes_multiarea"
    DATABASE_USER: str = "root"
    DATABASE_PASSWORD: str = ""
    
    # Aplicación
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    DEBUG_MODE: bool = True
    LOG_LEVEL: str = "INFO"
    
    # Temporizador
    N_SEG: int = 10
    SLA_SEG: int = 60
    ESTADO_TIMEOUT: str = "VENCIDA"
    
    # Seguridad
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8000"]
    
    # Zona horaria
    TIMEZONE: str = "America/Bogota"
    
    @property
    def database_url(self) -> str:
        """Construye la URL de conexión a MySQL"""
        return (
            f"mysql+pymysql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
            f"?charset=utf8mb4"
        )
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Singleton de configuración"""
    return Settings()


# Instancia global
settings = get_settings()