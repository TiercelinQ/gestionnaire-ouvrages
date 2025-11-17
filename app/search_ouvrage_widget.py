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
    QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QTimer
from PyQt6.QtGui import QIcon
from app.db_manager import DBManager
from app.ouvrage_add_modal import OuvrageAddModal
from app.ouvrage_edit_modal import OuvrageEditModal
from app.utils import show_custom_message_box

logger = logging.getLogger(__name__)

class QNumTableWidgetItem(QTableWidgetItem):
    """
    QTableWidgetItem personnalisé pour garantir un tri numérique correct
    dans QTableWidget, car le tri par défaut est lexicographique.
    """
    def __lt__(self, other) -> bool:
        """Surcharge de l'opérateur < pour comparer les nombres."""
        try:
            current_value = float(self.text() or 0)
            other_value = float(other.text() or 0)
            return current_value < other_value
        except ValueError:
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

    def __init__(self, db_manager: DBManager, initial_theme: str = 'light'):
        super().__init__()
        self.db_manager = db_manager
        self._initial_theme = initial_theme
        self._setup_ui()
        self.update_icons(self._initial_theme)
        # Rafraîchit automatiquement les données affichées dans le tableau
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.load_ouvrages)
        self.refresh_timer.start(15000)

    def _setup_ui(self):
        # 1. Zone de Recherche
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Recherche par Auteur, Titre, Edition ou Catégorie...")
        self.search_input.textChanged.connect(self.load_ouvrages)

        # 2. Boutons d'action
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

        # Layout des boutons et de la recherche
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.search_input)
        top_layout.addWidget(self.btn_refresh)
        top_layout.addWidget(self.btn_clear)
        top_layout.addWidget(btn_add)
        top_layout.addWidget(btn_export)

        # 2. Tableau des Ouvrages
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
                # Colonne Actions : s'adapte automatiquement à la taille du contenu
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
                header.setMinimumSectionSize(120)
            elif col_name in ["Auteur", "Titre", "Édition", "Catégorie"]:
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
                header.resizeSection(i, col_width)

        # 3. Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.table_ouvrages)

        self.footer_label = QLabel("Aucun résultat affiché.")
        self.footer_label.setObjectName("ResultFooterLabel")
        main_layout.addWidget(self.footer_label)

    def update_icons(self, theme_name: str):
        """Met à jour l'icône du bouton d'actualisation en fonction du thème."""

        if theme_name == 'dark':
            icon_path_refresh = ":/theme_icons/refresh_white.svg"
            icon_path_clear = ":/theme_icons/clear_white.svg"
        else:
            icon_path_refresh = ":/theme_icons/refresh_black.svg"
            icon_path_clear = ":/theme_icons/clear_black.svg"

        self.btn_refresh.setIcon(QIcon(icon_path_refresh))
        self.btn_refresh.setIconSize(QSize(24, 24))

        self.btn_clear.setIcon(QIcon(icon_path_clear))
        self.btn_clear.setIconSize(QSize(24, 24))

    def load_ouvrages(self):
        """
        Recharge les ouvrages depuis la base, puis applique le filtre éventuel.
        """
        all_ouvrages = self.db_manager.get_all_ouvrages()

        search_text = self.search_input.text().strip().lower()
        if search_text:
            ouvrages = self._filter_ouvrages(all_ouvrages, search_text)
        else:
            ouvrages = all_ouvrages

        self._populate_table(ouvrages)
        self._update_footer_label(len(ouvrages), search_text)

    def _update_footer_label(self, row_count: int, search_text: str):
        """
        Construit et met à jour le texte du pied de page des résultats (self.footer_label).
        :param row_count: Nombre de résultats affichés après filtrage.
        :param search_text: Le texte de recherche utilisé.
        """
        try:
            total_count = self.db_manager.get_total_ouvrage_count()
        except AttributeError:
            total_count = row_count
        if row_count == 0:
            if search_text:
                message = (f"Aucun ouvrage trouvé pour '{search_text}'. "
                        f"({total_count:,} au total.)").replace(",", " ")
            else:
                message = "Aucun ouvrage n'est enregistré dans la base de données."
        elif row_count == total_count and not search_text:
            formatted_count = f"{row_count:,}".replace(",", " ")
            message = f"{formatted_count} ouvrages au total."
        else:
            formatted_count = f"{row_count:,}".replace(",", " ")
            formatted_total = f"{total_count:,}".replace(",", " ")
            message = (f"{formatted_count} ouvrages trouvés pour '{search_text}'. "
                    f"({formatted_total} au total.)")
        self.footer_label.setText(message)

    def _filter_ouvrages(self, ouvrages: List[Dict[str, Any]], search_text: str) -> List[Dict[str, Any]]:
        """
        Filtre la liste des ouvrages basés sur le texte de recherche (Titre, Auteur ou Catégorie).
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
        """Remplit le QTableWidget avec les données fournies."""
        self.table_ouvrages.setSortingEnabled(False)
        self.table_ouvrages.setRowCount(len(ouvrages))

        data_keys = ['id', 'auteur', 'titre', 'edition', 'categorie_nom']

        for row_idx, ouvrage in enumerate(ouvrages):
            # --- Colonnes de données ---
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

            # --- Colonne Actions ---
            action_item = QTableWidgetItem("")
            action_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.table_ouvrages.setItem(row_idx, self.ACTION_COL_INDEX, action_item)

            # Ajout des boutons Éditer / Supprimer
            self._action_buttons(row_idx, ouvrage['id'])

            # Fixer la hauteur de la ligne immédiatement
            self.table_ouvrages.setRowHeight(row_idx, 36)

        # Réactiver le tri après insertion
        self.table_ouvrages.setSortingEnabled(True)

        # Ajuster la largeur de la colonne Actions
        self.table_ouvrages.resizeColumnToContents(self.ACTION_COL_INDEX)

    def _action_buttons(self, row: int, ouvrage_id: int):
        """
        Crée les boutons 'Editer' et 'Supprimer'.
        """
        actions_widget = QWidget()
        actions_widget.setObjectName("ActionButtonsContainer")
        h_layout = QHBoxLayout(actions_widget)
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.setSpacing(2)

        btn_edit = QPushButton("Éditer")
        btn_edit.setObjectName("EditTableActionButton")
        btn_edit.clicked.connect(lambda: self._handle_edit_ouvrage_by_id(ouvrage_id))
        h_layout.addWidget(btn_edit)

        btn_delete = QPushButton("Supprimer")
        btn_delete.setObjectName("DangerTableActionButton")
        btn_delete.clicked.connect(lambda: self._handle_delete_ouvrage_by_id(ouvrage_id))
        h_layout.addWidget(btn_delete)

        h_layout.addStretch()

        self.table_ouvrages.setCellWidget(row, self.ACTION_COL_INDEX, actions_widget)

    def _handle_add_ouvrage(self):
        """Ouvre la modale pour l'ajout d'un ouvrage (OuvrageAddModal)."""
        main_window = self.window()
        modal = OuvrageAddModal(self.db_manager, parent=main_window)
        modal.ouvrage_updated.connect(self.load_ouvrages)
        modal.exec()

    def _handle_edit_ouvrage_by_id(self, ouvrage_id: int):
        """Ouvre la modale pour l'édition/suppression d'un ouvrage (OuvrageEditModal)."""
        main_window = self.window()
        modal = OuvrageEditModal(self.db_manager, ouvrage_id=ouvrage_id, parent=main_window)
        modal.ouvrage_updated.connect(self.load_ouvrages)
        modal.ouvrage_deleted.connect(self.load_ouvrages)
        modal.exec()

    def _handle_delete_ouvrage_by_id(self, ouvrage_id: int):
        """
        Gère la suppression de l'ouvrage ayant l'ID donné.
        """
        ouvrage_details = self.db_manager.get_ouvrage_details(ouvrage_id)
        titre = ouvrage_details.get('titre', 'cet ouvrage') if ouvrage_details else 'cet ouvrage'

        reply = QMessageBox.question(
            self, "Confirmation Suppression",
            f"Êtes-vous sûr de vouloir supprimer définitivement l'ouvrage '<b>{titre}</b>' ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

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
        """Gère l'exportation des ouvrages vers un fichier CSV."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter les Ouvrages en CSV",
            "ouvrages_export.csv",
            "Fichiers CSV (*.csv)"
        )

        if not file_path:
            return

        if not file_path.lower().endswith('.csv'):
            file_path += '.csv'

        success, message = self.db_manager.export_all_ouvrages_to_csv(file_path)

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
        Ouvre la modale d'édition lorsqu'un utilisateur double-clique sur une ligne,
        sauf si le double-clic a lieu dans la colonne 'Actions'.
        """
        source_method = "search_ouvrage_widget._on_table_cell_double_clicked"
        logger.info("Ouverture au double clique d'un ouvrage - En cours")
        # Ignorer la colonne Actions
        if column == self.ACTION_COL_INDEX:
            return

        # Récupérer l'ID de l'ouvrage (colonne 0, même si elle est cachée)
        id_item = self.table_ouvrages.item(row, 0)
        if id_item is None:
            return

        id_text = id_item.text().strip()
        if not id_text:
            logger.info("Ouverture au double clique d'un ouvrage - Echec")
            logger.error("%s - Erreur: id_text est vide", source_method, exc_info=True)
            return

        try:
            ouvrage_id = int(id_text)
        except ValueError:
            logger.info("Ouverture au double clique d'un ouvrage - Echec")
            logger.error("%s - Erreur: id_text n’est pas convertible en entier", source_method, exc_info=True)
            return

        # Ouvrir la modale d'édition
        logger.info("Ouverture au double clique d'un ouvrage - Succès")
        self._handle_edit_ouvrage_by_id(ouvrage_id)

    def _handle_clear(self):
        """Vide la recherche et recharge tous les ouvrages."""
        self.search_input.clear()
        self.load_ouvrages()