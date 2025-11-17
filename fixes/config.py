# Minimal config used for testing; does not modify original repo
class Config:
    TESTING = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///'


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
