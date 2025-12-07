/**
 * Budgeometre - Detail Depense Page JS
 */

let evolutionData = null;
let currentChart = null;

const urlParams = new URLSearchParams(window.location.search);
const categorieId = urlParams.get('id');

document.addEventListener('DOMContentLoaded', async () => {
    if (!categorieId) {
        window.location.href = 'budget-dashboard.html';
        return;
    }
    await chargerDonnees();
});

async function chargerDonnees() {
    try {
        const data = await api.getDepensesCategorie(categorieId);

        document.getElementById('page-title').textContent = 
            'Depenses : ' + data.categorie.nom;
        document.title = 'Depenses - ' + data.categorie.nom + ' - Budgeometre';

        document.getElementById('total-depenses').innerHTML = 
            data.total_depenses.toFixed(2) + ' \u20AC';

        evolutionData = data.evolution;

        createChart(
            evolutionData.mois.labels,
            evolutionData.mois.data,
            'Depenses par mois'
        );

        renderTransactions(data.transactions);

    } catch (error) {
        console.error('Erreur:', error);
        document.getElementById('transactions-container').innerHTML = `
            <div class="no-data">Erreur de chargement</div>
        `;
    }
}

function renderTransactions(transactions) {
    const container = document.getElementById('transactions-container');

    if (!transactions || transactions.length === 0) {
        container.innerHTML = '<div class="no-data">Aucune transaction dans cette categorie</div>';
        return;
    }

    let html = '';
    for (const t of transactions) {
        html += `
            <div class="transaction-item">
                <div class="transaction-info">
                    <div class="transaction-titre">${t.titre}</div>
                    <div class="transaction-date">${t.dateFormatted}</div>
                </div>
                <div class="transaction-montant">${Math.abs(t.montant).toFixed(2)} \u20AC</div>
            </div>
        `;
    }
    container.innerHTML = html;
}

function createChart(labels, data, label) {
    const ctx = document.getElementById('depensesChart').getContext('2d');

    if (currentChart) {
        currentChart.destroy();
    }

    currentChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: label,
                data: data,
                backgroundColor: 'rgba(239, 68, 68, 0.7)',
                borderColor: '#ef4444',
                borderWidth: 2,
                borderRadius: 8,
                borderSkipped: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: '#fff',
                        callback: function(value) {
                            return value + ' \u20AC';
                        }
                    },
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

function showChart(period, btn) {
    document.querySelectorAll('.period-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');

    const titleEl = document.getElementById('chart-title');

    if (!evolutionData) return;

    if (period === 'mois') {
        titleEl.textContent = 'Evolution mensuelle';
        createChart(evolutionData.mois.labels, evolutionData.mois.data, 'Depenses par mois');
    } else if (period === 'trimestre') {
        titleEl.textContent = 'Evolution trimestrielle';
        createChart(evolutionData.trimestre.labels, evolutionData.trimestre.data, 'Depenses par trimestre');
    } else if (period === 'annee') {
        titleEl.textContent = 'Evolution annuelle';
        createChart(evolutionData.annee.labels, evolutionData.annee.data, 'Depenses par annee');
    }
}
