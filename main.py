# Import necessary libraries
import sqlite3
import pandas as pd
import time
from nexmo import Client as NexmoClient

# Your Nexmo credentials
nexmo_api_key = 'your api key'
nexmo_api_secret = 'your api secret'
nexmo_phone_number = 'your nexmo register phone number'

# Initialize Nexmo client
nexmo_client = NexmoClient(key=nexmo_api_key, secret=nexmo_api_secret)
# Function to send SMS via Nexmo


def send_sms(recipient_number, message):
    try:
        response = nexmo_client.send_message({
            'from': nexmo_phone_number,
            'to': recipient_number,
            'text': message,
        })

        if response['messages'][0]['status'] == '0':
            print("SMS sent successfully!")
        else:
            print(
                f"Failed to send SMS: {response['messages'][0]['error-text']}")
    except Exception as e:
        print("Error while sending SMS:", e)


# Database Connection setup
connection = sqlite3.connect('menu.db')
cursor = connection.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Menu(
        [product_id] INTEGER PRIMARY KEY AUTOINCREMENT, 
        [product_name] TEXT, 
        [product_price] INTEGER)
    ''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Orders(
        [order_id] INTEGER PRIMARY KEY AUTOINCREMENT, 
        [customer_name] TEXT,
        [customer_phone] TEXT,
        [product_name] TEXT,
        [quantity] INTEGER,
        [total_amount] INTEGER,
        [payment_status] TEXT)
    ''')

cursor.execute('''SELECT * FROM Menu''')
results = cursor.fetchall()
if not results:
    cursor.execute('''
        INSERT INTO Menu (product_name, product_price)
        VALUES
        ('Cake',400),
        ('Bread',50),
        ('Cookies',100),
        ('Doughnuts',80),
        ('Pie',120)
        ''')
    connection.commit()

# Displaying Menu Items


def display_items(cursor):
    query = '''SELECT * FROM Menu'''
    cursor.execute(query)
    results = cursor.fetchall()
    print("List of items: ")
    print("ID", "Name", "Price", sep=" ")
    for each in results:
        print(each[0], each[1], each[2], sep=" ")

# Export orders to Excel sheet


def export_orders_to_excel(cursor):
    query = '''SELECT * FROM Orders'''
    cursor.execute(query)
    results = cursor.fetchall()

    if not results:
        print("No orders found.")
        return

    column_names = ['order_id', 'customer_name', 'customer_phone',
                    'product_name', 'quantity', 'total_amount', 'payment_status']
    existing_orders_df = pd.DataFrame(results, columns=column_names)

    # Export DataFrame to Excel
    existing_orders_df.to_excel('orders.xlsx', index=False)
    print("All orders have been exported to 'orders.xlsx' successfully!")
    time.sleep(1)
    admin_login(connection, cursor)

# Printing Receipt


def print_receipt(customer_name, customer_phone, items, total_amount):
    print()
    print("---------Bakery Management System!--------")
    print("-----------------Receipt----------------")
    print(f"Customer Name: {customer_name}")
    print(f"Customer Phone: {customer_phone}")
    print("Items Purchased:")
    for item in items:
        print(f"{item[0]} - Quantity: {item[1]}")
    print(f"Total Amount: {total_amount}")
    print("Thank you! Have a sweet day!")
    print()


def generate_receipt(customer_name, customer_phone, items, total_amount):
    print("Generating receipt...")
    print_receipt(customer_name, customer_phone, items, total_amount)
    print("Receipt generated!")

# Admin login


def admin_login(connection, cursor):
    print()
    print("----------------------------------------------------------------------------")
    print("---------------------Welcome to Menu Management System!---------------------")
    print("------------------------You are logged in as Admin!-------------------------")
    print("----------------------------------------------------------------------------")
    print()
    print("Here are the list of choices:")
    print("Choice 1: Add an item",
          "Choice 2: Remove an item",
          "Choice 3: Update item price",
          "Choice 4: See all the items",
          "Choice 5: Export to ExcelSheet",
          "Choice 6: Exit",
          sep="\n")

    choice = int(input("Enter your choice: "))
    print()
    time.sleep(0.5)

    if choice == 1:
        print("What would you like to add?")
        product_name = input("Enter product name: ")
        product_price = int(input("Enter product price: "))

        try:
            query = f'''INSERT INTO Menu(product_name, product_price) VALUES ('{product_name}',{product_price})'''
            cursor.execute(query)
            connection.commit()
            print("The item has been added to the list!")
        except Exception as e:
            print("Error occurred while adding item!")
            print(e)

        time.sleep(1)
        admin_login(connection, cursor)

    elif choice == 2:
        display_items(cursor)
        print("Which item would you like to remove?")
        id = int(input("Enter product id: "))
        try:
            query = f'''DELETE FROM Menu WHERE product_id= {id}'''
            cursor.execute(query)
            connection.commit()
            print("The item has been removed from the shop!")
        except Exception as e:
            print("Invalid item!")
        time.sleep(1)
        admin_login(connection, cursor)

    elif choice == 3:
        display_items(cursor)
        print("Which item price would you like to update?")
        id = int(input("Enter product ID: "))
        price = int(input("Enter the updated price: "))
        try:
            query = f'''UPDATE Menu SET product_price={price} WHERE product_id={id}'''
            cursor.execute(query)
            connection.commit()
            print("The item price has been updated!")
        except Exception as e:
            print("Invalid Product ID!")
        time.sleep(1)
        admin_login(connection, cursor)

    elif choice == 4:
        display_items(cursor)
        time.sleep(1.5)
        admin_login(connection, cursor)

    elif choice == 5:
        export_orders_to_excel(cursor)

    elif choice == 6:
        exit()
    else:
        print("Invalid Choice!")
        time.sleep(1)
        admin_login(connection, cursor)

# Customer login


def customer_login(connection, cursor):
    print("-----------Welcome, You are logged in as a Customer!-------------")
    print("Here is the list of choices:")
    print("Choice 1: Place Order", "Choice 2: Exit", sep="\n")
    choice = int(input("Enter your choice: "))
    if choice == 1:
        name = input("Enter the customer name: ")
        phone_number = input("Enter the customer phone number: ")
        print(f"What does {name} want to buy?")
        time.sleep(0.5)
        display_items(cursor)

        total = 0
        items = []
        while True:
            id = int(input("Enter the product ID: "))
            quantity = int(input("Enter the quantity: "))
            try:
                query = f'''SELECT * FROM Menu WHERE product_id={id}'''
                cursor.execute(query)
                result = cursor.fetchone()

                total += result[2] * quantity
                items.append([result[1], quantity])
                i = input("Anything else? Answer Y for Yes and N for No! ")
                if i == 'N':
                    break
            except Exception as e:
                print("Invalid Entry!")
                print(e)
                break

        for item in items:
            product_name = item[0]
            quantity = item[1]
            try:
                query = f'''INSERT INTO Orders (customer_name, customer_phone, product_name, quantity, total_amount, payment_status)
                            VALUES ('{name}', '{phone_number}', '{product_name}', {quantity}, {quantity * total}, 'Pending')'''
                cursor.execute(query)
                connection.commit()
                owner_phone_number = 'Owner phone number'  # Owner's phone number
                owner_message = "New order received! Check it"
                send_sms(owner_phone_number, owner_message)

                customer_phone_number = phone_number  # Assuming phone_number is defined
                customer_message = "Your order was successfully placed. Please wait for further updates."
                send_sms(customer_phone_number, customer_message)
            except Exception as e:
                print("Error occurred while placing order:", e)
                break

        if total != 0:
            print()
            print("--------- Menu Management System--------")
            print("------------Billing Details!------------")
            print(f"Name: {name}")
            for each in items:
                print(each[0], each[1], sep=": ")
            print(f"Total: {total}")
            print("Thank you! Have a sweet day!")
            print()

        export_orders_to_excel(cursor)

        generate_receipt(name, phone_number, items, total)

        time.sleep(1)
        customer_login(connection, cursor)
    elif choice == 2:
        exit()
    else:
        print("Invalid Choice!")
        time.sleep(1)
        customer_login(connection, cursor)

# Main function


def main():
    while True:
        print()
        print(
            "----------------------------------------------------------------------------")
        print(
            "---------------------Welcome to Menu Management System!---------------------")
        print(
            "----------------------------------------------------------------------------")

        print("How would you like to proceed?")
        print("Choice 1: Admin Login", "Choice 2: Customer Login",
              "Choice 3: Exit", sep="\n")

        choice = input("Enter your choice: ")

        if choice == '1':
            password = input("Enter the password: ")
            if password == "**********":
                admin_login(connection, cursor)
            else:
                print("Incorrect Password!")
                time.sleep(1)

        elif choice == '2':
            customer_login(connection, cursor)
        elif choice == '3':
            exit()
        else:
            print("Invalid Choice!")


if __name__ == "__main__":
    main()
