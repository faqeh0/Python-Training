import logging

class Administrator:
    PASSWORD = "admin123"  # Change this to your desired password

    @staticmethod
    def authenticate():
        password_attempt = input("Enter the administrator password: ")
        return password_attempt == Administrator.PASSWORD

    @staticmethod
    #set inventory to default
    def reset_machine():
        try:
            print("-->Administrator resetting the machine.")
            # Resetting the machine logic remains the same
            Machine.inventory = {
                'sprite': {'quantity': 10, 'price_dollars': 3.5},
                'coca-cola': {'quantity': 15, 'price_dollars': 5.0},
                'doritos': {'quantity': 1, 'price_dollars': 2.5},
                'snickers': {'quantity': 12, 'price_dollars': 2.0}
            }
            print("-->Machine has been reset.")
        except Exception as e:
            logging.error(f"Error in resetting machine: {str(e)}")

    @staticmethod
    def refill_stock():
        try:
            print("-->Administrator refilling stock.")
            # Refilling stock logic remains the same
            item_name = input("Enter the name of the item to refill: ").lower()
            quantity = int(input("Enter the quantity to add: "))
            if item_name in Machine.inventory and Machine.inventory[item_name]['quantity'] > 0:
                Machine.inventory[item_name]['quantity'] += quantity
                print(f"-->Stock for {item_name.capitalize()} has been refilled (+{quantity} units).")
            else:
                price = float(input("Enter the price of the item: "))
                Machine.inventory[item_name] = {'quantity': quantity, 'price_dollars': price}
                print(f"-->New item {item_name.capitalize()} has been added to the inventory "
                      f"with a quantity of {quantity} and a price of ${price:.2f}.")
        except ValueError:
            print("-->Invalid input for quantity or price. Refill canceled.")
        except Exception as e:
            logging.error(f"Error in refilling stock: {str(e)}")

class Machine:
    inventory = {
        'sprite': {'quantity': 10, 'price_dollars': 3.5},
        'coca-cola': {'quantity': 15, 'price_dollars': 5.0},
        'doritos': {'quantity': 1, 'price_dollars': 2.5},
        'snickers': {'quantity': 12, 'price_dollars': 2.0}
    }
    exchange_rate = 0.29  # 1 shekel = 0.29 dollars

    @staticmethod
    def display_items():
        print("------------------------------------------------------")
        print("Available Items:")
        for item, details in Machine.inventory.items():
            if details['quantity'] > 0:  # Check if the item exists or not
                # Modify item name for correct capitalization
                if '-' in item:
                    modified_item = item.replace('-', ' ').title().replace(' ', '-')
                else:
                    modified_item = ' '.join(word.capitalize() for word in item.split())
                print(f"- {modified_item}: ${details['price_dollars']:.2f}")
        print("------------------------------------------------------")

    @staticmethod
    def get_item_price(item_name):
        return Machine.inventory.get(item_name, {}).get('price_dollars', 0)

    @staticmethod
    def confirm_purchase(balance, selected_item):
        item_price = Machine.get_item_price(selected_item)
        if item_price > 0:
            while True:
                if balance >= item_price:
                    Machine.inventory[selected_item.lower()]['quantity'] -= 1  # Access inventory in lowercase
                    change = balance - item_price
                    print(f"-->Purchase confirmed! You bought {selected_item.capitalize()} "
                          f"for ${item_price:.2f}. Your change is ${change:.2f}.")
                    return True
                else:
                    choose = input(f"-->Insufficient funds. Do you want to insert more cash, select another item, "
                                   f"or cancel the transaction? (Type 'cash'/'another'/ 'cancel'): ").replace(" ", "").lower()
                    if choose == "cancel":
                        return "cancel"
                    elif choose == "another":
                        return "another"
                    elif choose == "cash":
                        return "cash"
                    else:
                        print("-->Invalid choice. Please enter 'cash', 'another', or 'cancel'.")
        else:
            return "-->Selected item not available."


class Client:
    def __init__(self):
        self.balance = 0
        self.currency = ""
        self.selected_item = ""

    def select_currency(self):
        self.currency = input("Please choose the currency you will pay in (dollars/shekels), or type exit: ").replace(" ", "").lower()
        while self.currency not in ['dollars', 'shekels']:
            if self.currency == 'exit':
                return False
            self.currency = input("-->Invalid input. Please select currency (dollars/shekels): ").replace(" ", "").lower()
        return True

    def insert_cash(self, flag):
        while True:
            try:
                if self.currency == 'dollars':
                    while True:
                        if not flag:
                            self.balance = float(input("Please insert payment amount in dollars: ").replace(" ", ""))
                            if self.balance == 0:
                                print("-->Inserted amount cannot be zero. Please enter a valid amount.")
                            else:
                                print(f"-->Inserted ${self.balance:.2f} Dollars")
                                return True  # Return True on successful cash insertion
                        elif flag:
                            extra_balance = float(input("Please insert payment amount in dollars: ").replace(" ", ""))
                            self.balance += extra_balance
                            print(f"-->Your balance now is ${self.balance:.2f} Dollars")
                            return True  # Return True on successful cash insertion

                        if not self.balance:
                            raise ValueError("Empty input")
                        else:
                            break  # Break out of the loop if the amount is not zero

                elif self.currency == 'shekels':
                    while True:
                        shekel_amount = float(input("Please insert payment amount in shekels: ").replace(" ", ""))
                        if not shekel_amount:
                            raise ValueError("Empty input")
                        shekel_amount = float(shekel_amount)
                        if shekel_amount == 0:
                            print("-->Inserted amount cannot be zero. Please enter a valid amount.")
                        else:
                            if not flag:
                                self.balance = shekel_amount * Machine.exchange_rate
                                print(f"-->Inserted ${self.balance:.2f} Dollars")
                                return True  # Return True on successful cash insertion
                            elif flag:
                                extra_balance = shekel_amount * Machine.exchange_rate
                                self.balance += extra_balance
                                print(f"-->Your balance now is ${self.balance:.2f} Dollars")
                                return True  # Return True on successful cash insertion
                break

            except ValueError:
                print("-->Invalid input. Please enter a valid amount.")
                continue

    def cancel_request(self):
        print(f"-->Transaction canceled. Refunded amount: ${self.balance:.2f}")
        self.balance = 0  # Reset the balance to provide a refund

    def select_item(self):
        while True:
            selected_item = input("Please select an item from the inventory (type 'cancel' to abort): ").replace(" ", "").lower()
            if selected_item == 'cancel':
                self.cancel_request()
                return False
            elif selected_item in [item.lower() for item in Machine.inventory.keys()] and Machine.inventory[selected_item]['quantity'] > 0:
                self.selected_item = selected_item
                print(f"Selected item: {self.selected_item.capitalize()}")
                return True
            else:
                print("-->Invalid item. Please select from the displayed inventory or type 'cancel' to abort.")

def run_administrator_menu():
    if not Administrator.authenticate():
        print("Authentication failed. Returning to the main menu.")
        return

    while True:
        print("------------------------------------------------------")
        print("\nAdministrator Menu:")
        print("1. Reset Machine")
        print("2. Refill Stock")
        print("3. Exit")
        print("------------------------------------------------------")
        choice = input("Enter your choice (1/2/3): ")
        if choice == '1':
            Administrator.reset_machine()
        elif choice == '2':
            Administrator.refill_stock()
        elif choice == '3':
            print("Exiting the administrator menu. Returning to the main menu.")
            print("------------------------------------------------------")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")


def run_customer():
    client = Client()
    while True:
        Machine().display_items()
        if client.select_currency() is not False:
            client.insert_cash(False)
        else:
            print("------------------------------------------------------")
            break
        while client.select_item():
            result = Machine().confirm_purchase(client.balance, client.selected_item)
            if result == 'cancel':
                client.cancel_request()
                break
            elif result == 'another':
                continue
            elif result == 'cash':
                client.select_currency()
                client.insert_cash(True)
                continue
            break

def main():
    print("                                    ------------------------------------------------------")
    print("                                    -         Welcome to the Vending Machine!            -")
    print("                                    ------------------------------------------------------")
    while True:
        print("1. Customer")
        print("2. Administrator")
        print("3. Exit")
        print("------------------------------------------------------")
        role = input("Choose your role (1/2/3): ")

        if role == '1':
            run_customer()
        elif role == '2':
            run_administrator_menu()
        elif role == '3':
            print("Exiting the program. Goodbye!")
            break
        else:
            print("Invalid role. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()
