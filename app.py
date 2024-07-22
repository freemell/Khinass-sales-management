from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import mysql.connector
from mysql.connector import Error
import os
import secrets

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', secrets.token_hex(16))  # Use environment variable or generate a new key

def create_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # Use your MySQL username
        password="",  # Use your MySQL password
        database="khinass"
    )

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    username = request.form['username']
    password = request.form['password']
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        session['user_id'] = user.get('id')
        session['username'] = user.get('username')
        return redirect(url_for('index'))
    else:
        flash('Invalid username or password')
        return redirect(url_for('login'))

@app.route('/index')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', current_page='sales')

@app.route('/update_page')
def update_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('update.html', current_page='update')

@app.route('/history')
def history():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('history.html', current_page='history')

@app.route('/add')
def add_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('add.html', current_page='add')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/suggestions', methods=['GET'])
def suggestions():
    query = request.args.get('query', '').lower()
    suggestions = []
    if query:
        product_dao = ProductDAO()
        suggestions = product_dao.get_product_names(query)
    return jsonify(suggestions)

@app.route('/add_item', methods=['POST'])
def add_item():
    product_name = request.form['product_name']
    quantity = int(request.form['quantity'])
    product_dao = ProductDAO()
    product = product_dao.get_product_by_name(product_name)
    if product:
        return jsonify({
            'name': product['name'],
            'price': product['price'],
            'total_price': product['price'] * quantity,
            'remaining_quantity': product['quantity'] - quantity
        })
    else:
        return jsonify({'error': 'Product not found'}), 404

@app.route('/perform_transaction', methods=['POST'])
def perform_transaction():
    customer_name = request.form['customer_name']
    payment_type = request.form['payment_type']
    items = eval(request.form['items']) if isinstance(request.form['items'], str) else request.form['items']

    products = []
    products_to_update = []
    product_dao = ProductDAO()

    for item in items:
        product_name = item['name']
        quantity = int(item['quantity'])
        product = product_dao.get_product_by_name(product_name)

        if product:
            if product['quantity'] >= quantity:
                products.append({
                    'id': product['product_id'],  # Ensure this matches your schema
                    'name': product['name'],
                    'price': product['price'],
                    'quantity': quantity
                })
                products_to_update.append({
                    'id': product['product_id'],  # Ensure this matches your schema
                    'name': product['name'],
                    'price': product['price'],
                    'quantity': product['quantity'] - quantity
                })
            else:
                return jsonify({'error': f'Insufficient quantity for product: {product_name}'}), 400
        else:
            return jsonify({'error': f'Product not found: {product_name}'}), 404

    if products:
        success = product_dao.insert_transaction(customer_name, payment_type, products)
        if success:
            for product in products_to_update:
                product_dao.update_product_quantity(product['id'], product['quantity'])
            return jsonify({'message': 'Transaction Successful'})
        else:
            return jsonify({'error': 'Transaction Failed'}), 500

    return jsonify({'error': 'No products to process'}), 400

@app.route('/update_product', methods=['POST'])
def update_product():
    product_name = request.form['product_name']
    amount_added = request.form.get('amount_added')
    new_price = request.form.get('new_price')

    if not product_name:
        return jsonify({'error': 'Product name is required'}), 400

    try:
        if amount_added:
            amount_added = int(amount_added)
        if new_price:
            new_price = float(new_price)
    except ValueError:
        return jsonify({'error': 'Invalid input data'}), 400

    product_dao = ProductDAO()
    product = product_dao.get_product_by_name(product_name)

    if product:
        new_quantity = product['quantity'] + amount_added if amount_added else product['quantity']
        updated = False
        if new_price is not None and amount_added is not None:
            updated = product_dao.update_product(product['product_id'], new_price, new_quantity)
        elif new_price is not None:
            updated = product_dao.update_product_price(product['product_id'], new_price)
        elif amount_added is not None:
            updated = product_dao.update_product_quantity(product['product_id'], new_quantity)
        
        if updated:
            return jsonify({'message': 'Product updated successfully'})
        else:
            return jsonify({'error': 'Failed to update product'}), 500
    else:
        return jsonify({'error': 'Product not found'}), 404

@app.route('/delete_product', methods=['POST'])
def delete_product():
    product_name = request.form['product_name']
    
    product_dao = ProductDAO()
    product = product_dao.get_product_by_name(product_name)
    
    if product:
        if product_dao.delete_product(product['product_id']):
            return jsonify({'message': 'Product deleted successfully'})
        else:
            return jsonify({'error': 'Failed to delete product'}), 500
    else:
        return jsonify({'error': 'Product not found'}), 404

@app.route('/products', methods=['GET'])
def products():
    product_dao = ProductDAO()
    products = product_dao.get_all_products()
    return jsonify(products)

@app.route('/history_data', methods=['GET'])
def history_data():
    product_dao = ProductDAO()
    history = product_dao.get_transaction_history()
    return jsonify(history)

@app.route('/add_product', methods=['POST'])
def add_product():
    product_name = request.form['product_name']
    quantity = request.form['quantity']
    price = request.form['price']

    if not product_name or not quantity or not price:
        return jsonify({'error': 'All fields are required'}), 400

    try:
        quantity = int(quantity)
        price = float(price)
    except ValueError:
        return jsonify({'error': 'Invalid input data'}), 400

    product_dao = ProductDAO()
    success = product_dao.add_product(product_name, quantity, price)
    
    if success:
        return jsonify({'message': 'Product added successfully'})
    else:
        return jsonify({'error': 'Failed to add product'}), 500

class ProductDAO:
    def get_product_names(self, query):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM products WHERE LOWER(name) LIKE %s", ('%' + query + '%',))
        results = cursor.fetchall()
        conn.close()
        return [result[0] for result in results]

    def get_product_by_name(self, name):
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM products WHERE name = %s", (name,))
        result = cursor.fetchone()
        conn.close()
        return result

    def get_all_products(self):
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM products")
        results = cursor.fetchall()
        conn.close()
        return results

    def update_product_quantity(self, product_id, new_quantity):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE products SET quantity = %s WHERE product_id = %s", (new_quantity, product_id))  # Ensure this matches your schema
        conn.commit()
        conn.close()

    def update_product_price(self, product_id, new_price):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE products SET price = %s WHERE product_id = %s", (new_price, product_id))  # Ensure this matches your schema
        conn.commit()
        conn.close()

    def update_product(self, product_id, new_price, new_quantity):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE products SET price = %s, quantity = %s WHERE product_id = %s", (new_price, new_quantity, product_id))  # Ensure this matches your schema
        conn.commit()
        conn.close()

    def delete_product(self, product_id):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE product_id = %s", (product_id,))  # Ensure this matches your schema
        conn.commit()
        conn.close()

    def insert_transaction(self, customer_name, payment_type, products):
        conn = create_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO transactions (customer_name, payment_type) VALUES (%s, %s)",
                           (customer_name, payment_type))
            transaction_id = cursor.lastrowid
            for product in products:
                cursor.execute("INSERT INTO transaction_items (transaction_id, product_id, quantity, total_price) VALUES (%s, %s, %s, %s)",
                               (transaction_id, product['id'], product['quantity'], product['price'] * product['quantity']))
            conn.commit()
            return True
        except Error as e:
            print(f"Error: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def add_product(self, name, quantity, price):
        conn = create_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO products (name, quantity, price) VALUES (%s, %s, %s)", (name, quantity, price))
            conn.commit()
            return True
        except Error as e:
            print(f"Error: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_transaction_history(self):
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT t.customer_name, t.date, t.payment_type, p.name AS product_name, td.quantity, 
                   (td.quantity * p.price) AS total_amount, 
                   ((td.quantity * p.price) - (td.quantity * p.cost_price)) AS profit
            FROM transactions t
            JOIN transaction_items td ON t.transaction_id = td.transaction_id
            JOIN products p ON td.product_id = p.product_id
            ORDER BY t.date DESC
        """)
        results = cursor.fetchall()
        conn.close()
        return results

if __name__ == '__main__':
    app.run(debug=True)
