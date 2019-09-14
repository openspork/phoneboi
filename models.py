from peewee import *

db = SqliteDatabase("database.db")


class BaseModel(Model):
    name = CharField()

    class Meta:
        database = db


class Company(BaseModel):
    pass


class ConfigurationType(BaseModel):    
    pass


class Agreement(BaseModel):
    #configuration_type = ForeignKeyField(ConfigurationType, backref='agreements')
    company = ForeignKeyField(Company, backref="agreements")

class Configuration(BaseModel):
    configuration_type = ForeignKeyField(ConfigurationType, backref="configurations")
    agreement = ForeignKeyField(Agreement, backref="configurations")

    company = ForeignKeyField(Company, backref="configurations")
    device_id = IntegerField(null=True)


class Addition(BaseModel):
    agreement = ForeignKeyField(Agreement, backref="additions")
    configuration_type = ForeignKeyField(ConfigurationType, backref='additions')
    quantity = IntegerField()
    less_included = FloatField()






db.connect()
db.create_tables([Company, Agreement, ConfigurationType, Configuration, Addition])
