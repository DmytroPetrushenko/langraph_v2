import re
import sqlite3
import sqlite3 as sqlite
from typing import List, Dict


def create_connection(db_file="my_sqlite.db"):
    """
    Create a connection to an SQLite database that resides in memory
    """

    conn = None
    try:
        conn = sqlite.connect(db_file)
        return conn
    except sqlite.Error as e:
        print(e)
    return conn


def create_table(conn, table_name: str, table_fields: dict[str, list[str]] = None)-> bool:
    """Create a table to store the results with the given table name if it does not exist and is a valid identifier."""

    # Validate the table name against a regular expression pattern to ensure it's a valid identifier
    if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", table_name):
        raise ValueError(
            "Invalid table name. Table names must start with a letter or underscore and contain only letters, digits, "
            "and underscores.")

    # Check if the table already exists
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    if cursor.fetchone():
        print(f"Table '{table_name}' already exists.")
        return True

    # SQL to create a new table
    if table_fields is None:
        sql = f"""
        CREATE TABLE {table_name} (
            uuid TEXT NOT NULL PRIMARY KEY,
            status TEXT NOT NULL,
            host TEXT NOT NULL,
            module TEXT NOT NULL,
            result TEXT 
        );
        """
    else:
        sql = f'CREATE TABLE {table_name} ('
        for field_name, parameters in table_fields.items():
            sql += f'{field_name.lower()} {" ".join(parameters).upper()}, '
        sql = sql.rstrip(', ')  # Remove the trailing comma and space
        sql += ');'

    try:
        cursor.execute(sql)
        conn.commit()
        print(f"Table '{table_name}' created successfully.")
        return True
    except sqlite.Error as e:
        print(f"An error occurred while creating the table {table_name}: {e}")
        conn.rollback()  # Rollback in case of an error to maintain database integrity
        return False


def insert_data(conn, table_name: str, table_values: Dict[str, str], logger) -> bool:
    """
    Insert a new result into the specified table.

    Args:
        conn (sqlite3.Connection): Connection to the SQLite database.
        table_name (str): Name of the table into which the data will be inserted.
        table_values (Dict[str, str]): Dictionary containing the column names and values to be inserted.
        logger (PerformanceLogger): Logger instance for logging.

    Returns:
        bool: True if the insertion was successful, False otherwise.
    """
    # Validate that table fields match the keys in table_values
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name});")
    table_info = cursor.fetchall()

    table_columns = {column[1].lower() for column in table_info}
    value_columns = {key.lower() for key in table_values.keys()}

    if not value_columns.issubset(table_columns):
        missing_columns = value_columns - table_columns
        logger.error(f"The following columns are missing in the table {table_name}: {missing_columns}")
        return False

    # Creating the SQL query dynamically
    sql_1 = f'INSERT INTO {table_name} ('
    sql_2 = ') VALUES ('

    columns = []
    values = []

    for field_name, value in table_values.items():
        columns.append(f'"{field_name.lower()}"')
        values.append(value)
        sql_2 += '?, '

    sql = sql_1 + ', '.join(columns) + sql_2.rstrip(', ') + ')'

    try:
        cur = conn.cursor()
        cur.execute(sql, values)  # Parameterized input protects against SQL injections.
        conn.commit()  # Commit changes to save them to the database.
        logger.info(f"Data inserted successfully into table {table_name}.")
        return True
    except sqlite3.Error as e:
        logger.error(f"Error inserting data into table {table_name}: {e}")
        conn.rollback()  # Rollback changes in case of an error.
        return False



def get_result_by_uuid(conn, table_name, uuid) -> str:
    """
    Retrieve the result for a specific UUID from the specified table.

    Args:
    conn (sqlite3.Connection): The database connection object.
    table_name (str): The name of the table from which to retrieve the result.
    uuid (str): The UUID for which to retrieve the result.

    Returns:
    str: The result associated with the given UUID, or an empty string if not found or in case of an error.
    """
    sql = f"SELECT result FROM {table_name} WHERE uuid=?"
    try:
        cur = conn.cursor()
        cur.execute(sql, (uuid,))
        result = cur.fetchone()  # Fetch the first row of the results
        if result:
            return result[0]  # Return the first column of the row, which is the result
        return ""  # Return empty string if no result is found
    except sqlite.Error as e:
        print(f"Error retrieving data from table {table_name}: {e}")
        return ""  # Return empty string in case of an error


def get_uuid_by_status(conn, table_name, status="running") -> list:
    """
    Retrieve a list of UUIDs from a specified table where the status matches the given status.

    Args:
    conn (sqlite3.Connection): The database connection object.
    table_name (str): The name of the table from which to retrieve UUIDs.
    status (str): The status value to filter the UUIDs.

    Returns:
    list: A list of UUIDs that match the given status.
    """
    sql = f"SELECT uuid FROM {table_name} WHERE status=?"
    try:
        cur = conn.cursor()
        cur.execute(sql, (status,))
        # Fetch all matching rows and extract the first column (uuid)
        result = cur.fetchall()
        return [row[0] for row in result]
    except sqlite.Error as e:
        print(f"Error querying data from table {table_name}: {e}")
        return []  # Return an empty list in case of error


def get_results_by_table_name(conn, table_name) -> list:
    """
    Retrieve all results from a specified table where the status is 'completed'.

    Args:
    conn (sqlite3.Connection): The database connection object.
    table_name (str): The name of the table from which to retrieve the results.

    Returns:
    list: A list of results where the status is 'completed', or an empty list if no results are found or in case of an
    error.
    """
    sql = f"SELECT host, module, result FROM {table_name} WHERE status=?"
    try:
        cur = conn.cursor()
        cur.execute(sql, ("completed",))  # Use parameterized SQL to prevent SQL injection
        results = cur.fetchall()
        return [{'host': result[0], 'module': result[1], 'result': result[2]} for result in results] # Return a list of results, extracting from tuples returned by
        # fetchall()
    except sqlite.Error as e:
        print(f"Error retrieving data from table {table_name}: {e}")
        return []  # Return an empty list in case of an error


def set_status_by_uuid(conn, table_name, uuid, status):
    """
    Update the status of an entry in the specified table based on its UUID.

    Args:
        conn (sqlite3.Connection): The connection object to the database.
        table_name (str): The name of the table where the entry is to be updated.
        uuid (str): The unique identifier of the entry to update.
        status (str): The new status to set for the entry.

    Returns:
        bool: True if the update was successful, False otherwise.

    Raises:
        sqlite3.Error: Outputs an error message if an SQLite error occurs during the execution.
    """
    # SQL query to update the status of a specific entry identified by its UUID
    sql = f"UPDATE {table_name} SET status=? WHERE uuid=?"
    try:
        cur = conn.cursor()  # Create a cursor object using the connection
        cur.execute(sql, (status, uuid))  # Execute the SQL command with parameters
        conn.commit()  # Commit changes to the database
        return True
    except sqlite.Error as e:
        print(f"Error updating {status} status in table {table_name} by {uuid}: {e}")
        return False


def set_result_by_uuid(db_connection, table_name, uuid, result):
    """
    Update the result column of a specific record in a SQLite table based on the UUID.

    Args:
    conn (sqlite3.Connection): The database connection object.
    table_name (str): The name of the table where the update will occur.
    uuid (str): The UUID of the record to be updated.
    result (any): The new value to be set for the result column.

    Returns:
    bool: True if the update was successful, False otherwise.
    """
    # SQL query to update the 'result' column where 'uuid' matches
    sql = f"""
    UPDATE {table_name} 
    SET result = ? WHERE uuid = ?
    """

    try:
        # Creating a cursor from the connection
        cur = db_connection.cursor()
        # Executing the SQL command with parameters to prevent SQL injection
        cur.execute(sql, (str(result), uuid))
        # Committing the transaction to the database
        db_connection.commit()
        return True
    except sqlite.Error as e:
        # Handling exceptions and printing an error message
        print(f"Error updating a result in table {table_name} by {uuid}: {e}")
        return False


def get_all_tables(db_connection) -> List[str]:
    """
    Retrieve the names of all tables in the database, excluding SQLite internal tables.

    Args:
        db_connection: The database connection object.

    Returns:
        List[str]: A list of table names.
    """
    cursor = db_connection.cursor()
    query = """
    SELECT name 
    FROM sqlite_master 
    WHERE type='table' AND name NOT LIKE 'sqlite_%'
    """
    cursor.execute(query)
    tables = [row[0] for row in cursor.fetchall()]
    return tables


def table_has_required_fields(db_connection, table_name: str, required_fields: List[str]) -> bool:
    """
    Check if a table has all the required fields.

    Args:
        db_connection: The database connection object.
        table_name (str): The name of the table to check.
        required_fields (List[str]): A list of required field names.

    Returns:
        bool: True if the table has all the required fields, False otherwise.
    """
    cursor = db_connection.cursor()
    query = f"PRAGMA table_info({table_name})"
    cursor.execute(query)
    columns = [row[1] for row in cursor.fetchall()]
    return all(field in columns for field in required_fields)


def get_filtered_tables(db_connection, required_fields: List[str]) -> List[str]:
    """
    Get a list of tables that have all the required fields.

    Args:
        db_connection: The database connection object.
        required_fields (List[str]): A list of required field names.

    Returns:
        List[str]: A list of table names that have all the required fields.
    """
    tables = get_all_tables(db_connection)
    filtered_tables = []
    for table in tables:
        if table_has_required_fields(db_connection, table, required_fields):
            filtered_tables.append(table)
    return filtered_tables



def add_to_results(results: Dict[str, List[str]], table_name: str, result: str) -> None:
    """
    Add a result to the results dictionary under the specified table name.

    Args:
        results (Dict[str, List[str]]): The dictionary to add the result to.
        table_name (str): The table name to use as the key in the dictionary.
        result (str): The result to add to the list under the table name.
    """
    results.setdefault(table_name, []).append(result)


def chose_heavy_weight_result(results: Dict[str, List[str]]) -> str | None:
    """
    Choose the heaviest (longest) result from a dictionary of results.

    Args:
        results (Dict[str, List[str]]): A dictionary where keys are table names and values are lists of results.

    Returns:
        str | None: The result with the maximum length, or None if there are no results.

    Raises:
        ValueError: If the results dictionary is empty.
        TypeError: If any of the values in the results dictionary are not lists.
    """
    if not results:
        raise ValueError("The results dictionary is empty.")

    if not all(isinstance(value, list) for value in results.values()):
        raise TypeError("All values in the results dictionary should be lists.")

    result_list = [item for sublist in results.values() for item in sublist]

    if not result_list:
        return None

    heaviest_result = max(result_list, key=len)
    return heaviest_result


def check_existing_record(db_connection, module: str, rhosts: str) -> str | None:
    """
    Check if there is an existing record in any table for the given module and rhosts.

    Args:
        db_connection: The database connection object.
        module (str): The module to search for.
        rhosts (str): The rhosts to search for.

    Returns:
        str | None: The output from the first matching record, or None if no match is found.
    """
    required_fields = ['module', 'rhosts', 'output', 'compressed_output']
    tables = get_filtered_tables(db_connection, required_fields)
    cursor = db_connection.cursor()

    results = {}
    for table_name in tables:
        query = f"""
        SELECT output, compressed_output 
        FROM {table_name}
        WHERE module = ? AND rhosts = ?
        """
        cursor.execute(query, (module, rhosts))
        record = cursor.fetchone()
        if record:
            add_to_results(results, table_name, record)

    return chose_heavy_weight_result(results) if results else None

