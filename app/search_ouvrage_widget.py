# pylint: disable=no-name-in-module
"""
Widget d'affichage et de recherche des ouvrages (SearchOuvrageWidget).
Présente l'inventaire sous forme de tableau et gère les interactions principales
(recherche, affichage des détails, ajout, édition, suppression et export CSV).
"""

import logging
from typing import List, Dict, Any
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QFileDialog, QComboBox
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QTimer
from PyQt6.QtGui import QIcon
from app.db_manager import DBManager
from app.config_manager import ConfigManager
from app.ouvrage_add_modal import OuvrageAddModal
from app.ouvrage_edit_modal import OuvrageEditModal
from app.utils import show_custom_message_box

logger = logging.getLogger(__name__)

class QNumTableWidgetItem(QTableWidgetItem):
    """
    Élément personnalisé de QTableWidgetItem permettant un tri numérique correct.

    Problème résolu :
    - Par défaut, QTableWidget trie les valeurs comme des chaînes (lexicographiquement).
      Exemple : "10" < "2" car "1" est inférieur à "2".
    - Cette classe surcharge l’opérateur < pour comparer les valeurs comme des nombres.

    Fonctionnement :
    1. Convertit le texte de la cellule en float (ou 0 si vide).
    2. Compare la valeur courante avec celle de l’autre cellule.
    3. Si la conversion échoue (valeur non numérique), utilise le tri par défaut.

    Résultat :
    - Les colonnes contenant des nombres sont triées correctement (ordre numérique).
    """

    def __lt__(self, other) -> bool:
        """Surcharge de l'opérateur < pour comparer les nombres."""
        try:
            current_value = float(self.text() or 0)
            other_value = float(other.text() or 0)
            return current_value < other_value
        except ValueError:
            # Fallback : tri lexicographique par défaut
            return QTableWidgetItem.__lt__(self, other)

class SearchOuvrageWidget(QWidget):
    """
    Widget pour la recherche et l'affichage des ouvrages dans un tableau.
    Permet la recherche, l'édition, la suppression et l'exportation.
    """
    ouvrage_edited = pyqtSignal()

    COLUMNS = [
        ("ID", 0),
        ("Auteur", 200),
        ("Titre", 300),
        ("Édition", 150),
        ("Catégorie", 150),
        ("Actions", 160)
    ]
    ACTION_COL_INDEX = 5

    def __init__(self, db_manager: DBManager, config_manager: ConfigManager, initial_theme: str = 'light'):
        """
        Initialise le widget principal du dashboard.

        Paramètres :
        - db_manager : gestionnaire de base de données (accès aux ouvrages, catégories, périodes, etc.)
        - config_manager : gestionnaire de configuration (thème, préférences, etc.)
        - initial_theme : thème initial appliqué au dashboard (par défaut "light").

        Étapes :
        1. Appelle le constructeur parent pour initialiser le widget.
        2. Stocke les gestionnaires et le thème initial comme attributs.
        3. Construit l'interface utilisateur via _setup_ui().
        4. Met à jour les icônes selon le thème initial.
        5. Configure un timer pour rafraîchir les données toutes les 15 secondes.
        6. Le timer déclenche load_ouvrages() pour mettre à jour le tableau.

        Résultat :
        - Dashboard prêt à l’emploi avec UI construite, thème appliqué et données rafraîchies automatiquement.
        """

        # ----- Initialisation de la classe -----
        super().__init__()
        self.db_manager = db_manager
        self.config_manager = config_manager
        self._initial_theme = initial_theme

        # ----- Construction de l'interface -----
        self._setup_ui()

        # ----- Application du thème initial -----
        self.update_icons(self._initial_theme)

        # ----- Rafraîchissement automatique des données -----
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.load_ouvrages)
        self.refresh_timer.start(15000)  # toutes les 15 secondes

    def _setup_ui(self):
        """
        Construit l'interface utilisateur principale du tableau des ouvrages.

        Structure :
        1. Zone de recherche (QLineEdit) avec placeholder et rafraîchissement automatique.
        2. Filtre par localisation (QComboBox) pour afficher les ouvrages selon leur lieu.
        3. Boutons d'action (rafraîchir, effacer, ajouter, exporter CSV).
        4. Tableau des ouvrages (QTableWidget) configuré avec colonnes, en-têtes et comportements.
        5. Footer avec informations de rafraîchissement et message de résultats.
        6. Assemblage final dans un layout vertical.

        Résultat :
        - Interface complète et interactive pour gérer la recherche, le filtrage et l’affichage des ouvrages.
        - Table configurée pour une lecture claire et des actions rapides.
        """

        # 1. Zone de Recherche
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Recherche par Auteur, Titre, Edition ou Catégorie...")
        self.search_input.textChanged.connect(self.load_ouvrages)

        filter_widget = QWidget()
        filter_layout = QHBoxLayout(filter_widget)
        filter_layout.setContentsMargins(0, 0, 0, 0)
        filter_layout.setSpacing(6)

        # 2. Filtre sur la localisation
        self.label_loc_filter = QLabel("Localisation:")
        filter_layout.addWidget(self.label_loc_filter)
        locs = self.db_manager.get_ouvrages_by_location().keys()
        self.combo_loc_filter = QComboBox()
        self.combo_loc_filter.addItem("Toutes")
        self.combo_loc_filter.addItems(sorted(locs))
        filter_layout.addWidget(self.combo_loc_filter, 1)
        self.combo_loc_filter.currentTextChanged.connect(self.load_ouvrages)

        # 3. Boutons d'action
        self.btn_refresh = QPushButton()
        self.btn_refresh.setObjectName("SecondaryActionButton")
        self.btn_refresh.setToolTip("Actualiser la liste des ouvrages")
        self.btn_refresh.setFixedSize(QSize(36, 36))
        self.btn_refresh.clicked.connect(self.load_ouvrages)

        self.btn_clear = QPushButton()
        self.btn_clear.setObjectName("SecondaryActionButton")
        self.btn_clear.setToolTip("Effacer la recherche et afficher tous les ouvrages")
        self.btn_clear.setFixedSize(QSize(36, 36))
        self.btn_clear.clicked.connect(self._handle_clear)

        btn_add = QPushButton("Ajouter un Ouvrage")
        btn_add.setObjectName("PrimaryActionButton")
        btn_add.clicked.connect(self._handle_add_ouvrage)

        btn_export = QPushButton("Exporter CSV")
        btn_export.setObjectName("FilesActionButton")
        btn_export.clicked.connect(self._handle_export_csv)

        # Layout de la recherche, du filtre et des boutons
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.search_input)
        top_layout.addWidget(filter_widget)
        top_layout.addWidget(self.btn_refresh)
        top_layout.addWidget(self.btn_clear)
        top_layout.addWidget(btn_add)
        top_layout.addWidget(btn_export)

        # 4. Tableau des Ouvrages
        self.table_ouvrages = QTableWidget()
        self.table_ouvrages.setObjectName("OuvragesTable")
        self.table_ouvrages.setColumnCount(len(self.COLUMNS))

        # Configuration des en-têtes et des colonnes
        self.table_ouvrages.setHorizontalHeaderLabels([col[0] for col in self.COLUMNS])
        self.table_ouvrages.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_ouvrages.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table_ouvrages.setAlternatingRowColors(False)
        self.table_ouvrages.verticalHeader().setVisible(True)
        self.table_ouvrages.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.table_ouvrages.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table_ouvrages.cellDoubleClicked.connect(self._on_table_cell_double_clicked)

        header = self.table_ouvrages.horizontalHeader()
        self.table_ouvrages.verticalHeader().setDefaultSectionSize(36)

        # Configuration de la politique de redimensionnement des en-têtes
        for i, col_data in enumerate(self.COLUMNS):
            col_name = col_data[0]
            col_width = col_data[1]
            if col_name == "ID":
                self.table_ouvrages.setColumnHidden(i, True)
            elif col_name == "Actions":
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
                header.setMinimumSectionSize(120)
            elif col_name in ["Auteur", "Titre", "Édition", "Catégorie"]:
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
                header.resizeSection(i, col_width)

        # 5. Footer
        self.refresh_info_label = QLabel("Rafraîchissement du tableau toutes les 15 secondes")
        self.refresh_info_label.setObjectName("InstructionLabel")

        self.footer_label = QLabel("Aucun résultat affiché.")
        self.footer_label.setObjectName("ResultFooterLabel")

        footer_widget = QWidget()
        footer_layout = QHBoxLayout(footer_widget)
        footer_layout.setContentsMargins(0, 0, 0, 0)
        footer_layout.setSpacing(0)

        footer_layout.addWidget(self.refresh_info_label, alignment=Qt.AlignmentFlag.AlignLeft)
        footer_layout.addWidget(self.footer_label, alignment=Qt.AlignmentFlag.AlignRight)

        # 6. Assemblage
        main_layout = QVBoxLayout(self)
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.table_ouvrages)
        main_layout.addWidget(footer_widget)

    def update_icons(self, theme_name: str):
        """
        Met à jour les icônes des boutons d'action en fonction du thème choisi.

        Paramètres :
        - theme_name : nom du thème courant ("dark" ou "light").

        Fonctionnement :
        1. Sélectionne les icônes adaptées (blanches pour dark, noires pour light).
        2. Applique l'icône correspondante au bouton d'actualisation (btn_refresh).
        3. Applique l'icône correspondante au bouton d'effacement (btn_clear).
        4. Définit une taille uniforme (24x24) pour les deux icônes.

        Résultat :
        - Les boutons affichent des icônes cohérentes avec le thème actif.
        - L’interface reste lisible et harmonieuse en mode clair ou sombre.
        """

        # ----- Choix des icônes selon le thème -----
        if theme_name == 'dark':
            icon_path_refresh = ":/theme_icons/refresh_white.svg"
            icon_path_clear = ":/theme_icons/clear_white.svg"
        else:
            icon_path_refresh = ":/theme_icons/refresh_black.svg"
            icon_path_clear = ":/theme_icons/clear_black.svg"

        # ----- Application aux boutons -----
        self.btn_refresh.setIcon(QIcon(icon_path_refresh))
        self.btn_refresh.setIconSize(QSize(24, 24))

        self.btn_clear.setIcon(QIcon(icon_path_clear))
        self.btn_clear.setIconSize(QSize(24, 24))

    def load_ouvrages(self):
        """
        Recharge et affiche les ouvrages dans le tableau en appliquant les filtres actifs.

        Fonctionnement :
        1. Récupère tous les ouvrages depuis la base via db_manager.
        2. Applique un filtre texte (auteur, titre, édition, catégorie) si renseigné.
        3. Applique un filtre de localisation si sélectionné :
        - "Toutes" → aucun filtrage.
        - "Non renseignée" → ouvrages sans localisation.
        - Autre localisation → ouvrages correspondant à l'ID de localisation.
        4. Logge les informations de filtrage (localisation choisie, ID, nombre de résultats).
        5. Met à jour le tableau avec les ouvrages filtrés.
        6. Met à jour le footer avec le nombre de résultats et le texte de recherche.

        Résultat :
        - Le tableau reflète toujours l’état actuel de la base en fonction des filtres actifs.
        - Les logs permettent de tracer les opérations de filtrage.
        """

        # 1) Charger tous les ouvrages
        all_ouvrages = self.db_manager.get_all_ouvrages()

        # 2) Filtre texte
        search_text = self.search_input.text().strip().lower()
        if search_text:
            ouvrages = self._filter_ouvrages(all_ouvrages, search_text)
        else:
            ouvrages = all_ouvrages

        # 3) Filtre localisation
        selected_loc = self.combo_loc_filter.currentText().strip() if hasattr(self, "combo_loc_filter") else "Toutes"
        loc_id = None   # initialisation pour éviter l'erreur

        if selected_loc and selected_loc != "Toutes":
            if selected_loc == "Non renseignée":
                ouvrages = [o for o in ouvrages if o.get('id_localisation') in (None, "", 0)]
            else:
                loc_id = self.db_manager.get_location_id_by_name(selected_loc)
                if loc_id is not None:
                    ouvrages = [o for o in ouvrages if o.get('id_localisation') == loc_id]
                else:
                    ouvrages = []

        # 4) Log sécurisé
        logger.info("Filtre localisation: '%s' → loc_id=%s, résultats=%d", selected_loc, loc_id, len(ouvrages))

        # 5) Peuplement du tableau
        self._populate_table(ouvrages)

        # 6) Mise à jour du footer
        self._update_footer_label(len(ouvrages), search_text)

    def _update_footer_label(self, row_count: int, search_text: str):
        """
        Met à jour le pied de page du tableau des résultats.

        Paramètres :
        - row_count : nombre de lignes actuellement affichées dans le tableau.
        - search_text : texte de recherche appliqué (vide si aucun filtre texte).

        Fonctionnement :
        1. Récupère le nombre total d’ouvrages en base (via db_manager).
        - Si indisponible, utilise row_count comme fallback.
        2. Récupère la localisation sélectionnée (ou "Toutes" par défaut).
        3. Formate les nombres avec espaces pour lisibilité.
        4. Construit un texte de filtre (recherche + localisation).
        5. Génère un message adapté :
        - Aucun résultat → message explicite avec total.
        - Résultats trouvés → message avec nombre filtré et total.
        6. Met à jour le footer (QLabel) avec ce message.

        Résultat :
        - Le pied de page reflète toujours l’état actuel des résultats
        et précise les filtres appliqués.
        """

        try:
            total_count = self.db_manager.get_total_ouvrage_count()
        except AttributeError:
            total_count = row_count

        selected_loc = self.combo_loc_filter.currentText().strip() if hasattr(self, "combo_loc_filter") else "Toutes"

        # ----- Formatage des nombres -----
        formatted_count = f"{row_count:,}".replace(",", " ")
        formatted_total = f"{total_count:,}".replace(",", " ")

        # ----- Construction du texte de filtre -----
        filters = []
        if search_text:
            filters.append(f"pour '{search_text}'")
        if selected_loc != "Toutes":
            filters.append(f"dans la localisation '{selected_loc}'")

        filter_text = " ".join(filters)

        # ----- Génération du message -----
        if row_count == 0:
            if filter_text:
                message = f"Aucun ouvrage trouvé {filter_text}. ({formatted_total} au total.)"
            else:
                message = "Aucun ouvrage n'est enregistré dans la base de données."
        else:
            if filter_text:
                message = f"{formatted_count} ouvrages trouvés {filter_text}. ({formatted_total} au total.)"
            else:
                message = f"{formatted_count} ouvrages au total."

        # ----- Mise à jour du footer -----
        self.footer_label.setText(message)

    def _filter_ouvrages(self, ouvrages: List[Dict[str, Any]], search_text: str) -> List[Dict[str, Any]]:
        """
        Filtre une liste d'ouvrages en fonction d'un texte de recherche.

        Paramètres :
        - ouvrages : liste de dictionnaires représentant les ouvrages (champs : auteur, titre, édition, catégorie_nom).
        - search_text : texte de recherche (en minuscules) à comparer.

        Fonctionnement :
        1. Parcourt chaque ouvrage de la liste.
        2. Convertit les champs auteur, titre, édition et catégorie en minuscules.
        3. Vérifie si search_text est contenu dans l’un de ces champs.
        4. Si oui, ajoute l’ouvrage aux résultats.
        5. Retourne la liste des ouvrages filtrés.

        Résultat :
        - Liste des ouvrages correspondant au texte de recherche.
        - Si aucun ouvrage ne correspond, retourne une liste vide.
        """
        results = []
        for ouvrage in ouvrages:
            auteur = str(ouvrage.get('auteur', '')).lower()
            titre = str(ouvrage.get('titre', '')).lower()
            edition = str(ouvrage.get('edition', '')).lower()
            categorie = str(ouvrage.get('categorie_nom', '')).lower()

            if search_text in auteur or search_text in titre or search_text in edition or search_text in categorie:
                results.append(ouvrage)
        return results

    def _populate_table(self, ouvrages: List[Dict[str, Any]]):
        """
        Remplit le QTableWidget avec les ouvrages fournis.

        Paramètres :
        - ouvrages : liste de dictionnaires représentant les ouvrages
                    (champs attendus : id, auteur, titre, edition, categorie_nom).

        Fonctionnement :
        1. Désactive temporairement le tri pour éviter les réordonnancements pendant l’insertion.
        2. Définit le nombre de lignes du tableau selon la taille de la liste.
        3. Pour chaque ouvrage :
        • Insère les colonnes de données (ID, auteur, titre, édition, catégorie).
        • Utilise QNumTableWidgetItem pour l’ID afin de permettre un tri numérique.
        • Aligne le texte à gauche et centré verticalement.
        • Ajoute une colonne "Actions" avec boutons Éditer / Supprimer.
        • Fixe la hauteur de la ligne à 36 px.
        4. Réactive le tri une fois l’insertion terminée.
        5. Ajuste automatiquement la largeur de la colonne "Actions".

        Résultat :
        - Tableau rempli et prêt à l’usage, avec données formatées et actions disponibles.
        """

        # ----- Préparation du tableau -----
        self.table_ouvrages.setSortingEnabled(False)
        self.table_ouvrages.setRowCount(len(ouvrages))

        data_keys = ['id', 'auteur', 'titre', 'edition', 'categorie_nom']

        # ----- Remplissage des lignes -----
        for row_idx, ouvrage in enumerate(ouvrages):
            # Colonnes de données
            for col_idx, key_name in enumerate(data_keys):
                value = ouvrage.get(key_name)
                if value is None or value == "":
                    text = ""
                elif isinstance(value, str):
                    text = value
                else:
                    text = str(value)

                # Tri numérique pour la colonne ID
                if key_name == 'id':
                    item = QNumTableWidgetItem(text)
                else:
                    item = QTableWidgetItem(text)

                # Alignement du texte
                alignment = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
                item.setTextAlignment(alignment)

                self.table_ouvrages.setItem(row_idx, col_idx, item)

            # Colonne Actions
            action_item = QTableWidgetItem("")
            action_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.table_ouvrages.setItem(row_idx, self.ACTION_COL_INDEX, action_item)

            # Ajout des boutons Éditer / Supprimer
            self._action_buttons(row_idx, ouvrage['id'])

            # Fixer la hauteur de la ligne
            self.table_ouvrages.setRowHeight(row_idx, 36)

        # ----- Finalisation -----
        self.table_ouvrages.setSortingEnabled(True)
        self.table_ouvrages.resizeColumnToContents(self.ACTION_COL_INDEX)

    def _action_buttons(self, row: int, ouvrage_id: int):
        """
        Ajoute les boutons d'action 'Éditer' et 'Supprimer' dans une ligne du tableau.

        Paramètres :
        - row : index de la ligne du tableau où insérer les boutons.
        - ouvrage_id : identifiant unique de l’ouvrage concerné.

        Fonctionnement :
        1. Crée un conteneur QWidget pour héberger les boutons.
        2. Configure un layout horizontal sans marges, avec espacement minimal.
        3. Ajoute un bouton "Éditer" relié à la méthode _handle_edit_ouvrage_by_id().
        4. Ajoute un bouton "Supprimer" relié à la méthode _handle_delete_ouvrage_by_id().
        5. Ajoute un stretch pour pousser les boutons à gauche.
        6. Insère ce conteneur dans la colonne "Actions" de la ligne spécifiée.

        Résultat :
        - Chaque ligne du tableau dispose de boutons interactifs pour modifier ou supprimer l’ouvrage.
        """

        # ----- Conteneur des boutons -----
        actions_widget = QWidget()
        actions_widget.setObjectName("ActionButtonsContainer")

        h_layout = QHBoxLayout(actions_widget)
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.setSpacing(2)

        # ----- Bouton Éditer -----
        btn_edit = QPushButton("Éditer")
        btn_edit.setObjectName("EditTableActionButton")
        btn_edit.clicked.connect(lambda: self._handle_edit_ouvrage_by_id(ouvrage_id))
        h_layout.addWidget(btn_edit)

        # ----- Bouton Supprimer -----
        btn_delete = QPushButton("Supprimer")
        btn_delete.setObjectName("DangerTableActionButton")
        btn_delete.clicked.connect(lambda: self._handle_delete_ouvrage_by_id(ouvrage_id))
        h_layout.addWidget(btn_delete)

        # ----- Alignement -----
        h_layout.addStretch()

        # ----- Insertion dans la cellule -----
        self.table_ouvrages.setCellWidget(row, self.ACTION_COL_INDEX, actions_widget)

    def _handle_add_ouvrage(self):
        """
        Ouvre la fenêtre modale pour l'ajout d'un nouvel ouvrage.

        Fonctionnement :
        1. Récupère la fenêtre principale comme parent.
        2. Instancie OuvrageAddModal avec db_manager.
        3. Connecte le signal `ouvrage_updated` à load_ouvrages pour rafraîchir le tableau après ajout.
        4. Exécute la modale en mode bloquant.

        Résultat :
        - Permet à l’utilisateur d’ajouter un ouvrage.
        - Rafraîchit automatiquement le tableau une fois l’ajout validé.
        """
        main_window = self.window()
        modal = OuvrageAddModal(self.db_manager, parent=main_window)
        modal.ouvrage_updated.connect(self.load_ouvrages)
        modal.exec()

    def _handle_edit_ouvrage_by_id(self, ouvrage_id: int):
        """
        Ouvre la fenêtre modale pour l'édition ou la suppression d’un ouvrage existant.

        Paramètres :
        - ouvrage_id : identifiant unique de l’ouvrage à modifier ou supprimer.

        Fonctionnement :
        1. Récupère la fenêtre principale comme parent.
        2. Instancie OuvrageEditModal avec db_manager, config_manager et l’ID de l’ouvrage.
        3. Connecte les signaux :
        • `ouvrage_updated` → rafraîchit le tableau après modification.
        • `ouvrage_deleted` → rafraîchit le tableau après suppression.
        4. Exécute la modale en mode bloquant.

        Résultat :
        - Permet à l’utilisateur de modifier ou supprimer un ouvrage.
        - Rafraîchit automatiquement le tableau après action.
        """
        main_window = self.window()
        modal = OuvrageEditModal(self.db_manager, self.config_manager, ouvrage_id=ouvrage_id, parent=main_window)
        modal.ouvrage_updated.connect(self.load_ouvrages)
        modal.ouvrage_deleted.connect(self.load_ouvrages)
        modal.exec()

    def _handle_delete_ouvrage_by_id(self, ouvrage_id: int):
        """
        Gère la suppression d’un ouvrage identifié par son ID.

        Paramètres :
        - ouvrage_id : identifiant unique de l’ouvrage à supprimer.

        Fonctionnement :
        1. Récupère les détails de l’ouvrage pour afficher son titre dans la confirmation.
        2. Ouvre une boîte de dialogue de confirmation (QMessageBox).
        3. Si l’utilisateur confirme :
        • Appelle db_manager.delete_ouvrage() pour supprimer l’ouvrage.
        • Affiche un message personnalisé (succès ou erreur) via show_custom_message_box().
        • Rafraîchit le tableau si la suppression est réussie.
        4. Si l’utilisateur annule, aucune action n’est effectuée.

        Résultat :
        - L’ouvrage est supprimé de la base si confirmé.
        - L’interface est mise à jour pour refléter l’état actuel.
        """

        # ----- Récupération des détails -----
        ouvrage_details = self.db_manager.get_ouvrage_details(ouvrage_id)
        titre = ouvrage_details.get('titre', 'cet ouvrage') if ouvrage_details else 'cet ouvrage'

        # ----- Confirmation utilisateur -----
        reply = QMessageBox.question(
            self, "Confirmation Suppression",
            f"Êtes-vous sûr de vouloir supprimer définitivement l'ouvrage '<b>{titre}</b>' ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        # ----- Suppression si confirmée -----
        if reply == QMessageBox.StandardButton.Yes:
            success, message = self.db_manager.delete_ouvrage(ouvrage_id)

            if success:
                show_custom_message_box(
                    self,
                    'SUCCESS',
                    'Suppression Ouvrage Réussie',
                    message
                )
                self.load_ouvrages()
            else:
                show_custom_message_box(
                    self,
                    'Erreur Suppression Ouvrage',
                    'Erreur de suppression',
                    message
                )

    def _handle_export_csv(self):
        """
        Gère l’exportation des ouvrages vers un fichier CSV.

        Fonctionnement :
        1. Ouvre une boîte de dialogue pour choisir l’emplacement et le nom du fichier.
        • Propose par défaut "ouvrages_export.csv".
        • Restreint le choix aux fichiers CSV.
        2. Vérifie que l’utilisateur a bien sélectionné un chemin.
        3. Ajoute l’extension ".csv" si elle est absente.
        4. Appelle db_manager.export_all_ouvrages_to_csv() pour effectuer l’export.
        5. Affiche un message personnalisé :
        • Succès → boîte de dialogue de confirmation.
        • Échec → boîte de dialogue d’erreur.

        Résultat :
        - Les ouvrages sont exportés dans un fichier CSV choisi par l’utilisateur.
        - L’interface informe clairement du succès ou de l’échec de l’opération.
        """

        # ----- Sélection du fichier -----
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter les Ouvrages en CSV",
            "ouvrages_export.csv",
            "Fichiers CSV (*.csv)"
        )

        if not file_path:
            return

        # ----- Vérification de l’extension -----
        if not file_path.lower().endswith('.csv'):
            file_path += '.csv'

        # ----- Exportation -----
        success, message = self.db_manager.export_all_ouvrages_to_csv(file_path)

        # ----- Feedback utilisateur -----
        if success:
            show_custom_message_box(
                self,
                'SUCCESS',
                'Exportation CSV Réussie',
                message
            )
        else:
            show_custom_message_box(
                self,
                'ERROR',
                'Erreur Exportation CSV',
                message
            )

    def _on_table_cell_double_clicked(self, row: int, column: int):
        """
        Ouvre la fenêtre modale d’édition lorsqu’un utilisateur double-clique sur une ligne du tableau.

        Paramètres :
        - row : index de la ligne cliquée.
        - column : index de la colonne cliquée.

        Fonctionnement :
        1. Ignore le double-clic si la colonne correspond à "Actions".
        2. Récupère l’ID de l’ouvrage depuis la première colonne (même si cachée).
        3. Vérifie que l’ID est présent et convertible en entier.
        4. Si l’ID est valide, ouvre la modale d’édition via _handle_edit_ouvrage_by_id().
        5. Logge chaque étape (succès ou échec) pour faciliter le suivi.

        Résultat :
        - Permet d’éditer rapidement un ouvrage par double-clic sur sa ligne.
        - Évite les erreurs en cas d’ID manquant ou invalide.
        """

        source_method = "search_ouvrage_widget._on_table_cell_double_clicked"
        logger.info("Ouverture au double clique d'un ouvrage - En cours")

        # ----- Ignorer la colonne Actions -----
        if column == self.ACTION_COL_INDEX:
            return

        # ----- Récupération de l'ID -----
        id_item = self.table_ouvrages.item(row, 0)
        if id_item is None:
            return

        id_text = id_item.text().strip()
        if not id_text:
            logger.info("Ouverture au double clique d'un ouvrage - Echec")
            logger.error("%s - Erreur: id_text est vide", source_method, exc_info=True)
            return

        # ----- Conversion de l'ID -----
        try:
            ouvrage_id = int(id_text)
        except ValueError:
            logger.info("Ouverture au double clique d'un ouvrage - Echec")
            logger.error("%s - Erreur: id_text n’est pas convertible en entier", source_method, exc_info=True)
            return

        # ----- Ouverture de la modale -----
        logger.info("Ouverture au double clique d'un ouvrage - Succès")
        self._handle_edit_ouvrage_by_id(ouvrage_id)

    def _handle_clear(self):
        """
        Réinitialise la recherche et recharge tous les ouvrages dans le tableau.

        Fonctionnement :
        1. Vide le champ de recherche (QLineEdit).
        2. Vide le filtre 'Localisation' (QComboBox)
        3. Relance load_ouvrages() pour afficher l’ensemble des ouvrages sans filtre.

        Résultat :
        - Le tableau est remis à l’état initial, avec tous les ouvrages visibles.
        - Utile pour annuler rapidement un filtre texte et revenir à la vue complète.
        """
        # Réinitialiser la recherche
        self.search_input.clear()
        # Réinitialiser la localisation sur "Toutes"
        if hasattr(self, "combo_loc_filter"):
            self.combo_loc_filter.setCurrentIndex(0)
        # Recharger les ouvrages
        self.load_ouvrages()
