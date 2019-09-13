from peewee import *

db = SqliteDatabase('database.db')

class BaseModel(Model):
    name = CharField()
    class Meta:
        database = db

class Company(BaseModel):
    pass

class Agreement(BaseModel):
    company = ForeignKeyField(Company, backref='agreements')

class ConfigurationType(BaseModel):
    pass

class Configuration(BaseModel):
    configuration_type = ForeignKeyField(ConfigurationType, backref = 'configurations')
    configuration_type = ForeignKeyField(Agreement, backref = 'configurations')

    company = ForeignKeyField(Company, backref='agreements')
    device_id = IntegerField(null = True)






        
class Addition(BaseModel):
    agreement = ForeignKeyField(Agreement, backref='additions')
    quantity = IntegerField()
    less_included = FloatField()






db.connect()
db.create_tables([Company, Agreement, ConfigurationType, Configuration, Addition])