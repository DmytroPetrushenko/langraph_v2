from datetime import datetime

from sqlalchemy import Column, String, Integer, LargeBinary
from sqlalchemy.orm import declarative_base, declared_attr

# Create a base class for defining models
Base = declarative_base()


class ModuleAuxiliary(Base):
    __tablename__ = 'modules'  # Table name

    id = Column(Integer, primary_key=True)  # Unique identifier
    group = Column(String, nullable=False)
    sub_group = Column(String, nullable=False)
    name = Column(String, nullable=False)  # Module name
    disclosure_date = Column(String, nullable=True)  # Vulnerability disclosure date
    rank = Column(String, nullable=False)  # Module rank
    status_check = Column(String, default='No')  # Does the module support
    # vulnerability check?
    description = Column(String, nullable=True)  # Module description


class ModuleOptionsAuxiliary(Base):
    __tablename__ = 'module_options_auxiliary'

    id = Column(Integer, primary_key=True)
    module_name = Column(String, nullable=False)

    parameter_1 = Column(String, nullable=True)
    parameter_2 = Column(String, nullable=True)
    parameter_3 = Column(String, nullable=True)
    parameter_4 = Column(String, nullable=True)
    parameter_5 = Column(String, nullable=True)
    parameter_6 = Column(String, nullable=True)
    parameter_7 = Column(String, nullable=True)
    parameter_8 = Column(String, nullable=True)
    parameter_9 = Column(String, nullable=True)
    parameter_10 = Column(String, nullable=True)
    parameter_11 = Column(String, nullable=True)
    parameter_12 = Column(String, nullable=True)
    parameter_13 = Column(String, nullable=True)
    parameter_14 = Column(String, nullable=True)
    parameter_15 = Column(String, nullable=True)
    parameter_16 = Column(String, nullable=True)
    parameter_17 = Column(String, nullable=True)
    parameter_18 = Column(String, nullable=True)
    parameter_19 = Column(String, nullable=True)



class DynamicConsoleResult(Base):
    """Base class for dynamically named console result tables."""
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    host = Column(String)
    module = Column(String)
    output = Column(String)
    compressed_output = Column(String)
