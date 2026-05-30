
from ..admin.newData_concat import run_once_combined_duckdb
from ..admin.initial_admin_role import create_admin_user_roles_permission

# input admin user roles and permission in database
create_admin_user_roles_permission()

__all__ = [
    # update new data in parquet and .csv file
    "run_once_combined_duckdb"

]

