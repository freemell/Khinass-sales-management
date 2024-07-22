import sqlite3

def get_product_names(query):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM products WHERE name LIKE ?", ('%' + query + '%',))
    results = cursor.fetchall()
    conn.close()
    return [result[0] for result in results]

def get_product_by_name(name):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE name = ?", (name,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return {
            'id': result[0],
            'name': result[1],
            'price': result[2],
            'quantity': result[3]
        }
    return None

def insert_transaction(customer_name, payment_type, items):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO transactions (customer_name, payment_type) VALUES (?, ?)",
                       (customer_name, payment_type))
        transaction_id = cursor.lastrowid
        for item in items:
            cursor.execute("INSERT INTO transaction_items (transaction_id, product_id, quantity) VALUES (?, ?, ?)",
                           (transaction_id, item['id'], item['quantity']))
        conn.commit()
        return True
    except:
        conn.rollback()
        return False
    finally:
        conn.close()

def update_product_quantity(product_id, quantity):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET quantity = ? WHERE id = ?", (quantity, product_id))
    conn.commit()
    conn.close()
