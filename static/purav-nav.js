(function autoInjectPuravNav() {
  document.addEventListener("DOMContentLoaded", () => {
    const navEl = document.querySelector(".pc-nav");
    if (!navEl) return;
    if (navEl.getAttribute("data-injected") === "true") return;
    const currentPath = window.location.pathname;

    const items = [
      { href: "/purav/carting", label: "Dashboard", icon: "grid", match: ["/purav/carting"] },
      { href: "/purav/carting/trucks", label: "Trucks", icon: "sand", match: ["/purav/carting/trucks"] },
      { href: "/purav/carting/customers", label: "Customers", icon: "users", match: ["/purav/carting/customers"] },
      { href: "/purav/carting/suppliers", label: "Suppliers", icon: "retail", match: ["/purav/carting/suppliers"] },
      { href: "/purav/carting/materials", label: "Materials", icon: "assets", match: ["/purav/carting/materials"] },
      { href: "/purav/carting/staff", label: "Staff", icon: "users", match: ["/purav/carting/staff"] },
      { sep: true },
      { href: "/purav/carting/entry", label: "Sale Entry", icon: "retail", match: ["/purav/carting/entry"] },
      { href: "/purav/carting/challan", label: "Challan", icon: "prompts", match: ["/purav/carting/challan"] },
      { href: "/purav/carting/invoice", label: "Invoice", icon: "gst", match: ["/purav/carting/invoice"] },
      { href: "/purav/carting/payment", label: "Payment", icon: "gst", match: ["/purav/carting/payment"] },
      { href: "/purav/carting/trip", label: "Trip", icon: "sand", match: ["/purav/carting/trip"] },
      { href: "/purav/carting/expenses", label: "Expenses", icon: "download", match: ["/purav/carting/expenses"] },
      { sep: true },
      { href: "/purav/carting/purchase", label: "Purchase", icon: "download", match: ["/purav/carting/purchase"] },
      { href: "/purav/carting/staff-salary", label: "Salary", icon: "gst", match: ["/purav/carting/staff-salary"] },
      { href: "/purav/carting/staff-advance", label: "Advance", icon: "gst", match: ["/purav/carting/staff-advance"] },
      { sep: true },
      { href: "/purav/carting/party-view", label: "Party View", icon: "users", match: ["/purav/carting/party-view"] },
      { href: "/purav/carting/truck-view", label: "Truck View", icon: "sand", match: ["/purav/carting/truck-view"] },
      { href: "/purav/carting/payment-all", label: "Payment All", icon: "gst", match: ["/purav/carting/payment-all"] },
      { href: "/purav/carting/ledger", label: "Ledger", icon: "analytics", match: ["/purav/carting/ledger"] },
      { href: "/purav/carting/reports", label: "Reports", icon: "analytics", match: ["/purav/carting/reports"] },
      { href: "/purav/carting/alerts", label: "Alerts", icon: "bell", match: ["/purav/carting/alerts"] },
      { href: "/purav/carting/settings", label: "Settings", icon: "settings", match: ["/purav/carting/settings"] },
    ];

    let activeHref = ""; let longestMatch = 0;
    items.forEach(it => {
      if (it.sep) return;
      it.match.forEach(m => {
        if (currentPath === m || currentPath.startsWith(m + "/")) {
          if (m.length > longestMatch) { longestMatch = m.length; activeHref = it.href; }
        }
      });
    });

    let html = "";
    items.forEach(it => {
      if (it.sep) {
        html += `<div style="width:1px;height:24px;background:rgba(255,255,255,0.2);margin:0 4px;align-self:center;flex-shrink:0;"></div>`;
        return;
      }
      const isActive = it.href === activeHref;
      html += `<a href="${it.href}" class="${isActive ? 'active' : ''}" style="color:${isActive ? 'white' : 'rgba(255,255,255,0.85)'};text-decoration:none;padding:14px 12px;font-size:12px;font-weight:600;display:inline-flex;align-items:center;gap:5px;border-bottom:3px solid ${isActive ? 'white' : 'transparent'};white-space:nowrap;"><span data-icon="${it.icon}" style="width:14px;height:14px;display:inline-flex;"></span> ${it.label}</a>`;
    });

    navEl.innerHTML = html;
    navEl.style.cssText = "background:linear-gradient(135deg,#1e3a8a 0%,#ea580c 100%);padding:0 20px;display:flex;align-items:center;gap:4px;overflow-x:auto;box-shadow:0 4px 20px rgba(30,58,138,0.3);position:sticky;top:70px;z-index:90;white-space:nowrap;scrollbar-width:thin;";
    navEl.setAttribute("data-injected", "true");
    if (window.renderIcons) window.renderIcons();
  });
})();
