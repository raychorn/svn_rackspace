from sqlalchemy import MetaData, Table, Column, ForeignKey, types
from maintcal.model import metadata

calendar_table = Table('qcmc_calendar',
                       metadata,
                       autoload=True,
                       autoload_with=config['pylons.g'].sa_engine,
                       schema = schema_name)
scheduled_service_table = Table('qcmc_scheduled_service',
                                metadata,
                                autoload=True,
                                autoload_with=config['pylons.g'].sa_engine,
                       schema = schema_name)
log_completion_table = Table('qcmc_log_completion',
                             metadata,
                             autoload=True,
                             autoload_with=config['pylons.g'].sa_engine,
                       schema = schema_name)
scheduled_maintenance_table = Table('qcmc_scheduled_maintenance',
                                    metadata,
                                    autoload=True,
                                    autoload_with=config['pylons.g'].sa_engine,
                       schema = schema_name)
service_type_table = Table('qcmc_val_service_type',
                            metadata,
                            autoload=True,
                            autoload_with=config['pylons.g'].sa_engine,
                       schema = schema_name)
service_category_table = Table('qcmc_val_service_category',
                               metadata,
                               autoload=True,
                               autoload_with=config['pylons.g'].sa_engine,
                       schema = schema_name)
maintenance_table = Table('qcmc_val_maintenance_category',
                          metadata,
                          autoload=True,
                          autoload_with=config['pylons.g'].sa_engine,
                       schema = schema_name)