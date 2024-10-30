from typing import List, Dict

from utils.dao.sqlalchemy import db_manager
from utils.dao.sqlalchemy.db_manager import DatabaseSessionManager
from utils.dao.sqlalchemy.models import ModuleAuxiliary
from utils.msf.importing_msfinfo_database import get_required_options_msf_modules


def add_entities(db_url: str, db_base, db_models, entities_list: List[Dict[str, str]]) -> None:
    # Create an instance of the manager
    manager = db_manager.DatabaseSessionManager(db_url)

    # Initialize the manager with the Base
    manager.initialize(base=db_base)

    # Example list of dictionaries to add to the database

    # Add the data to the User table
    manager.add_entity_list(db_models, entities_list)


def get_all_entities(db_url: str, db_model, db_base) -> List[ModuleAuxiliary]:
    # Create an instance of the manager
    manager = db_manager.DatabaseSessionManager(db_url)

    # Initialize the manager with the Base
    manager.initialize(base=db_base)

    all_entities = manager.get_all_entities(db_model)

    return all_entities


def add_all_modules_requirement_options(db_url: str, db_model, db_base, all_entities):
    # Create an instance of the manager
    manager = db_manager.DatabaseSessionManager(db_url)

    # Initialize the manager with the Base
    manager.initialize(base=db_base)

    for entity in all_entities:
        module_category = entity.group
        module_name_short = entity.name.replace(f'{module_category}/', '')

        required_options = get_required_options_msf_modules(module_category, module_name_short)

        manager.add_module_requirement_options(db_model, entity.name, required_options)
