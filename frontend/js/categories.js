/**
 * Budgeometre - Categories Page JS
 */

const categoriesList = document.getElementById('categories-list');
const addForm = document.getElementById('add-category-form');
const messageContainer = document.getElementById('message-container');

document.addEventListener('DOMContentLoaded', async () => {
    await chargerCategories();
});

async function chargerCategories() {
    try {
        const categories = await api.getCategories(true);

        if (categories.length === 0) {
            categoriesList.innerHTML = `
                <div class="empty-state glass-card">
                    <p>Aucune categorie pour l'instant.</p>
                    <p>Ajoutez-en une ci-dessus !</p>
                </div>
            `;
            return;
        }

        let html = '';
        for (const cat of categories) {
            html += renderCategory(cat);
        }
        categoriesList.innerHTML = html;

    } catch (error) {
        console.error('Erreur:', error);
        categoriesList.innerHTML = `
            <div class="empty-state glass-card">
                <p>Erreur de chargement</p>
                <p>Verifiez que le backend est lance.</p>
            </div>
        `;
    }
}

function renderCategory(cat) {
    const transactions = cat.transactions || [];
    let transactionsHtml = '';

    if (transactions.length > 0) {
        for (const t of transactions) {
            const classe = t.montant >= 0 ? 'positif' : 'negatif';
            const signe = t.montant >= 0 ? '+' : '';
            transactionsHtml += `
                <div class="transaction-item">
                    <div class="transaction-info">
                        <div class="transaction-titre">${t.titre}</div>
                        <div class="transaction-date">${t.dateFormatted}</div>
                    </div>
                    <div class="transaction-montant ${classe}">
                        ${signe}${t.montant.toFixed(2)} \u20AC
                    </div>
                </div>
            `;
        }
    } else {
        transactionsHtml = '<div class="no-transactions">Aucune transaction dans cette categorie</div>';
    }

    return `
        <div class="category-card">
            <div class="category-header">
                <div class="category-info">
                    <div class="category-name">${cat.nom}</div>
                    <div class="category-description">${cat.description || 'Aucune description'}</div>
                </div>
                <div class="category-stats">
                    <div class="count">${cat.nb_transactions || 0}</div>
                    <div class="label">transaction(s)</div>
                </div>
                <div class="category-actions">
                    <button type="button" class="btn-toggle" onclick="toggleTransactions(this, 'transactions-${cat.id}')">
                        Voir
                    </button>
                    <button type="button" class="btn-delete" onclick="supprimerCategorie(${cat.id}, '${cat.nom}')">
                        Suppr.
                    </button>
                </div>
            </div>

            <div class="transactions-dropdown" id="transactions-${cat.id}">
                <div class="transactions-list">
                    ${transactionsHtml}
                </div>
            </div>
        </div>
    `;
}

function toggleTransactions(btn, id) {
    const dropdown = document.getElementById(id);
    dropdown.classList.toggle('open');
    btn.classList.toggle('active');

    if (dropdown.classList.contains('open')) {
        btn.textContent = 'Masquer';
    } else {
        btn.textContent = 'Voir';
    }
}

async function supprimerCategorie(id, nom) {
    if (!confirm(`Supprimer la categorie "${nom}" ?`)) {
        return;
    }

    try {
        await api.deleteCategory(id);
        showMessage('Categorie supprimee', 'success');
        await chargerCategories();
    } catch (error) {
        showMessage(error.message, 'error');
    }
}

addForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const nom = document.getElementById('nom').value.trim();
    const description = document.getElementById('description').value.trim();

    if (!nom) {
        showMessage('Le nom est obligatoire', 'error');
        return;
    }

    const btnAdd = document.getElementById('btn-add');
    btnAdd.disabled = true;
    btnAdd.textContent = 'Ajout...';

    try {
        await api.createCategory({ nom, description });
        showMessage('Categorie ajoutee', 'success');
        addForm.reset();
        await chargerCategories();
    } catch (error) {
        showMessage(error.message, 'error');
    } finally {
        btnAdd.disabled = false;
        btnAdd.textContent = 'Ajouter';
    }
});

function showMessage(text, type) {
    messageContainer.innerHTML = `<div class="message ${type}">${text}</div>`;
    setTimeout(() => {
        messageContainer.innerHTML = '';
    }, 3000);
}
