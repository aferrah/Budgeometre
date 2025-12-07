/**
 * Budgeometre - Index Page JS
 */

document.addEventListener('DOMContentLoaded', async () => {
    await chargerSolde();
    await chargerTransactions();
});

async function chargerSolde() {
    try {
        const data = await api.getSolde();

        document.getElementById('montant').innerHTML = data.solde.toFixed(2) + ' \u20AC';
        document.getElementById('revenus').innerHTML = '+' + data.revenus.toFixed(2) + ' \u20AC';
        document.getElementById('depenses').innerHTML = '-' + data.depenses.toFixed(2) + ' \u20AC';

        const circle = document.getElementById('solde-circle');
        if (data.solde >= 0) {
            circle.classList.remove('negatif');
            circle.classList.add('positif');
        } else {
            circle.classList.remove('positif');
            circle.classList.add('negatif');
        }
    } catch (error) {
        console.error('Erreur chargement solde:', error);
    }
}

async function chargerTransactions() {
    const container = document.getElementById('transactions-container');

    try {
        const data = await api.getTransactions({ limit: 10 });

        if (data.transactions.length === 0) {
            container.innerHTML = `
                <p style="color: rgba(255, 255, 255, 0.7); text-align: center; padding: 20px;">
                    Aucune transaction enregistree pour l'instant.
                </p>
            `;
            return;
        }

        let html = `
            <table>
                <thead>
                    <tr>
                        <th>Libelle</th>
                        <th>Categorie</th>
                        <th>Montant</th>
                    </tr>
                </thead>
                <tbody>
        `;

        for (const t of data.transactions) {
            const classe = t.montant >= 0 ? 'positif' : 'negatif';
            const signe = t.montant >= 0 ? '+' : '';
            html += `
                <tr>
                    <td>${t.titre}</td>
                    <td>${t.categorie.nom}</td>
                    <td class="montant-cell ${classe}">
                        ${signe}${t.montant.toFixed(2)} \u20AC
                    </td>
                </tr>
            `;
        }

        html += '</tbody></table>';
        container.innerHTML = html;

    } catch (error) {
        console.error('Erreur chargement transactions:', error);
        container.innerHTML = `
            <p style="color: #ef4444; text-align: center; padding: 20px;">
                Impossible de charger les transactions.<br>
                Verifiez que le backend est lance sur le port 5000.
            </p>
        `;
    }
}
