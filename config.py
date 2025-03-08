
class DevelopmentConfig:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:Full-Stack-dev97@localhost:3306/mechanics_db'
    CACHE_TYPE = 'SimpleCache'
    
class TestingConfig:
    pass

class ProductionConfig:
    pass