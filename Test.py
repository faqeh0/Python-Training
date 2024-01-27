import unittest
from unittest.mock import patch
from io import StringIO

import VendingMachine
from VendingMachine import Machine, Client, Administrator

class TestVendingMachine(unittest.TestCase):

    def setUp(self):
        # Reset the machine inventory before each test
        Machine.inventory = {
            'sprite': {'quantity': 10, 'price_dollars': 3.5},
            'coca-cola': {'quantity': 15, 'price_dollars': 5.0},
            'doritos': {'quantity': 1, 'price_dollars': 2.5},
            'snickers': {'quantity': 12, 'price_dollars': 2.0}
        }

    def test_display_items(self):
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            Machine.display_items()
            result = mock_stdout.getvalue().strip()
        expected_output = """------------------------------------------------------
Available Items:
- Sprite: $3.50
- Coca-Cola: $5.00
- Doritos: $2.50
- Snickers: $2.00
------------------------------------------------------"""
        self.assertEqual(result, expected_output)

    def test_get_item_price(self):
        self.assertEqual(Machine.get_item_price('coca-cola'), 5.0)
        self.assertEqual(Machine.get_item_price('non-existent-item'), 0)

    def test_client_select_currency_invalid_input(self):
        with patch('builtins.input', side_effect=['invalid_currency', 'dollars']):
            client = Client()
            client.select_currency()
        self.assertEqual(client.currency, 'dollars')

    def test_client_select_currency_valid_input(self):
        with patch('builtins.input', side_effect=['shekels']):
            client = Client()
            result = client.select_currency()
        self.assertTrue(result)
        self.assertEqual(client.currency, 'shekels')

    def test_insert_cash_dollars(self):
        client = Client()
        client.currency = 'dollars'
        with patch('builtins.input', side_effect=['5']):
            result = client.insert_cash(False)
        self.assertTrue(result)  # Successful cash insertion
        self.assertEqual(client.balance, 5.0)  # Balance updated correctly

    def test_insert_cash_shekels(self):
        client = Client()
        client.currency = 'shekels'
        with patch('builtins.input', side_effect=['10']):
            result = client.insert_cash(False)
        self.assertTrue(result)  # Successful cash insertion
        self.assertEqual(client.balance, 0.29 * 10)  # Balance updated correctly based on exchange rate

    def test_insert_invalid_cash(self):
        client = Client()
        client.currency = 'dollars'
        with patch('builtins.input', side_effect=['0', '5']):
            result = client.insert_cash(False)
        self.assertTrue(result)  # Successful cash insertion
        self.assertEqual(client.balance, 5.0)  # Balance updated correctly

    def test_select_item_valid_item(self):
        client = Client()
        with patch('builtins.input', side_effect=['sprite']):
            result = client.select_item()
        self.assertTrue(result)  # Valid item selected
        self.assertEqual(client.selected_item, 'sprite')  # Selected item set correctly

    def test_client_select_invalid_item(self):
        client = Client()
        with patch('builtins.input', side_effect=['invalid_item', 'coca-cola']):
            with patch('sys.stdout', new_callable=StringIO):
                result = client.select_item()
        self.assertEqual(result, True)
        self.assertEqual(client.selected_item, 'coca-cola')

    def test_select_item_out_of_stock_then_valid_item(self):
        client = Client()
        Machine.inventory['sprite']['quantity'] = 0

        with patch('builtins.input', side_effect=['sprite', 'cancel']):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                client.select_item()

        expected_output = "-->Invalid item. Please select from the displayed inventory or type 'cancel' to abort."
        self.assertIn(expected_output, mock_stdout.getvalue())

    def test_confirm_purchase_insufficient_funds(self):
        client = Client()
        client.currency = 'dollars'
        client.balance = 2.0  # Assuming the selected item price is $3.5
        client.selected_item = 'sprite'
        with patch('builtins.input', side_effect=['another']):
            result = Machine.confirm_purchase(client.balance, client.selected_item)
        self.assertEqual(result, 'another')
        self.assertEqual(client.balance, 2.0)  # Balance remains the same
        with patch('builtins.input', side_effect=['cash']):
            result = Machine.confirm_purchase(client.balance, client.selected_item)
            self.assertEqual(result, 'cash')
            self.assertEqual(client.balance, 2.0)  # Balance remains the same
        with patch('builtins.input', side_effect=['cancel']):
            result = Machine.confirm_purchase(client.balance, client.selected_item)
            self.assertEqual(result, 'cancel')
            self.assertEqual(client.balance, 2.0)  # Balance remains the same

    def test_confirm_purchase_insufficient_funds2(self):
        Machine.inventory['coca-cola']['quantity'] = 2
        with patch('builtins.input', side_effect=['another', 'cash', '5']):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                result = Machine.confirm_purchase(3, 'coca-cola')
        self.assertEqual(result, 'another')
        self.assertEqual(Machine.inventory['coca-cola']['quantity'], 2)

    def test_confirm_purchase_sufficient_funds(self):
        client = Client()
        client.currency = 'dollars'
        client.balance = 5.0  # Assuming the selected item price is $3.5
        client.selected_item = 'sprite'
        with patch('builtins.input', side_effect=['']):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                result = Machine.confirm_purchase(client.balance, client.selected_item)
                change_output = mock_stdout.getvalue().strip()
        self.assertTrue(result)  # Purchase confirmed
        self.assertIn("Your change is $1.50", change_output)  # Verify change output
        self.assertEqual(Machine.inventory['sprite']['quantity'], 9)  # Verify that item quantity reduced

    def test_confirm_purchase_invalid_choice(self):
        client = Client()
        client.currency = 'dollars'
        client.balance = 2.0
        client.selected_item = 'sprite'
        with patch('builtins.input', side_effect=['invalid', 'another']):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                Machine.confirm_purchase(client.balance, client.selected_item)
                change_output = mock_stdout.getvalue().strip()
        self.assertIn("-->Invalid choice. Please enter 'cash', 'another', or 'cancel'.", change_output)
        self.assertEqual(client.balance, 2.0)  # Balance remains the same

    def test_cancel_request(self):
        client = Client()
        client.balance = 3.0
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            client.cancel_request()
            result = mock_stdout.getvalue().strip()
        expected_output = "-->Transaction canceled. Refunded amount: $3.00"
        self.assertEqual(result, expected_output)
        self.assertEqual(client.balance, 0)  # Balance reset

    def test_administrator_reset_machine(self):
        with patch('builtins.input', side_effect=['admin123']):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                Administrator.reset_machine()
                output = mock_stdout.getvalue().strip()
        expected_inventory = {
            'sprite': {'quantity': 10, 'price_dollars': 3.5},
            'coca-cola': {'quantity': 15, 'price_dollars': 5.0},
            'doritos': {'quantity': 1, 'price_dollars': 2.5},
            'snickers': {'quantity': 12, 'price_dollars': 2.0}
        }
        self.assertEqual(Machine.inventory, expected_inventory)  # Machine inventory reset correctly
        self.assertIn("Administrator resetting the machine.", output)
        self.assertIn("Machine has been reset.", output)

    def test_administrator_refill_stock_existing_item(self):
        with patch('builtins.input', side_effect=['sprite', '5']):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                Administrator.refill_stock()
                output = mock_stdout.getvalue().strip()
        expected_inventory = {
            'sprite': {'quantity': 15, 'price_dollars': 3.5},
            'coca-cola': {'quantity': 15, 'price_dollars': 5.0},
            'doritos': {'quantity': 1, 'price_dollars': 2.5},
            'snickers': {'quantity': 12, 'price_dollars': 2.0}
        }
        self.assertEqual(Machine.inventory, expected_inventory)  # Machine inventory refilled correctly
        self.assertIn("Administrator refilling stock.", output)
        self.assertIn("Stock for Sprite has been refilled (+5 units).", output)

    def test_administrator_refill_stock_new_item(self):
        with patch('builtins.input', side_effect=['new-item', '5', '2.0']):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                Administrator.refill_stock()
                output = mock_stdout.getvalue().strip()
        expected_inventory = {
            'sprite': {'quantity': 10, 'price_dollars': 3.5},
            'coca-cola': {'quantity': 15, 'price_dollars': 5.0},
            'doritos': {'quantity': 1, 'price_dollars': 2.5},
            'snickers': {'quantity': 12, 'price_dollars': 2.0},
            'new-item': {'quantity': 5, 'price_dollars': 2.0}
        }
        self.assertEqual(Machine.inventory, expected_inventory)  # New item added to inventory correctly
        self.assertIn("-->Administrator refilling stock.\n-->New item New-item has been added to the "
                      "inventory with a quantity of 5 and a price of $2.00.",output)

    def test_refill_stock_existing_item_invalid_quantity(self):
        with patch('builtins.input', side_effect=['sprite', 'invalid']):
            Administrator.refill_stock()
        expected_inventory = {
            'sprite': {'quantity': 10, 'price_dollars': 3.5},
            'coca-cola': {'quantity': 15, 'price_dollars': 5.0},
            'doritos': {'quantity': 1, 'price_dollars': 2.5},
            'snickers': {'quantity': 12, 'price_dollars': 2.0}
        }
        self.assertEqual(Machine.inventory, expected_inventory)  # Machine inventory refilled correctly

    def test_refill_stock_new_item_invalid_quantity(self):
        with patch('builtins.input', side_effect=['new_item', 'invalid_quantity', '2.0']):
            with patch('builtins.print') as mock_print:
                Administrator.refill_stock()
                mock_print.assert_called_with("-->Invalid input for quantity or price. Refill canceled.")

    def test_exit_the_main_menu(self):
        client = Client()
        with patch('builtins.input', side_effect=['3']):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                VendingMachine.main()
        self.assertIn("Exiting the program. Goodbye!", mock_stdout.getvalue())

    def test_run_administrator_menu_exit(self):
        with patch('builtins.input', side_effect=['admin123', '3']):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                VendingMachine.run_administrator_menu()
        self.assertIn("Exiting the administrator menu. Returning to the main menu.", mock_stdout.getvalue())

    def test_run_administrator_menu_invalid_choice_then_exit(self):
        with patch('builtins.input', side_effect=['admin123', 'invalid', '3']):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                VendingMachine.run_administrator_menu()
        self.assertIn("Invalid choice. Please enter 1, 2, or 3.", mock_stdout.getvalue())
        self.assertIn("Exiting the administrator menu. Returning to the main menu.", mock_stdout.getvalue())

    def test_run_administrator_menu_refill_stock_invalid_password_then_exit(self):
        with patch('builtins.input', side_effect=['invalid', '2', 'sprite', '5']):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                VendingMachine.run_administrator_menu()
                output = mock_stdout.getvalue().strip()
        self.assertIn("Authentication failed. Returning to the main menu.", output)

    def test_administrator_reset_machine_exception(self):
        with patch('builtins.print') as mock_print:
            with patch('VendingMachine.Machine.inventory', side_effect=Exception("Test Error")):
                Administrator.reset_machine()
                mock_print.assert_called_with("-->Machine has been reset.")

if __name__ == '__main__':
    unittest.main()