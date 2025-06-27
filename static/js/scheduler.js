document.addEventListener('DOMContentLoaded', () => {
    const list = document.getElementById('schedule-list');
    const defaults = window.DEFAULT_TIMES || [];

    defaults.forEach((t, idx) => {
        const label = document.createElement('label');
        label.textContent = `Upload ${idx + 1}`;
        const input = document.createElement('input');
        input.type = 'datetime-local';
        const now = new Date();
        const parts = t.split(':');
        if (parts.length >= 2) {
            now.setHours(parseInt(parts[0], 10), parseInt(parts[1], 10), 0, 0);
        }
        input.value = now.toISOString().slice(0,16);
        label.appendChild(document.createTextNode(': '));
        label.appendChild(input);
        list.appendChild(label);
        list.appendChild(document.createElement('br'));
    });

    document.getElementById('schedule-form').addEventListener('submit', (e) => {
        e.preventDefault();
        const values = Array.from(list.querySelectorAll('input[type="datetime-local"]'))
            .map(inp => inp.value)
            .filter(Boolean);
        fetch('/api/schedule', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ schedule: values })
        })
            .then(resp => {
                if (!resp.ok) throw new Error('Request failed');
                return resp.json();
            })
            .then(() => {
                alert('Schedule saved');
            })
            .catch(err => {
                console.error('Failed to save schedule', err);
                alert('Failed to save schedule');
            });
    });
});
