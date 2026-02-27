(function () {
  // state: { id: { id, name, price, qty, maxQty } }
  const selected = {};
  let allSelected = false; 

  function formatCurrency(value) {
    return "EGP " + Number(value).toLocaleString("en-EG", {
      maximumFractionDigits: 2,
    });
  }

  function getSelectedTotal() {
    return Object.values(selected).reduce(
      (sum, item) => sum + item.price * item.qty,
      0
    );
  }

  function renderRightPanel() {
      const container = document.getElementById("selected-items");
      if (!container) return;
    
      const emptyEl = container.querySelector(".js-selected-empty");
    
      // hapus semua row sebelumnya
      container.querySelectorAll(".js-selected-row").forEach((el) => el.remove());
    
      const items = Object.values(selected);
    
      if (!items.length) {
        if (emptyEl) emptyEl.classList.remove("hidden");
      } else if (emptyEl) {
        emptyEl.classList.add("hidden");
      }
  
      items.forEach((item) => {
        // wrapper row
        const row = document.createElement("div");
        row.className =
          "js-selected-row flex items-center justify-between py-1 border-b border-gray-100 cursor-pointer select-none";
        row.dataset.id = item.id; 
    
        // kiri: qty badge + name
        const left = document.createElement("div");
        left.className = "flex items-center gap-2 min-w-0";
    
        const badge = document.createElement("span");
        badge.className =
          "shrink-0 w-5 h-5 rounded-full bg-pink-100 text-pink-600 text-[10px] font-bold flex items-center justify-center";
        badge.textContent = item.qty;
    
        const nameSpan = document.createElement("span");
        nameSpan.className = "truncate text-gray-700 text-xs font-medium";
        nameSpan.textContent = item.name;
    
        left.appendChild(badge);
        left.appendChild(nameSpan);
    
        // kanan: line total
        const right = document.createElement("span");
        right.className = "shrink-0 text-gray-500 text-xs ml-2";
        right.textContent = formatCurrency(item.price * item.qty);
    
        row.appendChild(left);
        row.appendChild(right);
        container.appendChild(row);
      });
  
      // update total
      const totalEl = document.getElementById("selected-total");
      if (totalEl) {
        totalEl.textContent = formatCurrency(getSelectedTotal());
      }
    }


  function handleRowClick(event) {
    const row = event.target.closest(".js-order-item-row");
    if (!row) return;

    const id = row.dataset.id;
    const name = row.dataset.name || row.querySelector(".font-medium")?.textContent || "";
    const price = Number(row.dataset.price || 0);
    const maxQty = Number(row.dataset.qty || 0);
    if (!id || !maxQty) return;

    const current = selected[id]?.qty || 0;
    const next = current + 1 > maxQty ? 0 : current + 1;

    if (!next) {
      delete selected[id];
    } else {
      selected[id] = { id, name, price, qty: next, maxQty };
    }

    // update counter kiri
    const countEl = row.querySelector(".js-selected-count");
    if (countEl) countEl.textContent = next;

    renderRightPanel();
  }

  function handleSelectAllClick() {
    const rows = document.querySelectorAll(".js-order-item-row");

    if (!allSelected) {
      // mode: pilih semua
      rows.forEach((row) => {
        const id = row.dataset.id;
        const name =
          row.dataset.name ||
          row.querySelector(".font-medium")?.textContent ||
          "";
        const price = Number(row.dataset.price || 0);
        const maxQty = Number(row.dataset.qty || 0);
        if (!id || !maxQty) return;

        selected[id] = { id, name, price, qty: maxQty, maxQty };

        const countEl = row.querySelector(".js-selected-count");
        if (countEl) countEl.textContent = maxQty;
      });

      allSelected = true;
    } else {
      // mode: reset semua ke 0
      Object.keys(selected).forEach((id) => delete selected[id]);

      rows.forEach((row) => {
        const countEl = row.querySelector(".js-selected-count");
        if (countEl) countEl.textContent = 0;
      });

      allSelected = false;
    }

    renderRightPanel();
  }


  function handleSelectedRowClick(event) {
    const row = event.target.closest(".js-selected-row");
    if (!row) return;

    const id = row.dataset.id;
    const item = selected[id];
    if (!item) return;

    const nextQty = item.qty - 1;

    if (nextQty <= 0) {
      delete selected[id];
    } else {
      selected[id] = { ...item, qty: nextQty };
    }

    // update counter di kiri
    const leftRow = document.querySelector(`.js-order-item-row[data-id="${id}"]`);
    if (leftRow) {
      const countEl = leftRow.querySelector(".js-selected-count");
      if (countEl) countEl.textContent = nextQty;
    }

    renderRightPanel();
  }

  function init() {
    // delegasi click pada document untuk semua row
    document.addEventListener("click", handleRowClick);

    const selectedItemsContainer = document.getElementById("selected-items");
    if (selectedItemsContainer) {
      selectedItemsContainer.addEventListener("click", handleSelectedRowClick);
    }

    const selectAllBtn = document.querySelector("button[type='button'].whitespace-nowrap");
    // Atau kasih id pada button Select All dan pakai getElementById
    if (selectAllBtn) {
      selectAllBtn.addEventListener("click", handleSelectAllClick);
    }

    renderRightPanel();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  // expose untuk debug kalau perlu
  window.LoadOrder = {
    selected,
    getSelectedTotal,
  };
})();
