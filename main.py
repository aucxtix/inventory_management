from auth import login

username = input("Username: ")
password = input("Password: ")

user = login(username, password)

if not user:
    print("Invalid Login")
    exit()

role = user[0]

if role == "Admin":
    print("""
1. Add Product
2. Delete Product
3. Reports
4. Sales
""")

elif role == "Manager":
    print("""
1. Add Product
2. Reports
3. Sales
""")

elif role == "Staff":
    print("""
1. Sales
""")

from products import add_product, view_products, search_product, delete_product

add_product(
    "Mouse",
    "Electronics",
    "Logitech",
    500,
    20
)

while True:

    print("""
1. Add Product
2. View Products
3. Search Product
4. Delete Product
5. Exit
""")

    choice = input("Enter Choice: ")

    if choice == "1":
        name = input("Name: ")
        category = input("Category: ")
        supplier = input("Supplier: ")
        price = float(input("Price: "))
        stock = int(input("Stock: "))

        add_product(
            name,
            category,
            supplier,
            price,
            stock
        )

    elif choice == "2":
        view_products()

    elif choice == "3":
        search = input("Search Product: ")
        search_product(search)

    elif choice == "4":
        pid = int(input("Product ID: "))
        delete_product(pid)

    elif choice == "5":
        break