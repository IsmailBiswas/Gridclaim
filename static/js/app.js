(() => {
  const app = document.getElementById("app");
  const grid = document.getElementById("grid");
  if (!app || !grid) return;

  const playerId = app.dataset.playerId || "";
  const cooldownSeconds = Number(app.dataset.cooldownSeconds || "2.5");

  let cooling = false;
  let endsAt = 0;
  let tickTimer = 0;
  let activeCell = null;

  function csrfToken() {
    const match = document.cookie.match(/(?:^|; )csrftoken=([^;]*)/);
    return match ? decodeURIComponent(match[1]) : "";
  }

  document.body.addEventListener("htmx:configRequest", (event) => {
    const token = csrfToken();
    if (token) event.detail.headers["X-CSRFToken"] = token;
  });

  function left() {
    return Math.max(0, (endsAt - Date.now()) / 1000);
  }

  function clearTimerUI() {
    document.querySelectorAll(".cell.show-cooldown-timer").forEach((cell) => {
      cell.classList.remove("show-cooldown-timer");
      const el = cell.querySelector(".cell-timer");
      if (el) el.textContent = "";
    });
    activeCell = null;
  }

  function paintTimer() {
    if (!activeCell || !document.body.contains(activeCell)) return;
    let el = activeCell.querySelector(".cell-timer");
    if (!el) {
      el = document.createElement("span");
      el.className = "cell-timer";
      activeCell.appendChild(el);
    }
    activeCell.classList.add("show-cooldown-timer");
    el.textContent = left().toFixed(1);
  }

  function shake(cell) {
    cell.classList.remove("is-shaking");
    void cell.offsetWidth;
    cell.classList.add("is-shaking");
    window.setTimeout(() => cell.classList.remove("is-shaking"), 230);
  }

  function stopCooldown() {
    cooling = false;
    endsAt = 0;
    app.classList.remove("is-cooling");
    if (tickTimer) {
      clearInterval(tickTimer);
      tickTimer = 0;
    }
    clearTimerUI();
  }

  function startCooldown(seconds) {
    const duration = Number(seconds);
    if (!(duration > 0)) return;
    cooling = true;
    endsAt = Date.now() + duration * 1000;
    app.classList.add("is-cooling");
    if (tickTimer) clearInterval(tickTimer);
    tickTimer = window.setInterval(() => {
      if (left() <= 0) {
        stopCooldown();
        return;
      }
      paintTimer();
    }, 50);
  }

  function onCooldownClick(cell) {
    activeCell = cell;
    paintTimer();
    shake(cell);
  }

  // During cooldown: click still works for feedback, but claim is blocked.
  grid.addEventListener(
    "click",
    (event) => {
      if (!cooling) return;
      const cell = event.target.closest(".cell");
      if (!cell || !grid.contains(cell)) return;
      event.preventDefault();
      event.stopImmediatePropagation();
      onCooldownClick(cell);
    },
    true
  );

  document.body.addEventListener("htmx:beforeRequest", (event) => {
    const el = event.detail.elt;
    if (!(el instanceof HTMLElement) || !el.classList.contains("cell")) return;
    if (!cooling) return;
    event.preventDefault();
    onCooldownClick(el);
  });

  // Always start cooldown after a successful claim response.
  document.body.addEventListener("htmx:afterRequest", (event) => {
    const el = event.detail.elt;
    if (!(el instanceof HTMLElement) || !el.classList.contains("cell")) return;
    const xhr = event.detail.xhr;
    if (!xhr) return;

    if (xhr.status === 200) {
      clearTimerUI();
      startCooldown(cooldownSeconds);
      if (window.posthog) {
        window.posthog.capture("cell_claimed", {
          cell_id: el.dataset.cellId,
          x: el.dataset.x,
          y: el.dataset.y,
        });
      }
      return;
    }

    if (xhr.status === 429) {
      const remaining = Number(xhr.getResponseHeader("X-Cooldown-Remaining") || cooldownSeconds);
      startCooldown(remaining > 0 ? remaining : cooldownSeconds);
      onCooldownClick(el);
      if (window.posthog) {
        window.posthog.capture("claim_cooldown_blocked", {
          cell_id: el.dataset.cellId,
        });
      }
    }
  });

  function markOwnership() {
    document.querySelectorAll(".cell[data-owner-id]").forEach((cell) => {
      const ownerId = cell.getAttribute("data-owner-id") || "";
      cell.classList.toggle("is-mine", Boolean(ownerId) && ownerId === playerId);
    });
  }

  markOwnership();
  document.body.addEventListener("htmx:afterSwap", markOwnership);
  document.body.addEventListener("htmx:wsAfterMessage", markOwnership);

  const initial = Number(app.dataset.cooldownRemaining || "0");
  if (initial > 0) startCooldown(initial);
})();
