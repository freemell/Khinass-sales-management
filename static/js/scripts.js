function navigate(page) {
    window.location.href = `/${page}`;
}

function fetchSuggestions() {
    let query = document.getElementById('productField').value;
    let suggestionsList = document.getElementById('suggestionsList');
    if (query.length > 0) {
        fetch(`/suggestions?query=${query}`)
            .then(response => response.json())
            .then(data => {
                suggestionsList.innerHTML = '';
                data.forEach(item => {
                    let li = document.createElement('li');
                    li.textContent = item;
                    li.onclick = () => {
                        document.getElementById('productField').value = item;
                        suggestionsList.innerHTML = '';
                    };
                    suggestionsList.appendChild(li);
                });
            });
    } else {
        suggestionsList.innerHTML = '';
    }
}

function addItem() {
    let productName = document.getElementById('productField').value;
    let quantity = document.getElementById('quantityField').value;

    fetch('/add_item', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: `product_name=${productName}&quantity=${quantity}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            let table = document.getElementById('itemsTable').getElementsByTagName('tbody')[0];
            let newRow = table.insertRow();
            newRow.insertCell(0).textContent = data.name;
            newRow.insertCell(1).textContent = quantity;
            newRow.insertCell(2).textContent = data.price;
            newRow.insertCell(3).textContent = data.total_price;
            newRow.insertCell(4).textContent = data.remaining_quantity;

            updateTotalAmount();
        }
    });
}

function updateTotalAmount() {
    let table = document.getElementById('itemsTable').getElementsByTagName('tbody')[0];
    let totalAmount = 0;
    for (let row of table.rows) {
        totalAmount += parseFloat(row.cells[3].textContent);
    }
    document.getElementById('totalAmount').textContent = `Total: ${totalAmount}`;
}

function performTransaction() {
    let customerName = document.getElementById('customerField').value;
    let paymentType = document.getElementById('paymentType').value;
    let table = document.getElementById('itemsTable').getElementsByTagName('tbody')[0];
    let items = [];
    for (let row of table.rows) {
        items.push({
            name: row.cells[0].textContent,
            quantity: row.cells[1].textContent
        });
    }

    fetch('/perform_transaction', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: `customer_name=${customerName}&payment_type=${paymentType}&items=${JSON.stringify(items)}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            alert(data.message);
            document.getElementById('itemsTable').getElementsByTagName('tbody')[0].innerHTML = '';
            updateTotalAmount();
        }
    });
}

function updateProduct() {
    let productName = document.getElementById('productField').value;
    let amountAdded = document.getElementById('amountAddedField').value;
    let newPrice = document.getElementById('priceField').value;

    if (!productName) {
        alert("Product name is required");
        return;
    }

    let body = `product_name=${productName}`;
    if (amountAdded) {
        body += `&amount_added=${amountAdded}`;
    }
    if (newPrice) {
        body += `&new_price=${newPrice}`;
    }

    fetch('/update_product', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: body
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            alert(data.message);
            loadProducts(); // Reload products table after update
        }
    });
}

function deleteProduct() {
    let productName = document.getElementById('productField').value;

    fetch('/delete_product', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: `product_name=${productName}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            alert(data.message);
            loadProducts(); // Reload products table after deletion
        }
    });
}

function loadProducts() {
    fetch('/products')
    .then(response => response.json())
    .then(data => {
        let table = document.getElementById('productsTable').getElementsByTagName('tbody')[0];
        table.innerHTML = ''; // Clear existing rows
        data.forEach(product => {
            let newRow = table.insertRow();
            newRow.insertCell(0).textContent = product.name;
            newRow.insertCell(1).textContent = product.amount_added || 0;
            newRow.insertCell(2).textContent = product.price;
            newRow.insertCell(3).textContent = product.quantity;
        });
    });
}

function loadHistory() {
    fetch('/history_data')
    .then(response => response.json())
    .then(data => {
        let table = document.getElementById('historyTable').getElementsByTagName('tbody')[0];
        table.innerHTML = ''; // Clear existing rows
        data.forEach(record => {
            let newRow = table.insertRow();
            newRow.insertCell(0).textContent = record.customer_name;
            newRow.insertCell(1).textContent = new Date(record.date).toLocaleString();
            newRow.insertCell(2).textContent = record.payment_type;
            newRow.insertCell(3).textContent = record.product_name;
            newRow.insertCell(4).textContent = record.quantity;
            newRow.insertCell(5).textContent = record.total_amount;
            newRow.insertCell(6).textContent = record.profit;
        });
    });
}

// Load products when the page loads
document.addEventListener('DOMContentLoaded', loadProducts);
document.addEventListener('DOMContentLoaded', loadHistory);
function addProduct() {
    let productName = document.getElementById('productField').value;
    let quantity = document.getElementById('quantityField').value;
    let price = document.getElementById('priceField').value;

    if (!productName || !quantity || !price) {
        alert('All fields are required');
        return;
    }

    fetch('/add_product', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: `product_name=${productName}&quantity=${quantity}&price=${price}`
    })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
            } else {
                alert(data.message);
                document.getElementById('productField').value = '';
                document.getElementById('quantityField').value = '';
                document.getElementById('priceField').value = '';
            }
        });
}
