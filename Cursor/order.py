def create_order(item_name, quantity):
    return {
        "item": item_name,
        "quantity": quantity,
        "status": "created"
    }