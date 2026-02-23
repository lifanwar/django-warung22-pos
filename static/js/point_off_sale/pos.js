// POS cart: state sederhana + template cloning + event delegation + category filter.
(function () {
  const cart = {}; // {id: {id, name, price, qty}}

  function $(id) {
    return document.getElementById(id);
  }

  const els = {
    orderItems: () => $("order-items"),
    orderEmpty: () => $("order-empty"),
    orderTotal: () => $("order-total"),
    subtotal: () => $("subtotal"),
    template: () => $("order-item-template"),
  };

  function formatRupiah(value) {
    return "Rp " + Number(value).toLocaleString("id-ID", {
      maximumFractionDigits: 0,
    });
  }

  // ========== CART STATE ==========

  function addItem(id, name, price) {
    const key = String(id);
    if (!cart[key]) {
      cart[key] = { id: key, name, price: Number(price), qty: 0 };
    }
    cart[key].qty += 1;
    render();
  }

  function removeItem(id) {
    const key = String(id);
    if (!cart[key]) return;
    cart[key].qty -= 1;
    if (cart[key].qty <= 0) {
      delete cart[key];
    }
    render();
  }

  function getCartCount() {
    return Object.values(cart).reduce((sum, item) => sum + item.qty, 0);
  }

  function getSubtotal() {
    return Object.values(cart).reduce(
      (sum, item) => sum + item.price * item.qty,
      0
    );
  }

  function clearOrderList(container, keepNode) {
    Array.from(container.children).forEach((child) => {
      if (keepNode && child === keepNode) return;
      container.removeChild(child);
    });
  }

  // ========== RENDER CURRENT ORDER ==========

  function render() {
  const container = els.orderItems();
  const emptyEl = els.orderEmpty();
  const totalEl = els.orderTotal();
  const subtotalNode = els.subtotal();
  const template = els.template();

  if (!container || !subtotalNode || !totalEl || !template) return;

  const items = Object.values(cart);

  clearOrderList(container, emptyEl || null);

  if (items.length === 0) {
    if (emptyEl) {
      emptyEl.classList.remove("hidden");
      emptyEl.classList.add("block");
      container.appendChild(emptyEl);
    }
    totalEl.classList.add("hidden");
  } else {
    if (emptyEl) {
      emptyEl.classList.add("hidden");
    }

    items.forEach((item) => {
      const frag = template.content.cloneNode(true);

      const nameNode = frag.querySelector(".order-item-name");
      const metaNode = frag.querySelector(".order-item-meta");
      const totalNode = frag.querySelector(".order-item-total");
      const minusBtn = frag.querySelector(".order-item-minus");

      if (nameNode) nameNode.textContent = item.name;
      if (metaNode)
        metaNode.textContent = `x${item.qty} · ${formatRupiah(item.price)}`;
      if (totalNode)
        totalNode.textContent = formatRupiah(item.price * item.qty);
      if (minusBtn) {
        minusBtn.dataset.id = item.id;
      }

      container.appendChild(frag);
    });

    totalEl.classList.remove("hidden");
  }

  // hitung subtotal SELALU di akhir
  const subtotalRaw = getSubtotal();
  subtotalNode.textContent = formatRupiah(subtotalRaw);

  // sync badge Alpine
  const totalItems = getCartCount();
  window.dispatchEvent(
    new CustomEvent("cart-updated", { detail: totalItems })
  );

  // kirim subtotal mentah ke Alpine
  window.dispatchEvent(
    new CustomEvent("cart-subtotal-updated", { detail: subtotalRaw })
  );
}


  // ========== CATEGORY FILTER (CLIENT-SIDE) ==========

  function setActiveCategory(categoryKey) {
    const tabs = document.querySelectorAll(".js-category-tab");
    const items = document.querySelectorAll("#menu-grid .js-menu-add");
    const title = document.getElementById("menu-title");

    tabs.forEach((tab) => {
      const tabCat = tab.dataset.category;
      const isActive = tabCat === categoryKey;

      tab.classList.toggle("bg-pink-200", isActive);
      tab.classList.toggle("border-pink-300", isActive);
      tab.classList.toggle("text-pink-700", isActive);

      tab.classList.toggle("bg-white", !isActive);
      tab.classList.toggle("border-gray-200", !isActive);
      tab.classList.toggle("text-gray-700", !isActive);
    });

    items.forEach((btn) => {
      const itemCat = btn.dataset.category || "";
      const show = categoryKey === "all" ? true : itemCat === categoryKey;
      btn.style.display = show ? "" : "none";
    });

    if (title) {
      title.textContent =
        categoryKey === "all"
          ? "All Items"
          : categoryKey.replace(/-/g, " ") + " Items";
    }
  }

  // ========== EVENT HANDLERS ==========

  function handleMenuClick(event) {
    // add to cart
    const btn = event.target.closest(".js-menu-add");
    if (btn) {
      const id = btn.dataset.id;
      const name = btn.dataset.name;
      const price = btn.dataset.price;

      if (!id || !name || !price) return;
      addItem(id, name, price);
      return;
    }

    // category filter
    const tab = event.target.closest(".js-category-tab");
    if (tab) {
      const cat = tab.dataset.category || "all";
      setActiveCategory(cat);
    }
  }

  function handleOrderClick(event) {
    const minusBtn = event.target.closest(".order-item-minus");
    if (!minusBtn) return;

    const id = minusBtn.dataset.id;
    if (!id) return;

    removeItem(id);
  }

  // ========== INIT ==========

  function init() {
    const menuContainer = document;
    const orderContainer = els.orderItems();

    if (menuContainer) {
      menuContainer.addEventListener("click", handleMenuClick);
    }

    if (orderContainer) {
      orderContainer.addEventListener("click", handleOrderClick);
    }

    // kategori default
    setActiveCategory("all");
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  // expose kalau suatu saat perlu
  window.POS = {
    addItem,
    removeItem,
    getCartCount,
    getSubtotal,
  };
})();
