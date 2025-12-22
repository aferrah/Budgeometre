-- =============================================
-- Script de peuplement de la base Budgeomètre
-- =============================================

-- Nettoyage des tables (optionnel - décommenter si nécessaire)
-- TRUNCATE "TRANSACTION", "OBJECTIF", "ARCHIVE_MENSUELLE", "CATEGORIE" RESTART IDENTITY CASCADE;

-- =============================================
-- CATÉGORIES
-- =============================================
INSERT INTO "CATEGORIE" ("nom", "description", "couleur", "limite_budget") VALUES
    ('Alimentation', 'Courses et restaurants', '#ef4444', 400),
    ('Transport', 'Essence, transports en commun', '#3b82f6', 150),
    ('Loisirs', 'Sorties, cinéma, jeux', '#a855f7', 200),
    ('Logement', 'Loyer et charges', '#f59e0b', 900),
    ('Santé', 'Médecin, pharmacie', '#14b8a6', 100),
    ('Shopping', 'Vêtements, électronique', '#ec4899', 150),
    ('Abonnements', 'Netflix, Spotify, téléphone', '#6366f1', 80),
    ('Épargne', 'Objectifs d''épargne', '#10b981', 0),
    ('Salaire', 'Revenus professionnels', '#22c55e', 0),
    ('Autre', 'Divers', '#64748b', 0)
ON CONFLICT DO NOTHING;

-- =============================================
-- TRANSACTIONS - Décembre 2025 (mois en cours)
-- =============================================

-- Revenus
INSERT INTO "TRANSACTION" ("montant", "dateTransaction", "titre", "commentaire", "idCategorie") VALUES
    (2500.00, '2025-12-01 09:00:00', 'Salaire décembre', 'Virement employeur', (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Salaire')),
    (150.00, '2025-12-15 14:30:00', 'Remboursement assurance', NULL, (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Autre'));

-- Dépenses fixes
INSERT INTO "TRANSACTION" ("montant", "dateTransaction", "titre", "commentaire", "idCategorie") VALUES
    (-850.00, '2025-12-01 10:00:00', 'Loyer décembre', 'Prélèvement automatique', (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Logement')),
    (-45.00, '2025-12-01 10:05:00', 'Électricité', 'EDF', (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Logement')),
    (-15.99, '2025-12-01 10:10:00', 'Netflix', 'Abonnement mensuel', (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Abonnements')),
    (-9.99, '2025-12-01 10:15:00', 'Spotify', 'Abonnement mensuel', (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Abonnements')),
    (-19.99, '2025-12-01 10:20:00', 'Forfait mobile', 'Free Mobile', (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Abonnements'));

-- Courses alimentaires
INSERT INTO "TRANSACTION" ("montant", "dateTransaction", "titre", "commentaire", "idCategorie") VALUES
    (-67.42, '2025-12-02 18:30:00', 'Courses Carrefour', 'Courses de la semaine', (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Alimentation')),
    (-23.50, '2025-12-05 12:15:00', 'Boulangerie', 'Pain et viennoiseries', (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Alimentation')),
    (-89.30, '2025-12-09 19:00:00', 'Courses Leclerc', 'Courses hebdomadaires', (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Alimentation')),
    (-45.00, '2025-12-12 20:30:00', 'Restaurant italien', 'Dîner en famille', (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Alimentation')),
    (-72.15, '2025-12-16 18:45:00', 'Courses Auchan', 'Courses de la semaine', (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Alimentation')),
    (-18.90, '2025-12-19 13:00:00', 'Déjeuner resto', 'Pause déjeuner travail', (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Alimentation')),
    (-156.80, '2025-12-21 16:00:00', 'Courses de Noël', 'Repas de fête', (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Alimentation'));

-- Transport
INSERT INTO "TRANSACTION" ("montant", "dateTransaction", "titre", "commentaire", "idCategorie") VALUES
    (-55.00, '2025-12-03 08:00:00', 'Essence', 'Plein voiture', (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Transport')),
    (-75.00, '2025-12-10 07:45:00', 'Pass Navigo', 'Abonnement mensuel', (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Transport')),
    (-48.50, '2025-12-18 17:30:00', 'Essence', 'Demi-plein', (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Transport'));

-- Loisirs
INSERT INTO "TRANSACTION" ("montant", "dateTransaction", "titre", "commentaire", "idCategorie") VALUES
    (-12.50, '2025-12-07 21:00:00', 'Cinéma', 'Film en IMAX', (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Loisirs')),
    (-35.00, '2025-12-14 15:00:00', 'Escape Game', 'Sortie entre amis', (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Loisirs')),
    (-59.99, '2025-12-20 10:00:00', 'Jeu vidéo', 'Cadeau pour moi', (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Loisirs'));

-- Shopping
INSERT INTO "TRANSACTION" ("montant", "dateTransaction", "titre", "commentaire", "idCategorie") VALUES
    (-79.99, '2025-12-08 14:00:00', 'Vêtements Zara', 'Pull et pantalon', (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Shopping')),
    (-129.00, '2025-12-15 11:00:00', 'Cadeaux de Noël', 'Pour la famille', (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Shopping'));

-- Santé
INSERT INTO "TRANSACTION" ("montant", "dateTransaction", "titre", "commentaire", "idCategorie") VALUES
    (-25.00, '2025-12-11 09:30:00', 'Médecin généraliste', 'Consultation', (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Santé')),
    (-18.50, '2025-12-11 10:15:00', 'Pharmacie', 'Médicaments', (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Santé'));

-- =============================================
-- TRANSACTIONS - Novembre 2025
-- =============================================
INSERT INTO "TRANSACTION" ("montant", "dateTransaction", "titre", "commentaire", "idCategorie") VALUES
    (2500.00, '2025-11-01 09:00:00', 'Salaire novembre', 'Virement employeur', (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Salaire')),
    (-850.00, '2025-11-01 10:00:00', 'Loyer novembre', 'Prélèvement automatique', (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Logement')),
    (-42.00, '2025-11-01 10:05:00', 'Électricité', 'EDF', (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Logement')),
    (-15.99, '2025-11-01 10:10:00', 'Netflix', NULL, (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Abonnements')),
    (-9.99, '2025-11-01 10:15:00', 'Spotify', NULL, (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Abonnements')),
    (-19.99, '2025-11-01 10:20:00', 'Forfait mobile', NULL, (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Abonnements')),
    (-245.80, '2025-11-05 18:00:00', 'Courses du mois', 'Gros plein', (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Alimentation')),
    (-89.50, '2025-11-12 19:30:00', 'Courses semaine', NULL, (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Alimentation')),
    (-67.20, '2025-11-19 18:45:00', 'Courses', NULL, (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Alimentation')),
    (-55.00, '2025-11-08 08:30:00', 'Essence', 'Plein', (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Transport')),
    (-75.00, '2025-11-10 07:45:00', 'Pass Navigo', NULL, (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Transport')),
    (-28.00, '2025-11-15 20:00:00', 'Bowling', 'Sortie amis', (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Loisirs')),
    (-45.00, '2025-11-22 21:00:00', 'Concert', NULL, (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Loisirs')),
    (-149.99, '2025-11-25 14:00:00', 'Chaussures', 'Sneakers', (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Shopping'));

-- =============================================
-- TRANSACTIONS - Octobre 2025
-- =============================================
INSERT INTO "TRANSACTION" ("montant", "dateTransaction", "titre", "commentaire", "idCategorie") VALUES
    (2500.00, '2025-10-01 09:00:00', 'Salaire octobre', NULL, (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Salaire')),
    (200.00, '2025-10-15 14:00:00', 'Prime exceptionnelle', 'Bonus Q3', (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Salaire')),
    (-850.00, '2025-10-01 10:00:00', 'Loyer octobre', NULL, (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Logement')),
    (-38.00, '2025-10-01 10:05:00', 'Électricité', NULL, (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Logement')),
    (-15.99, '2025-10-01 10:10:00', 'Netflix', NULL, (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Abonnements')),
    (-9.99, '2025-10-01 10:15:00', 'Spotify', NULL, (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Abonnements')),
    (-19.99, '2025-10-01 10:20:00', 'Forfait mobile', NULL, (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Abonnements')),
    (-312.40, '2025-10-06 17:00:00', 'Courses mensuelles', NULL, (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Alimentation')),
    (-78.90, '2025-10-14 18:30:00', 'Courses', NULL, (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Alimentation')),
    (-95.00, '2025-10-20 12:00:00', 'Restaurant anniversaire', 'Mon anniversaire!', (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Alimentation')),
    (-62.00, '2025-10-05 08:00:00', 'Essence', NULL, (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Transport')),
    (-75.00, '2025-10-10 07:45:00', 'Pass Navigo', NULL, (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Transport')),
    (-89.00, '2025-10-12 15:00:00', 'Parc attractions', 'Sortie weekend', (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Loisirs')),
    (-35.00, '2025-10-25 20:00:00', 'Théâtre', NULL, (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Loisirs'));

-- =============================================
-- OBJECTIFS D'ÉPARGNE
-- =============================================
INSERT INTO "OBJECTIF" ("montant", "epargne_actuelle", "description", "frequence", "dateDebut", "idCategorie") VALUES
    (1000.00, 450.00, 'Vacances été 2026', 'mensuel', '2025-01-01', (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Épargne')),
    (500.00, 320.00, 'Nouveau téléphone', 'mensuel', '2025-06-01', (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Épargne')),
    (5000.00, 1250.00, 'Fonds d''urgence', 'mensuel', '2025-01-01', (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Épargne')),
    (200.00, 200.00, 'Cadeau anniversaire maman', 'annuel', '2025-10-01', (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Épargne'));

-- Transactions d'épargne (liées aux objectifs)
INSERT INTO "TRANSACTION" ("montant", "dateTransaction", "titre", "commentaire", "idCategorie") VALUES
    (-100.00, '2025-12-01 11:00:00', 'Épargne vacances', 'Versement mensuel', (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Épargne')),
    (-50.00, '2025-12-01 11:05:00', 'Épargne téléphone', 'Versement mensuel', (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Épargne')),
    (-150.00, '2025-12-01 11:10:00', 'Fonds urgence', 'Versement mensuel', (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Épargne')),
    (-100.00, '2025-11-01 11:00:00', 'Épargne vacances', NULL, (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Épargne')),
    (-50.00, '2025-11-01 11:05:00', 'Épargne téléphone', NULL, (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Épargne')),
    (-150.00, '2025-11-01 11:10:00', 'Fonds urgence', NULL, (SELECT "idCategorie" FROM "CATEGORIE" WHERE "nom" = 'Épargne'));

-- =============================================
-- AFFICHAGE DES RÉSULTATS
-- =============================================
SELECT 'Catégories créées:' AS info, COUNT(*) AS total FROM "CATEGORIE";
SELECT 'Transactions créées:' AS info, COUNT(*) AS total FROM "TRANSACTION";
SELECT 'Objectifs créés:' AS info, COUNT(*) AS total FROM "OBJECTIF";