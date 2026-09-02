document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("pebbleForm");
    const moodInput = document.getElementById("moodInput");
    const container = document.getElementById("pebblesContainer");

    // Fetch and display existing pebbles on load
    loadPebbles();

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const message = moodInput.value.trim();
        if (!message) return;

        // 1. Create temporary falling animation pebble
        const fallingPebble = document.createElement("div");
        fallingPebble.className = "falling-pebble";
        fallingPebble.textContent = message;
        container.appendChild(fallingPebble);

        // 2. Send data to Flask backend API
        try {
            const response = await fetch("/api/pebbles", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: message })
            });

            if (response.ok) {
                moodInput.value = "";
                // After animation completes, remove temp element and refresh jar contents
                setTimeout(() => {
                    fallingPebble.remove();
                    loadPebbles();
                }, 800);
            }
        } catch (error) {
            console.error("Error saving pebble:", error);
            fallingPebble.remove();
        }
    });

    async function loadPebbles() {
        try {
            const response = await fetch("/api/pebbles");
            if (response.ok) {
                const pebbles = await response.json();
                // Clear existing displayed pebbles except any active animations
                const activeAnimations = container.querySelectorAll(".falling-pebble");
                container.innerHTML = "";
                activeAnimations.forEach(p => container.appendChild(p));

                // Render stored pebbles
                pebbles.forEach(p => {
                    const pebbleEl = document.createElement("div");
                    pebbleEl.className = "stored-pebble";
                    pebbleEl.textContent = p.message;
                    container.appendChild(pebbleEl);
                });
            }
        } catch (error) {
            console.error("Error loading pebbles:", error);
        }
    }
});