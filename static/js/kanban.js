document.addEventListener('DOMContentLoaded', () => {
  const tasks = document.querySelectorAll('.task');
  const columns = document.querySelectorAll('.column');

  tasks.forEach(task => {
    task.setAttribute('draggable', true);

    task.addEventListener('dragstart', (e) => {
      e.dataTransfer.setData('text/plain', task.id);
      setTimeout(() => task.classList.add('invisible'), 0);
    });

    task.addEventListener('dragend', () => {
      task.classList.remove('invisible');
    });
  });

  columns.forEach(col => {
    col.addEventListener('dragover', (e) => {
      e.preventDefault();
    });

    col.addEventListener('drop', (e) => {
      e.preventDefault();
      const taskId = e.dataTransfer.getData('text/plain');
      const task = document.getElementById(taskId);
      if (task) col.appendChild(task);

      // Optional: Send update to Flask via fetch/AJAX to update task status
    });
  });
});
