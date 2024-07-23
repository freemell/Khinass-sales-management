Khinass Drinks & H2O Management System
Description
A web-based application designed to manage sales, inventory, and transaction history for Khinass Drinks & H2O. This project leverages Flask for backend operations and MySQL for database management. The frontend includes additional functionalities implemented using Java Swing.
Features
•	User Authentication: Secure login and session management.
•	Product Management: Add, update, and delete product details.
•	Sales Transactions: Record and manage sales transactions.
•	Transaction History: View detailed transaction history.
•	Product Suggestions: Auto-suggest product names during transactions.
Technologies Used
•	Backend: Python, Flask
•	Database: MySQL (using XAMPP)
•	Frontend: Java Swing
•	Development Tools: XAMPP, MySQL, Git
Installation and Setup
1.	Clone the Repository:
sh
Copy code
git clone https://github.com/your-username/khinass-drinks-management.git
cd khinass-drinks-management
2.	Set Up Virtual Environment:
sh
Copy code
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
3.	Install Dependencies:
sh
Copy code
pip install -r requirements.txt
4.	Configure Database:
o	Start XAMPP and ensure MySQL is running.
o	Create a database named khinass.
o	Import the provided SQL file to set up the necessary tables.
5.	Run the Application:
sh
Copy code
flask run
6.	Access the Application: Open your web browser and go to http://localhost:5000.
Database Configuration
Ensure your MySQL database configuration in the create_connection() function matches your setup:
python
Copy code
def create_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # Use your MySQL username
        password="",  # Use your MySQL password
        database="khinass"
    )
Additional Setup for Java Swing Interface
For the Java Swing frontend, compile and run the Java code using your preferred IDE or command line.
Deployment
To deploy this application on another local machine:
1.	Ensure Python and XAMPP are installed.
2.	Copy the project folder to the target machine.
3.	Set up the virtual environment and install dependencies as described above.
4.	Configure the database and import SQL schema.
5.	Run the Flask application.
Usage
•	Login: Use the login page to authenticate.
•	Sales: Navigate to the sales page to record transactions.
•	Update: Update product details as needed.
•	History: View transaction history.
•	Add: Add new products to the inventory.
________________________________________
Feel free to customize the instructions and details according to your project specifics and requirements.

"# Khinass-sales-management" 
