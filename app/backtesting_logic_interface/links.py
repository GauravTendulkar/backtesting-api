from ..database.mongodb.repositories import equation_collection

def get_all_links() -> list:

    result = list(equation_collection.get_all_links())

    for i in range(0, len(result)):
        result[i] = result[i]["link"]

    return result