document.addEventListener('DOMContentLoaded', function() {
    const taskList = document.getElementById('task-list');

    taskList.addEventListener('click', function(e) {
        const li = e.target.closest('li');
        const taskId = li ? li.dataset.taskId : null;
        if (!taskId) return;

        if (e.target.classList.contains('delete-btn')) {
            if (confirm('Are you sure you want to delete this task?')) {
                window.location.href = urls.delete.replace("0", taskId);
            }
        }

        if (e.target.classList.contains('complete-btn')) {
            window.location.href = urls.complete.replace("0", taskId);
        }

        if (e.target.classList.contains('edit-btn')) {
            const newTitle = prompt('Edit task title:', li.querySelector('div').textContent.trim());
             if (newTitle) {
                const editUrl = urls.edit.replace("PLACEHOLDER", li.dataset.taskUuid);
                window.location.href = editUrl + "?title=" + encodeURIComponent(newTitle);
            }
        }
    });
});
