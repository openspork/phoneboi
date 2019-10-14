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

class AgreementType(BaseModel):
    pass

class Agreement(BaseModel):
    company = ForeignKeyField(Company, backref="agreements")
    agreement_type = ForeignKeyField(AgreementType, backref="agreements")

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
db.create_tables([Company, Agreement, AgreementType, ConfigurationType, Configuration, Addition])
