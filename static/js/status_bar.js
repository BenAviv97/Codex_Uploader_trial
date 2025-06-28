document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('status-container');

    function statusToPercent(status) {
        switch (status) {
            case 'uploading':
                return 50;
            case 'uploaded':
            case 'done':
                return 100;
            case 'failed':
                return 100;
            default:
                return 0;
        }
    }

    function renderStatus(data) {
        container.innerHTML = '';
        data.forEach(item => {
            const wrapper = document.createElement('div');
            wrapper.className = 'status-item';

            const label = document.createElement('div');
            label.textContent = `Video ${item.id}`;
            wrapper.appendChild(label);

            const bar = document.createElement('div');
            bar.className = 'status-bar';
            if (item.status === 'failed') {
                bar.classList.add('failed');
            }

            const progress = document.createElement('div');
            progress.className = 'progress';
            progress.style.width = statusToPercent(item.status) + '%';
            progress.textContent = item.status;
            bar.appendChild(progress);
            wrapper.appendChild(bar);

            container.appendChild(wrapper);
        });
    }

    function fetchStatus() {
        fetch('/api/status')
            .then(resp => resp.json())
            .then(renderStatus)
            .catch(err => console.error('Failed to load status', err));
    }

    fetchStatus();
    setInterval(fetchStatus, 5000);
});
