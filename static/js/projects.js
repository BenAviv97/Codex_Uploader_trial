document.addEventListener('DOMContentLoaded', () => {
    fetch('/api/projects')
        .then((resp) => resp.json())
        .then((folders) => {
            const list = document.getElementById('project-list');
            folders.forEach((f) => {
                const li = document.createElement('li');
                const link = document.createElement('a');
                link.href = '#';
                link.textContent = f.name;
                link.dataset.folderId = f.id;
                link.addEventListener('click', (e) => {
                    e.preventDefault();
                    alert(`Selected project: ${f.name}`);
                });
                li.appendChild(link);
                list.appendChild(li);
            });
        })
        .catch((err) => {
            console.error('Failed to load projects', err);
        });
});
