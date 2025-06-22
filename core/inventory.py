class Inventory:
    def __init__(self):
        self.items = {}

    def add(self, item_name, quantity=1):
        self.items[item_name] = self.items.get(item_name, 0) + quantity

    def remove(self, item_name, quantity=1):
        if self.has(item_name, quantity):
            self.items[item_name] -= quantity
            if self.items[item_name] <= 0:
                del self.items[item_name]
            return True
        return False

    def has(self, item_name, quantity=1):
        return self.items.get(item_name, 0) >= quantity

    def get_all(self):
        return self.items.copy()

    def __repr__(self):
        return f"Inventory({self.items})"
