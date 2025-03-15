let orders = [];

async function loadOrders(tableNumber = "", status = "") {
    const queryParams = new URLSearchParams();

    if (tableNumber !== "") {
        queryParams.append("table_number", tableNumber);
    }
    if (status !== "") {
        queryParams.append("status", status);
    }

    const response = await fetch(`http://localhost:8001/orders/search?${queryParams.toString()}`);

    orders = await response.json();
    renderOrders(orders);
}

function renderOrders(filteredOrders) {
    const ordersList = document.getElementById("orders-list");
    ordersList.innerHTML = "";
    filteredOrders.forEach(order => {
        const orderCard = document.createElement("div");
        orderCard.classList.add("order-card");

        orderCard.innerHTML = `
            <h3>Заказ ID: ${order.id}</h3>
            <p>Стол: ${order.table_number}, Статус: <span class="status">${order.status}</span></p>
            <div class="order-details">
                <strong>Блюда:</strong>
                <ul>
                    ${Object.entries(order.items).map(([dish, price]) => `
                        <li>${dish}: <span class="dish-price">${price}₽</span></li>
                    `).join('')}
                </ul>
                <p class="total-price">Общая стоимость: ${order.total_price}₽</p>
            </div>
        `;

        orderCard.addEventListener("click", () => openModal(order));
        ordersList.appendChild(orderCard);
    });
}


// Функция для поиска через Elasticsearch
function searchOrders() {
    const searchQuery = document.getElementById("search-query").value.trim();

    let tableNumber = "";
    let status = "";

    if (!isNaN(searchQuery) && searchQuery !== "") {
        tableNumber = searchQuery;
    } else if (searchQuery !== "") {
        status = searchQuery;
    }

    // Если пустой запрос, загружаем всё
    if (searchQuery === "") {
        loadOrders(); // вызов без параметров
    } else {
        loadOrders(tableNumber, status);
    }
}

async function addItem() {
    const dishName = document.getElementById("dish_name").value;
    const price = parseFloat(document.getElementById("dish_price").value);
    if (dishName && price) {
        orderItems.push({ dish: dishName, price: price });
        updateOrderItemsList();
    }
    document.getElementById("dish_name").value = '';
    document.getElementById("dish_price").value = '';
}

function updateOrderItemsList() {
    const orderItemsList = document.getElementById("order-items-list");
    orderItemsList.innerHTML = "";
    orderItems.forEach((item, index) => {
        const li = document.createElement("li");
        li.classList.add("order-item");
        li.innerHTML = `${item.dish}: <b>${item.price}₽</b>
            <button onclick="removeItem(${index})">Удалить</button>`;
        orderItemsList.appendChild(li);
    });
}

function removeItem(index) {
    orderItems.splice(index, 1);
    updateOrderItemsList();
}

async function addOrder() {
    const tableNumber = document.getElementById("table_number").value;
    if (!orderItems.length || !tableNumber) {
        alert("Заполните все поля!");
        return;
    }

    const orderData = {
        table_number: tableNumber,
        items: orderItems.reduce((acc, item) => {
            acc[item.dish] = item.price;
            return acc;
        }, {}),
        total_price: orderItems.reduce((acc, item) => acc + item.price, 0)
    };

    const response = await fetch("http://localhost:8001/orders", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(orderData)
    });
    if (response.ok) {
        alert("Заказ добавлен!");
        orderItems = [];  // Сбросить список блюд после добавления
        updateOrderItemsList();
        loadOrders(); // Перезагрузим список заказов
    }
}

window.onload = loadOrders;
let currentEditingOrder = null;

// Открываем модалку при клике на карточку
function openModal(order) {
    currentEditingOrder = JSON.parse(JSON.stringify(order)); // Копия данных для редактирования

    document.getElementById("modal").style.display = "flex";

    document.getElementById("modal-order-id").value = order.id;
    document.getElementById("modal-status").value = order.status;

    updateModalDishesList();
}

function closeModal() {
    document.getElementById("modal").style.display = "none";
}

// Добавление нового блюда в модалке
function addDishToModal() {
    const dishName = document.getElementById("modal-dish-name").value;
    const dishPrice = parseFloat(document.getElementById("modal-dish-price").value);

    if (dishName && dishPrice) {
        currentEditingOrder.items[dishName] = dishPrice;  // Добавляем новое блюдо
        updateModalDishesList();  // Обновляем отображаемый список блюд

        document.getElementById("modal-dish-name").value = "";  // Очищаем поля ввода
        document.getElementById("modal-dish-price").value = "";
    }
}

// Обновляем список блюд в модалке
function updateModalDishesList() {
    const dishesList = document.getElementById("modal-dishes-list");
    dishesList.innerHTML = "";

    for (const [dish, price] of Object.entries(currentEditingOrder.items)) {
        const li = document.createElement("li");
        li.textContent = `${dish}: ${price}₽`;

        const deleteBtn = document.createElement("button");
        deleteBtn.textContent = "Удалить";
        deleteBtn.style.marginLeft = "10px";
        deleteBtn.onclick = () => {
            delete currentEditingOrder.items[dish];
            updateModalDishesList();
        };

        li.appendChild(deleteBtn);
        dishesList.appendChild(li);
    }
}

// Сохранить изменения заказа
async function saveChanges() {
    const updatedStatus = document.getElementById("modal-status").value;

    // Пересчитываем total_price, включая старые и новые блюда
    const updatedItems = { ...currentEditingOrder.items }; // Делаем копию старых блюд
    const totalPrice = Object.values(updatedItems).reduce((sum, price) => sum + price, 0);

    const updatedOrder = {
        status: updatedStatus,
        new_items: updatedItems,
    };

    const response = await fetch(`http://localhost:8001/orders/${currentEditingOrder.id}`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(updatedOrder)
    });

    if (response.ok) {
        alert("Заказ обновлен!");
        closeModal();
        loadOrders(); // Перезагружаем список заказов
    } else {
        alert("Ошибка при обновлении заказа.");
    }
}

// Удаление заказа
async function deleteOrder() {
    const confirmDelete = confirm("Вы уверены, что хотите удалить заказ?");
    if (!confirmDelete) return;

    const response = await fetch(`http://localhost:8001/orders/${currentEditingOrder.id}`, {
        method: "DELETE"
    });

    if (response.ok) {
        alert("Заказ удален!");
        closeModal();
        loadOrders();
    } else {
        alert("Ошибка при удалении заказа.");
    }
}


document.addEventListener("keydown", function(event) {
    if (event.key === "Escape") {
        closeModal();
    }
});