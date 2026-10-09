/* ============================================
   PURAV CARTING — Common Navigation
   Auto-injects nav into any page with class "pc-nav"
   ============================================ */

const PURAV_NAV_ITEMS = [
  { href: "/purav/carting", label: "Dashboard", icon: "grid", key: "dashboard" },
  { href: "/purav/carting/trucks", label: "Trucks", icon: "sand", key: "trucks" },
  { href: "/purav/carting/customers", label: "Customers", icon: "users", key: "customers" },
  { href: "/purav/carting/suppliers", label: "Suppliers", icon: "retail", key: "suppliers" },
  { href: "/purav/carting/materials", label: "Materials", icon: "assets", key: "materials" },
  { href: "/purav/carting/staff", label: "Staff", icon: "users", key: "staff" },
  { href: "/purav/carting/entry", label: "Sale Entry", icon: "retail", key: "entry" },
  { href: "/purav/carting/challan", label: "Challan", icon: "retail", key: "challan" },
  { href: "/purav/carting/purchase", label: "Purchase", icon: "download", key: "purchase" },
  { href: "/purav/carting/invoice", label: "Invoice", icon: "gst", key: "invoice" },
  { href: "/purav/carting/payment", label: "Payment", icon: "gst", key: "payment" },
  { href: "/purav/carting/trip", label: "Trip", icon: "sand", key: "trip" },
  { href: "/purav/carting/staff-salary", label: "Salary", icon: "gst", key: "staff-salary" },
  { href: "/purav/carting/staff-advance", label: "Advance", icon: "gst", key: "staff-advance" },
  { href: "/purav/carting/ledger", label: "Ledger", icon: "analytics", key: "ledger" },
  { href: "/purav/carting/reports", label: "Reports", icon: "analytics", key: "reports" },
  { href: "/purav/carting/alerts", label: "Alerts", icon: "bell", key: "alerts" },
  { href: "/purav/carting/settings", label: "Settings", icon: "settings", key: "settings" },
];

function renderPuravNav() {
  const navEl = document.querySelector(".pc-nav[data-purav-nav]");
  if (!navEl) return;
  const active = navEl.getAttribute("data-active") || "";
  let html = "";
  PURAV_NAV_ITEMS.forEach((item, i) => {
    // Add separator every 6 items
    if (i === 6 || i === 12) {
      html += `<div style="width:1px;height:24px;background:rgba(255,255,255,0.2);margin:0 6px;align-self:center;"></div>`;
    }
    const cls = item.key === active ? "active" : "";
    html += `<a href="${item.href}" class="${cls}"><span data-icon="${item.icon}"></span> ${item.label}</a>`;
  });
  navEl.innerHTML = html;
  if (window.renderIcons) window.renderIcons();
}

document.addEventListener("DOMContentLoaded", renderPuravNav);
