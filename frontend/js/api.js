/**
 * Budgeometre - Module API
 * Gere toutes les communications avec le backend
 */

const API_URL = 'http://localhost:5000/api';

const api = {
    // =========================================================================
    // SOLDE
    // =========================================================================

    async getSolde() {
        const response = await fetch(`${API_URL}/solde`);
        if (!response.ok) throw new Error('Erreur lors de la recuperation du solde');
        return response.json();
    },

    // =========================================================================
    // TRANSACTIONS
    // =========================================================================

    async getTransactions(options = {}) {
        const params = new URLSearchParams();
        if (options.limit) params.append('limit', options.limit);
        if (options.offset) params.append('offset', options.offset);
        if (options.categorie_id) params.append('categorie_id', options.categorie_id);

        const url = `${API_URL}/transactions${params.toString() ? '?' + params : ''}`;
        const response = await fetch(url);
        if (!response.ok) throw new Error('Erreur lors de la recuperation des transactions');
        return response.json();
    },

    async createTransaction(data) {
        const response = await fetch(`${API_URL}/transactions`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Erreur lors de la creation');
        }
        return response.json();
    },

    async deleteTransaction(id) {
        const response = await fetch(`${API_URL}/transactions/${id}`, {
            method: 'DELETE'
        });
        if (!response.ok) throw new Error('Erreur lors de la suppression');
        return response.json();
    },

    // =========================================================================
    // CATEGORIES
    // =========================================================================

    async getCategories(withTransactions = false) {
        const url = `${API_URL}/categories${withTransactions ? '?with_transactions=true' : ''}`;
        const response = await fetch(url);
        if (!response.ok) throw new Error('Erreur lors de la recuperation des categories');
        return response.json();
    },

    async getCategory(id) {
        const response = await fetch(`${API_URL}/categories/${id}`);
        if (!response.ok) throw new Error('Categorie introuvable');
        return response.json();
    },

    async createCategory(data) {
        const response = await fetch(`${API_URL}/categories`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Erreur lors de la creation');
        }
        return response.json();
    },

    async deleteCategory(id) {
        const response = await fetch(`${API_URL}/categories/${id}`, {
            method: 'DELETE'
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Erreur lors de la suppression');
        }
        return response.json();
    },

    // =========================================================================
    // DASHBOARD
    // =========================================================================

    async getDashboard() {
        const response = await fetch(`${API_URL}/dashboard`);
        if (!response.ok) throw new Error('Erreur lors de la recuperation du dashboard');
        return response.json();
    },

    // =========================================================================
    // DEPENSES PAR CATEGORIE
    // =========================================================================

    async getDepensesCategorie(id) {
        const response = await fetch(`${API_URL}/categories/${id}/depenses`);
        if (!response.ok) throw new Error('Erreur lors de la recuperation des depenses');
        return response.json();
    },

    // =========================================================================
    // OBJECTIFS
    // =========================================================================

    async getObjectifs() {
        const response = await fetch(`${API_URL}/objectifs`);
        if (!response.ok) throw new Error('Erreur lors de la recuperation des objectifs');
        return response.json();
    },

    async createObjectif(data) {
        const response = await fetch(`${API_URL}/objectifs`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Erreur lors de la creation');
        }
        return response.json();
    },

    // =========================================================================
    // UTILITAIRES
    // =========================================================================

    async healthCheck() {
        const response = await fetch(`${API_URL}/health`);
        return response.ok;
    }
};

window.api = api;