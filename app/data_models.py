"""
Module définissant le schéma de la base de données (noms des tables et instructions SQL).
Contient la classe DBSchema pour une référence centralisée des structures de données
nécessaires à la création et à la manipulation de la BDD.
"""

class DBSchema:
    """
    Définit le schéma de la base de données (noms des tables et structures SQL).
    """

    TABLE_ILLUSTRATIONS = 'illustrations'
    TABLE_CATEGORIES = "categories"
    TABLE_GENRES = "genres"
    TABLE_SOUS_GENRES = "sous_genres"
    TABLE_PERIODES = 'periodes'
    TABLE_RELIURES = 'reliures'
    TABLE_LOCALISATIONS = 'localisations'
    TABLE_USERS = "users"
    TABLE_OUVRAGES = "ouvrages"
    TABLE_LOGS = "logs"

    SCHEMA_ILLUSTRATIONS = f"""
    CREATE TABLE IF NOT EXISTS {TABLE_ILLUSTRATIONS} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL UNIQUE
    );
    """

    SCHEMA_CATEGORIES = f"""
    CREATE TABLE IF NOT EXISTS {TABLE_CATEGORIES} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL UNIQUE
    );
    """

    SCHEMA_GENRES = f"""
    CREATE TABLE IF NOT EXISTS {TABLE_GENRES} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL,
        id_categorie INTEGER NOT NULL,
        FOREIGN KEY (id_categorie) REFERENCES {TABLE_CATEGORIES} (id) ON DELETE CASCADE
    );
    """

    SCHEMA_SOUS_GENRES = f"""
    CREATE TABLE IF NOT EXISTS {TABLE_SOUS_GENRES} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL,
        id_genre INTEGER NOT NULL,
        FOREIGN KEY (id_genre) REFERENCES {TABLE_GENRES} (id) ON DELETE CASCADE
    );
    """

    SCHEMA_PERIODES = f"""
    CREATE TABLE IF NOT EXISTS {TABLE_PERIODES} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL UNIQUE
    );
    """

    SCHEMA_RELIURES = f"""
    CREATE TABLE IF NOT EXISTS {TABLE_RELIURES} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL UNIQUE
    );
    """

    SCHEMA_LOCALISATIONS = f"""
    CREATE TABLE IF NOT EXISTS {TABLE_LOCALISATIONS} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL UNIQUE
    );
    """

    SCHEMA_USERS = f"""
    CREATE TABLE IF NOT EXISTS {TABLE_USERS} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        system_name TEXT NOT NULL UNIQUE,
        user_name TEXT NOT NULL UNIQUE,
        date_creation TEXT NOT NULL
    );
    """

    SCHEMA_OUVRAGES = f"""
    CREATE TABLE IF NOT EXISTS {TABLE_OUVRAGES} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titre TEXT NOT NULL,
        sous_titre TEXT,
        auteur TEXT NOT NULL,
        auteur_2 TEXT,
        titre_original TEXT,
        cycle TEXT,
        tome INTEGER,
        id_illustration INTEGER,
        id_categorie INTEGER,
        id_genre INTEGER,
        id_sous_genre INTEGER,
        id_periode INTEGER,
        edition TEXT,
        collection TEXT,
        edition_annee TEXT,
        edition_numero TEXT,
        edition_premiere_annee TEXT,
        isbn TEXT,
        id_reliure INTEGER,
        nombre_page INTEGER,
        dimension TEXT,
        id_localisation INTEGER,
        localisation_details TEXT,
        --CONTENU
        resume TEXT,
        remarques TEXT,
        couverture_premiere_chemin TEXT,
        couverture_premiere_emplacement TEXT,
        couverture_quatrieme_chemin TEXT,
        couverture_quatrieme_emplacement TEXT,
        date_creation TEXT NOT NULL,
        date_modification TEXT NOT NULL,
        cree_par INTEGER NOT NULL,
        modifie_par INTEGER NOT NULL,
        FOREIGN KEY (id_illustration) REFERENCES {TABLE_ILLUSTRATIONS} (id) ON DELETE SET NULL,
        FOREIGN KEY (id_categorie) REFERENCES {TABLE_CATEGORIES} (id) ON DELETE SET NULL,
        FOREIGN KEY (id_genre) REFERENCES {TABLE_GENRES} (id) ON DELETE SET NULL,
        FOREIGN KEY (id_sous_genre) REFERENCES {TABLE_SOUS_GENRES} (id) ON DELETE SET NULL,
        FOREIGN KEY (id_periode) REFERENCES {TABLE_PERIODES} (id) ON DELETE SET NULL,
        FOREIGN KEY (id_reliure) REFERENCES {TABLE_RELIURES} (id) ON DELETE SET NULL,
        FOREIGN KEY (id_localisation) REFERENCES {TABLE_LOCALISATIONS} (id) ON DELETE SET NULL,
        FOREIGN KEY (cree_par) REFERENCES {TABLE_USERS} (id) ON DELETE SET NULL,
        FOREIGN KEY (modifie_par) REFERENCES {TABLE_USERS} (id) ON DELETE SET NULL
    );
    """

    SCHEMA_LOGS = f"""
    CREATE TABLE IF NOT EXISTS {TABLE_LOGS} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        level TEXT NOT NULL,
        source_module TEXT,
        error_type TEXT,
        message TEXT NOT NULL,
        user_id INTEGER,
        FOREIGN KEY(user_id) REFERENCES {TABLE_USERS}(id)
    );
    """

    ALL_SCHEMAS = [
        SCHEMA_ILLUSTRATIONS,
        SCHEMA_CATEGORIES,
        SCHEMA_GENRES,
        SCHEMA_SOUS_GENRES,
        SCHEMA_PERIODES,
        SCHEMA_RELIURES,
        SCHEMA_LOCALISATIONS,
        SCHEMA_USERS,
        SCHEMA_OUVRAGES,
        SCHEMA_LOGS
    ]
