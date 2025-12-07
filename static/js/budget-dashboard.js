// Read JSON data injected by the template
const raw = document.getElementById("dashboard-data")?.textContent || "{}";
let parsed = {};
try {
  parsed = JSON.parse(raw);
} catch (e) {
  console.error("Failed to parse dashboard data JSON:", e);
}

const allData = parsed.allData || {};
const categoriesIds = parsed.categoriesIds || {};

// Couleurs des catégories
const categoriesRef = [
  { nom: "Alimentation", color: "#10b981" },
  { nom: "Transport", color: "#3b82f6" },
  { nom: "Loisirs", color: "#f59e0b" },
  { nom: "Logement", color: "#8b5cf6" },
  { nom: "Santé", color: "#ec4899" },
  { nom: "Vêtements", color: "#14b8a6" },
  { nom: "Éducation", color: "#f97316" },
  { nom: "Épargne", color: "#06b6d4" },
  { nom: "Autres", color: "#64748b" },
  { nom: "Autre", color: "#64748b" },
];

let lineChart = null;
let barChart = null;
let currentPeriod = "month";

function changePeriod(period, btn) {
  currentPeriod = period;

  document
    .querySelectorAll(".period-btn")
    .forEach((b) => b.classList.remove("active"));
  if (btn) btn.classList.add("active");

  const data = allData[period];
  if (!data) return;

  // Mettre à jour les stats
  const depElem = document.getElementById("stat-depenses");
  const revElem = document.getElementById("stat-revenus");
  const soldeElem = document.getElementById("stat-solde");
  const soldeLabelElem = document.getElementById("stat-solde-label");

  if (depElem) depElem.textContent = Number(data.depenses).toFixed(2) + "€";
  if (revElem) revElem.textContent = Number(data.revenus).toFixed(2) + "€";
  if (soldeElem) soldeElem.textContent = Number(data.solde).toFixed(2) + "€";

  if (soldeElem) {
    soldeElem.classList.remove("positive", "negative");
    soldeElem.classList.add(data.solde >= 0 ? "positive" : "negative");
  }

  if (soldeLabelElem) {
    soldeLabelElem.innerHTML =
      "<span>" + (data.solde >= 0 ? "Excédent" : "Déficit") + "</span>";
    soldeLabelElem.className =
      "stat-change " + (data.solde >= 0 ? "up" : "down");
  }

  // Mettre à jour les labels de période
  const periodeLabel = document.getElementById("periode-label");
  const periodeLabel2 = document.getElementById("periode-label-2");
  const evolutionTitle = document.getElementById("evolution-title");

  if (periodeLabel) periodeLabel.textContent = data.label;
  if (periodeLabel2) periodeLabel2.textContent = data.label;
  if (evolutionTitle) evolutionTitle.textContent = data.evolutionTitle;

  updateLineChart(data);
  updateBarChart(data);
}

function updateLineChart(data) {
  if (!data) return;
  if (lineChart) lineChart.destroy();

  const ctx = document.getElementById("lineChart")?.getContext("2d");
  if (!ctx) return;

  lineChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: data.evolutionLabels || [],
      datasets: [
        {
          label: "Dépenses",
          data: data.evolutionDep || [],
          borderColor: "#ef4444",
          backgroundColor: "rgba(239, 68, 68, 0.1)",
          borderWidth: 3,
          tension: 0.4,
          fill: true,
        },
        {
          label: "Revenus",
          data: data.evolutionRev || [],
          borderColor: "#10b981",
          backgroundColor: "rgba(16, 185, 129, 0.1)",
          borderWidth: 3,
          tension: 0.4,
          fill: true,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: { legend: { labels: { color: "#fff" } } },
      scales: {
        y: {
          beginAtZero: true,
          ticks: { color: "#fff" },
          grid: { color: "rgba(255,255,255,0.1)" },
        },
        x: { ticks: { color: "#fff" }, grid: { display: false } },
      },
    },
  });
}

function updateBarChart(data) {
  if (!data) return;
  if (barChart) barChart.destroy();

  const labels = Object.keys(data.categories || {});
  const values = Object.values(data.categories || {});
  const colors = labels.map((label) => {
    const cat = categoriesRef.find((c) => c.nom === label);
    return cat ? cat.color : "#64748b";
  });

  const ctx = document.getElementById("barChart")?.getContext("2d");
  if (!ctx) return;

  barChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Dépenses",
          data: values,
          backgroundColor: colors,
          borderRadius: 8,
          borderSkipped: false,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: {
        y: {
          beginAtZero: true,
          ticks: { color: "#fff" },
          grid: { color: "rgba(255,255,255,0.1)" },
        },
        x: { ticks: { color: "#fff" }, grid: { display: false } },
      },
      onClick: (evt, elements) => {
        if (elements.length > 0) {
          const index = elements[0].index;
          const categorieName = labels[index];
          const categorieId = categoriesIds[categorieName];
          if (categorieId) {
            window.location.href = `/depenses-categorie/${categorieId}`;
          }
        }
      },
      onHover: (event, elements) => {
        try {
          if (event && event.native && event.native.target)
            event.native.target.style.cursor =
              elements.length > 0 ? "pointer" : "default";
        } catch (e) {
          // no-op for compatibility
        }
      },
    },
  });
}

window.addEventListener("load", () => {
  // Initialize from server-provided data
  if (allData && allData[currentPeriod]) {
    updateLineChart(allData[currentPeriod]);
    updateBarChart(allData[currentPeriod]);
  }

  // Expose changePeriod globally so inline buttons can call it
  window.changePeriod = changePeriod;
});
