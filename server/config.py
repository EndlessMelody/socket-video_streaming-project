# Configuration Module
"""
Central configuration management for Socket Communication System
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration"""
    
    # Project paths
    BASE_DIR = Path(__file__).parent.parent
    
    # Server configuration
    SERVER_HOST: str = os.getenv('HOST', '127.0.0.1')
    SERVER_PORT: int = int(os.getenv('PORT', '5555'))
    MAX_CONNECTIONS: int = int(os.getenv('MAX_CONNECTIONS', '100'))
    SOCKET_TIMEOUT: int = int(os.getenv('SOCKET_TIMEOUT', '300'))
    
    # Message configuration
    MESSAGE_MAX_SIZE: int = int(os.getenv('MESSAGE_MAX_SIZE', '4096'))
    ENCODING: str = os.getenv('ENCODING', 'utf-8')
    
    # Video Streaming Configuration
    BUFFER_SIZE: int = int(os.getenv('BUFFER_SIZE', '65536'))  # 64KB for video frames
    
    # Video Quality Settings
    DEFAULT_FPS: int = int(os.getenv('DEFAULT_FPS', '30'))
    DEFAULT_WIDTH: int = int(os.getenv('DEFAULT_WIDTH', '640'))
    DEFAULT_HEIGHT: int = int(os.getenv('DEFAULT_HEIGHT', '480'))
    MAX_WIDTH: int = 1920
    MAX_HEIGHT: int = 1080
    MIN_WIDTH: int = 320
    MIN_HEIGHT: int = 240
    
    # Video Quality Presets
    QUALITY_LOW = {'width': 320, 'height': 240, 'fps': 15, 'compression': 50, 'bitrate': 500_000}
    QUALITY_MEDIUM = {'width': 640, 'height': 480, 'fps': 24, 'compression': 70, 'bitrate': 1_500_000}
    QUALITY_HIGH = {'width': 1280, 'height': 720, 'fps': 30, 'compression': 85, 'bitrate': 3_000_000}
    QUALITY_ULTRA = {'width': 1920, 'height': 1080, 'fps': 30, 'compression': 90, 'bitrate': 6_000_000}
    
    # Frame Buffer Settings
    MAX_BUFFER_FRAMES: int = 60
    FRAME_DROP_THRESHOLD: float = 0.8  # Drop frames when buffer 80% full
    
    # Codec Settings
    VIDEO_CODEC: str = os.getenv('VIDEO_CODEC', 'h264')  # h264, mjpeg, vp8
    FALLBACK_CODEC: str = 'mjpeg'
    
    # Network Settings
    CHUNK_SIZE: int = 32768  # 32KB chunks for frame transmission
    MAX_FRAME_SIZE: int = 1_048_576  # 1MB max frame size
    
    # Database configuration
    DB_TYPE: str = os.getenv('DB_TYPE', 'sqlite')
    DB_NAME: str = os.getenv('DB_NAME', 'chat_server.db')
    DB_PATH: Path = BASE_DIR / DB_NAME
    
    # PostgreSQL settings (if used)
    POSTGRES_HOST: str = os.getenv('DB_HOST', 'localhost')
    POSTGRES_PORT: int = int(os.getenv('DB_PORT', '5432'))
    POSTGRES_USER: str = os.getenv('DB_USER', 'chat_user')
    POSTGRES_PASSWORD: str = os.getenv('DB_PASSWORD', '')
    POSTGRES_DB: str = os.getenv('DB_NAME', 'socket_chat')
    
    # Logging configuration
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE: str = os.getenv('LOG_FILE', 'socket_server.log')
    LOG_PATH: Path = BASE_DIR / 'logs' / LOG_FILE
    
    # Security settings
    PASSWORD_MIN_LENGTH: int = 8
    SESSION_TIMEOUT: int = 3600  # seconds
    
    # Threading configuration
    THREAD_POOL_SIZE: int = int(os.getenv('THREAD_POOL_SIZE', '50'))
    
    @classmethod
    def get_database_url(cls) -> str:
        """Get database connection URL"""
        if cls.DB_TYPE == 'postgresql':
            return f"postgresql://{cls.POSTGRES_USER}:{cls.POSTGRES_PASSWORD}@{cls.POSTGRES_HOST}:{cls.POSTGRES_PORT}/{cls.POSTGRES_DB}"
        else:
            return f"sqlite:///{cls.DB_PATH}"
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration"""
        # Create logs directory if not exists
        cls.LOG_PATH.parent.mkdir(exist_ok=True)
        
        # Validate port range
        if not (1024 <= cls.SERVER_PORT <= 65535):
            raise ValueError(f"Invalid port: {cls.SERVER_PORT}")
        
        return True


class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'
    # Use PostgreSQL in production
    DB_TYPE = 'postgresql'


class TestingConfig(Config):
    """Testing environment configuration"""
    TESTING = True
    DB_NAME = 'test_chat_server.db'
    SERVER_PORT = 5556  # Different port for testing


# Select configuration based on environment
ENV = os.getenv('ENVIRONMENT', 'development').lower()

if ENV == 'production':
    config = ProductionConfig()
elif ENV == 'testing':
    config = TestingConfig()
else:
    config = DevelopmentConfig()

# Validate configuration
config.validate()
