/**
 * Budgeometre - Add Expense Page JS
 */

const form = document.getElementById('expense-form');
const message = document.getElementById('form-message');
const amountInput = document.getElementById('amount');
const amountWrapper = document.getElementById('amount-wrapper');
const submitBtn = document.getElementById('submit-btn');
const categorySelect = document.getElementById('category');

document.addEventListener('DOMContentLoaded', async () => {
    await chargerCategories();
    document.getElementById('date').valueAsDate = new Date();
});

async function chargerCategories() {
    try {
        const categories = await api.getCategories();
        categorySelect.innerHTML = '<option value="" disabled selected>Choisir une categorie</option>';
        
        for (const cat of categories) {
            const option = document.createElement('option');
            option.value = cat.id;
            option.textContent = cat.nom;
            categorySelect.appendChild(option);
        }
    } catch (error) {
        console.error('Erreur chargement categories:', error);
        showMessage('Impossible de charger les categories', 'error');
    }
}

function validateAmount(value) {
    value = value.replace(',', '.');
    const regex = /^\d+(\.\d{0,2})?$/;
    return regex.test(value) && parseFloat(value) > 0;
}

amountInput.addEventListener('input', function() {
    let value = this.value.trim();
    this.value = value.replace(',', '.');

    if (value === '') {
        amountWrapper.classList.remove('error', 'valid');
        return;
    }

    if (validateAmount(value)) {
        amountWrapper.classList.remove('error');
        amountWrapper.classList.add('valid');
    } else {
        amountWrapper.classList.remove('valid');
        amountWrapper.classList.add('error');
    }
});

amountInput.addEventListener('keypress', function(event) {
    const char = String.fromCharCode(event.which);
    const currentValue = this.value;

    if (!/[\d.,]/.test(char)) {
        event.preventDefault();
        return;
    }

    if ((char === '.' || char === ',') && (currentValue.includes('.') || currentValue.includes(','))) {
        event.preventDefault();
        return;
    }

    if (currentValue.includes('.')) {
        const decimals = currentValue.split('.')[1];
        if (decimals && decimals.length >= 2 && char !== '.' && char !== ',') {
            event.preventDefault();
            return;
        }
    }
});

form.addEventListener('submit', async function(event) {
    event.preventDefault();

    const value = amountInput.value.trim();
    if (!validateAmount(value)) {
        amountWrapper.classList.add('error');
        amountInput.focus();
        return;
    }

    submitBtn.disabled = true;
    submitBtn.textContent = 'Enregistrement...';

    const data = {
        titre: document.getElementById('label').value,
        montant: parseFloat(value.replace(',', '.')),
        type: document.querySelector('input[name="type"]:checked').value,
        categorie_id: parseInt(categorySelect.value),
        date: document.getElementById('date').value || null,
        commentaire: document.getElementById('comment').value || null
    };

    try {
        await api.createTransaction(data);
        showMessage('Transaction enregistree avec succes !', 'success');
        
        setTimeout(() => {
            window.location.href = 'index.html';
        }, 1500);

    } catch (error) {
        console.error('Erreur:', error);
        showMessage('Erreur lors de l\'enregistrement: ' + error.message, 'error');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Enregistrer';
    }
});

function showMessage(text, type) {
    message.textContent = text;
    message.className = 'form-message ' + type;
    message.hidden = false;
}
