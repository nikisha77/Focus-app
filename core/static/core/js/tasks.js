// Task CRUD via fetch so the timer JS module is not destroyed by a page reload.
(function () {
  const list = document.getElementById("task-list");
  const form = document.getElementById("task-add-form");
  const input = form.querySelector("input[name='text']");
  const countEl = document.getElementById("task-count");

  function getCsrf() {
    const m = document.cookie.match(/csrftoken=([^;]+)/);
    return m ? m[1] : "";
  }

  function updateCount() {
    if (!countEl) return;
    const tasks = list.querySelectorAll(".task").length;
    countEl.textContent = String(tasks);
  }

  function post(url, body) {
    return fetch(url, {
      method: "POST",
      credentials: "same-origin",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCsrf(),
        "X-Requested-With": "XMLHttpRequest",
      },
      body: JSON.stringify(body || {}),
    });
  }

  function makeTaskNode(task) {
    const li = document.createElement("li");
    li.className = "task" + (task.done ? " done" : "");
    li.dataset.id = String(task.id);
    li.innerHTML =
      '<button class="check" data-action="toggle" aria-label="Toggle done">' +
        (task.done ? "✓" : "○") +
      '</button>' +
      '<span class="task-text"></span>' +
      '<button class="delete" data-action="delete" aria-label="Delete">×</button>';
    li.querySelector(".task-text").textContent = task.text;
    return li;
  }

  function removeEmpty() {
    const empty = document.getElementById("task-empty");
    if (empty) empty.remove();
  }

  function showEmptyIfNeeded() {
    if (!list.querySelector(".task")) {
      const li = document.createElement("li");
      li.className = "empty";
      li.id = "task-empty";
      li.textContent = "No tasks yet. Add one above.";
      list.appendChild(li);
    }
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const text = input.value.trim();
    if (!text) return;
    const res = await post("/tasks/add/", { text });
    if (!res.ok) return;
    const task = await res.json();
    removeEmpty();
    list.prepend(makeTaskNode(task));
    input.value = "";
    updateCount();
  });

  list.addEventListener("click", async (e) => {
    const btn = e.target.closest("button[data-action]");
    if (!btn) return;
    const li = btn.closest(".task");
    if (!li) return;
    const id = li.dataset.id;
    const action = btn.dataset.action;

    if (action === "toggle") {
      const res = await post(`/tasks/${id}/toggle/`);
      if (!res.ok) return;
      const task = await res.json();
      li.classList.toggle("done", task.done);
      btn.textContent = task.done ? "✓" : "○";
    } else if (action === "delete") {
      const res = await post(`/tasks/${id}/delete/`);
      if (!res.ok) return;
      li.remove();
      updateCount();
      showEmptyIfNeeded();
    }
  });

  updateCount();
})();