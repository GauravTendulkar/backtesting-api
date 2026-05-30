

from ..roles_and_permission import insert_all_admin_permission, create_admin_roles_if_not_exists




def create_admin_user_roles_permission():
    insert_all_admin_permission()
    create_admin_roles_if_not_exists()