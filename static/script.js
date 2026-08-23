document.addEventListener("DOMContentLoaded", fetchPebbles);

async function fetchPebbles() {
    try {
        const response = await fetch('/api/pebbles');
        const pebbles = await response.json();
        
        const listContainer = document.getElementById('pebblesList');
        listContainer.innerHTML = '';

        if (pebbles.length === 0) {
            listContainer.innerHTML = '<p class="subtitle">The jar is empty. Drop the first pebble!</p>';
            return;
        }

        pebbles.forEach(pebble => {
            const card = document.createElement('div');
            card.className = 'pebble-card';
            card.textContent = pebble.message;
            listContainer.appendChild(card);
        });
    } catch (error) {
        console.error('Error fetching pebbles:', error);
    }
}

async function dropPebble() {
    const inputField = document.getElementById('pebbleInput');
    const errorMsg = document.getElementById('errorMsg');
    const message = inputField.value.trim();

    errorMsg.textContent = '';

    if (!message) {
        errorMsg.textContent = 'Please type something before dropping!';
        return;
    }

    try {
        const response = await fetch('/api/pebbles', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: message })
        });

        const data = await response.json();

        if (response.ok) {
            inputField.value = '';
            fetchPebbles();
        } else {
            errorMsg.textContent = data.error || 'Something went wrong.';
        }
    } catch (error) {
        errorMsg.textContent = 'Network error. Could not connect to server.';
        console.error('Error adding pebble:', error);
    }
}