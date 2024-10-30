import logging

from datetime import datetime
from sqlalchemy import create_engine, inspect, Engine, select, and_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, DeclarativeMeta
from typing import Type, List, Optional, Tuple

from utils.dao.sqlalchemy.models import ModuleAuxiliary, ModuleOptionsAuxiliary, DynamicConsoleResult, Base

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)


class ManagerAlchemyDB:
    """
    Database manager class for handling SQLAlchemy operations.
    """

    def __init__(self, db_url: str):
        """
        Initialize the ManagerDB with a database URL.

        :param db_url: SQLAlchemy database URL
        """
        self._engine: Engine = create_engine(db_url, echo=True, future=True)
        self._Session = sessionmaker(self._engine)

    def create_tables_by_models(self, base: Type[DeclarativeMeta]) -> None:
        """
        Create database tables based on the provided SQLAlchemy models.

        :param base: DeclarativeMeta instance containing model definitions
        """
        try:
            base.metadata.create_all(self._engine)
            logger.info("Tables created successfully")
        except SQLAlchemyError as e:
            logger.error(f"Error creating tables: {e}")

    def get_sub_group_from_modules(self) -> List[str]:
        """
        Fetch unique 'group' and 'sub_group' values from the ModuleAuxiliary table.

        :return: List of strings with 'group:sub_group' format
        """
        try:
            with self._Session() as session:
                result = session.execute(
                    select(ModuleAuxiliary.group, ModuleAuxiliary.sub_group).distinct()
                ).all()

                # Convert the result to a list of strings in the format "group:sub_group"
                return [f"{row[0]}/{row[1]}" for row in result]
        except SQLAlchemyError as e:
            logger.error(f"Error fetching group and sub_group values: {e}")
            return []

    def get_modules_by_sub_group(self, complex_name: str) -> List[Tuple[str, str]]:
        """
        Retrieve modules by their 'group:sub_group' from the ModuleAuxiliary table.

        :param complex_name: The name of the group:sub_group to filter modules by
        :return: List of tuples containing module names and descriptions
        """
        # Divide complex_name into group and sub_group
        group_name, sub_group_name = complex_name.split('/')

        try:
            with self._Session() as session:
                result = session.execute(
                    select(ModuleAuxiliary.name).
                    where(and_(ModuleAuxiliary.sub_group == sub_group_name,
                               ModuleAuxiliary.group == group_name))
                ).scalars().all()

                return result
        except SQLAlchemyError as e:
            logger.error(f"Error fetching modules for group '{group_name}' and sub_group '{sub_group_name}': {e}")
            return []

    def get_module_options(self, module_name: str) -> List[Optional[str]]:
        """
        Retrieve all non-null parameter fields for a given module.

        :param module_name: The name of the module to retrieve options for
        :return: List of non-null parameter values
        """
        try:
            fields = [getattr(ModuleOptionsAuxiliary, f"parameter_{i}") for i in range(1, 20)]
            with self._Session() as session:
                result = session.execute(
                    select(*fields).where(ModuleOptionsAuxiliary.module_name == module_name)
                ).first()
                return [value for value in result if value is not None] if result else []
        except SQLAlchemyError as e:
            logger.error(f"Error fetching options for module '{module_name}': {e}")
            return []

    def write_to_db(self, host: str, module: str, output: str, compressed_output: str) -> None:
        """
        Write console output to a dynamically named table.

        :param host: The host information
        :param module: The module name
        :param output: The console output to be stored
        :param compressed_output: Compressed console output
        """
        try:
            with self._Session() as session:
                # Generate the dynamic table name
                table_name = get_table_name()

                # Dynamically create the model class with the table name
                class ScanResult(DynamicConsoleResult):
                    __tablename__ = table_name
                    __table_args__ = {'extend_existing': True}

                # Check if the table exists, and create it if it doesn't
                inspector = inspect(self._engine)
                if not inspector.has_table(ScanResult.__tablename__):
                    Base.metadata.create_all(self._engine, tables=[ScanResult.__table__])

                # Create a new record
                new_result = ScanResult(
                    host=host,
                    module=module,
                    output=output,
                    compressed_output=compressed_output
                )

                session.add(new_result)
                session.commit()
                logger.info(f"Data successfully written to {ScanResult.__tablename__}")
        except SQLAlchemyError as e:
            logger.error(f"Error writing to database: {e}")

    def insert_module_auxiliary_data(self, data: List[dict]) -> None:
        """
        Insert multiple records into the ModuleAuxiliary table.

        :param data: List of dictionaries containing module data to be inserted
        """
        try:
            with self._Session() as session:
                # Convert each dictionary into a ModuleAuxiliary model object
                module_entries = [
                    ModuleAuxiliary(
                        group=entry.get("group"),
                        sub_group=entry.get("sub_group"),
                        name=entry.get("name"),
                        disclosure_date=entry.get("disclosure_date"),
                        rank=entry.get("rank"),
                        status_check=entry.get("status_check"),
                        description=entry.get("description")
                    ) for entry in data
                ]

                # Add all records to the session
                session.add_all(module_entries)
                # Save changes
                session.commit()
                logger.info("Data successfully inserted into ModuleAuxiliary")
        except SQLAlchemyError as e:
            logger.error(f"Error inserting data into database: {e}")

    def get_modules_by_group(self, group_name: str) -> List[str]:
        """
        Retrieve a list of modules from ModuleAuxiliary table by group.

        :param group_name: The name of the group to filter modules by
        :return: List of strings containing module details
        """
        try:
            with self._Session() as session:
                result = session.execute(
                    select(ModuleAuxiliary.name).
                    where(ModuleAuxiliary.group == group_name)
                ).all()
                # Convert the result into a list of dictionaries
                return [row[0] for row in result]
        except SQLAlchemyError as e:
            logger.error(f"Error fetching modules for group '{group_name}': {e}")
            return []

    def insert_module_options(self, module_name: str, options: List[str]) -> None:
        """
        Insert module options into the ModuleOptionsAuxiliary table.

        :param module_name: The name of the module
        :param options: List of module parameters
        """
        try:
            # Fill in the parameter fields in order, leaving None for empty fields
            option_fields = {f"parameter_{i + 1}": options[i] if i < len(options) else None for i in range(19)}

            with self._Session() as session:
                # Create a record for the module
                module_options = ModuleOptionsAuxiliary(
                    module_name=module_name,
                    **option_fields  # Передача всех параметров
                )

                # Add a record to the session
                session.add(module_options)
                # Save changes
                session.commit()
                logger.info(f"Module options for '{module_name}' successfully inserted.")
        except SQLAlchemyError as e:
            logger.error(f"Error inserting module options for '{module_name}': {e}")


def get_table_name() -> str:
    """Generate a table name based on the current date."""
    current_date = datetime.now().strftime("%Y_%m_%d")
    return f"msf_console_{current_date}"
