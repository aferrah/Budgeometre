/**
 * Budgeometre - Budget Dashboard Page JS
 */

const categoriesRef = [
    { nom: 'Alimentation', color: '#10b981' },
    { nom: 'Transport', color: '#3b82f6' },
    { nom: 'Loisirs', color: '#f59e0b' },
    { nom: 'Logement', color: '#8b5cf6' },
    { nom: 'Sante', color: '#ec4899' },
    { nom: 'Vetements', color: '#14b8a6' },
    { nom: 'Education', color: '#f97316' },
    { nom: 'Epargne', color: '#06b6d4' },
    { nom: 'Autres', color: '#64748b' },
    { nom: 'Autre', color: '#64748b' }
];

let allData = null;
let lineChart = null;
let barChart = null;
let currentPeriod = 'month';

document.addEventListener('DOMContentLoaded', async () => {
    await chargerDashboard();
});

async function chargerDashboard() {
    try {
        allData = await api.getDashboard();
        updateDisplay(allData[currentPeriod]);
    } catch (error) {
        console.error('Erreur chargement dashboard:', error);
    }
}

function changePeriod(period, btn) {
    currentPeriod = period;

    document.querySelectorAll('.period-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');

    if (allData) {
        updateDisplay(allData[period]);
    }
}

function updateDisplay(data) {
    document.getElementById('stat-depenses').innerHTML = data.depenses.toFixed(2) + ' \u20AC';
    document.getElementById('stat-revenus').innerHTML = data.revenus.toFixed(2) + ' \u20AC';
    document.getElementById('stat-solde').innerHTML = data.solde.toFixed(2) + ' \u20AC';
    document.getElementById('stat-solde').style.color = data.solde >= 0 ? '#22c55e' : '#ef4444';
    
    const soldeLabel = document.getElementById('stat-solde-label');
    soldeLabel.innerHTML = '<span>' + (data.solde >= 0 ? 'Excedent' : 'Deficit') + '</span>';
    soldeLabel.className = 'stat-change ' + (data.solde >= 0 ? 'up' : 'down');

    const objectifs = allData.objectifs;
    document.getElementById('stat-objectifs').textContent = 
        objectifs.respectes + '/' + objectifs.total;
    document.getElementById('stat-objectifs-ratio').innerHTML = 
        '<span>' + objectifs.ratio + '% respectes</span>';

    document.getElementById('periode-label').textContent = data.label;
    document.getElementById('periode-label-2').textContent = data.label;

    const titles = {
        'month': 'Evolution (6 derniers mois)',
        'quarter': 'Evolution (4 derniers trimestres)',
        'year': 'Evolution (3 dernieres annees)'
    };
    document.getElementById('evolution-title').textContent = titles[currentPeriod];

    updateLineChart(data);
    updateBarChart(data);
}

function updateLineChart(data) {
    if (lineChart) {
        lineChart.destroy();
    }

    const ctx = document.getElementById('lineChart').getContext('2d');
    lineChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.evolution.labels,
            datasets: [
                {
                    label: 'Depenses',
                    data: data.evolution.depenses,
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    borderWidth: 3,
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Revenus',
                    data: data.evolution.revenus,
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    borderWidth: 3,
                    tension: 0.4,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { labels: { color: '#fff' } }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { color: '#fff' },
                    grid: { color: 'rgba(255,255,255,0.1)' }
                },
                x: {
                    ticks: { color: '#fff' },
                    grid: { display: false }
                }
            }
        }
    });
}

function updateBarChart(data) {
    if (barChart) {
        barChart.destroy();
    }

    const categories = data.categories;
    const labels = Object.keys(categories);
    const values = labels.map(l => categories[l].montant);
    const colors = labels.map(label => {
        const cat = categoriesRef.find(c => c.nom === label);
        return cat ? cat.color : '#64748b';
    });

    const ctx = document.getElementById('barChart').getContext('2d');
    barChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Depenses',
                data: values,
                backgroundColor: colors,
                borderRadius: 8,
                borderSkipped: false
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { color: '#fff' },
                    grid: { color: 'rgba(255,255,255,0.1)' }
                },
                x: {
                    ticks: { color: '#fff' },
                    grid: { display: false }
                }
            },
            onClick: (event, elements) => {
                if (elements.length > 0) {
                    const index = elements[0].index;
                    const categorieName = labels[index];
                    const categorieId = categories[categorieName].id;
                    if (categorieId) {
                        window.location.href = `detail-depense.html?id=${categorieId}`;
                    }
                }
            },
            onHover: (event, elements) => {
                event.native.target.style.cursor = elements.length > 0 ? 'pointer' : 'default';
            }
        }
    });
}
