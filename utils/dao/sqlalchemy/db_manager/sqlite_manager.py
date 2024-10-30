from typing import List, Dict

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from utils.dao.sqlalchemy.models import ModuleOptionsAuxiliary


class DatabaseSessionManager:
    def __init__(self, db_url='sqlite:///example.db', echo=True):
        """
        Initializes the manager with database connection parameters.

        :param db_url: The database URL (default is SQLite)
        :param echo: SQLAlchemy parameter for outputting SQL queries (default is True)
        """
        self.db_url = db_url
        self.echo = echo
        self.engine = None
        self.Session: Session|None = None

    def initialize(self, base):
        """
        Initializes the database engine and creates tables based on the provided Base.

        :param base: The base class of SQLAlchemy models (e.g., Base)
        """
        if not self.engine:
            # Set up the database connection
            self.engine = create_engine(self.db_url, echo=self.echo)

            # Create all tables if they do not already exist
            base.metadata.create_all(self.engine)

            # Set up the session factory for database interaction
            self.Session = sessionmaker(bind=self.engine)

    def get_session(self):
        """
        Returns a session for working with the database.

        :return: SQLAlchemy session
        """
        if not self.Session:
            raise Exception("DatabaseSessionManager must be initialized with initialize(base) before calling "
                            "get_session().")
        return self.Session

    def add_entity_list(self, model_class, entity_list: List[Dict[str, str]]) -> None:
        """
        Adds a list of dictionaries to the database.

        :param model_class: The model class that corresponds to the table where data will be inserted.
        :param entity_list: A list of dictionaries, where each dictionary represents a row to be added.
        """
        session = self.get_session()
        try:
            # Create instances of the model class from each dictionary and add them to the session
            for entity in entity_list:
                instance = model_class(**entity)
                session.add(instance)

            # Commit all changes to the database
            session.commit()
            print(f"The Entities were added in in: {self.db_url}")
        except Exception as e:
            # Rollback the transaction in case of an error
            session.rollback()
            print(f"Error while adding data: {e}")
        finally:
            # Close the session
            session.close()

    def get_all_entities(self, model_class) -> List:
        session = self.get_session()
        all_entities = session.query(model_class).all()
        return all_entities

    def add_module_requirement_options(self,
                                       db_models,
                                       module_name: str,
                                       required_options: List[str]
                                       ):
        session = self.get_session()
        try:
            # Create a dictionary to hold the module name and its parameters
            parameters_dict = {'module_name': module_name}

            # Fill in the parameters from the required_options list
            for num in range(1, len(required_options) + 1):
                parameters_dict[f'parameter_{num}'] = required_options[num - 1]

            # Fill in the remaining parameters with None (if there are fewer than 19 required options)
            for num in range(len(required_options) + 1, 20):
                parameters_dict[f'parameter_{num}'] = None

            # Create an instance of the ModuleOptions class with the populated parameters
            instance = db_models(**parameters_dict)
            session.add(instance)

            # Commit all changes to the database
            session.commit()
            print(f"The Entities were added in: {self.db_url}")
        except Exception as e:
            # Rollback the transaction in case of an error
            session.rollback()
            print(f"Error while adding data: {e}")
        finally:
            # Close the session
            session.close()


    def get_all_sub_group_module(self) -> List:
        session = self.get_session()
        all_entities = session.query(ModuleOptionsAuxiliary).value('sub_group')
        return all_entities
