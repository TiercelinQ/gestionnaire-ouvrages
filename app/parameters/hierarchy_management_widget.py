# pylint: disable=no-name-in-module
"""
Module contenant la classe HierarchyManagementWidget.

Ce widget est conçu pour gérer les classifications hiérarchiques (Catégories, Genres, Sous-genres)
de l'application. Il offre des fonctionnalités CRUD (Créer, Lire, Mettre à jour, Supprimer)
pour ces classifications et permet également l'importation de données
hiérarchiques via un fichier JSON. Il interagit avec le DBManager
pour les opérations de base de données.
"""

import os
import json
from typing import Optional, List, Tuple
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QListWidget, QGroupBox, QInputDialog, QFileDialog, QListWidgetItem, QMessageBox
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QIcon
from app.db_manager import DBManager
from app.data_models import DBSchema
from app.utils import show_custom_message_box, FocusListWidget

class HierarchyManagementWidget(QWidget):
    """
    Widget pour la gestion hiérarchique des classifications : Catégories, Genres, Sous-genres.
    Inclut l'importation JSON.
    """
    data_updated = pyqtSignal()

    def __init__(self, db_manager: DBManager):
        super().__init__()
        self.db_manager = db_manager
        self._setup_ui()
        self.load_categories()

    def _setup_ui(self):
        """
        Configure tous les éléments visuels (widgets et layouts) de la gestion
        hiérarchique des classifications.
        """
        vertical_layout = QVBoxLayout(self)
        vertical_layout.setContentsMargins(0, 0, 0, 0)

        import_layout = QHBoxLayout()
        import_layout.addWidget(QLabel("<h2>Catégories, Genres et Sous-Genres</h2>"))
        import_layout.addStretch(1)
        vertical_layout.addLayout(import_layout)

        classification_horizontal_layout = QHBoxLayout()
        self.category_group = self._create_parameter_group("Catégories", DBSchema.TABLE_CATEGORIES, has_parent=False)
        self.genre_group = self._create_parameter_group("Genres", DBSchema.TABLE_GENRES, has_parent=True)
        self.subgenre_group = self._create_parameter_group("Sous-Genres", DBSchema.TABLE_SOUS_GENRES, has_parent=True)

        classification_horizontal_layout.addWidget(self.category_group)
        classification_horizontal_layout.addWidget(self.genre_group)
        classification_horizontal_layout.addWidget(self.subgenre_group)
        vertical_layout.addLayout(classification_horizontal_layout)
        vertical_layout.addStretch(1)

        vertical_layout.addStretch(1)

        bottom_horizontal_layout = QHBoxLayout()
        bottom_horizontal_layout.addStretch(1)

        self.btn_import_json = QPushButton("Importer Classification (JSON)")
        self.btn_import_json.setObjectName("FilesActionButton")
        self.btn_import_json.clicked.connect(self._import_classifications)

        bottom_horizontal_layout.addWidget(self.btn_import_json)
        vertical_layout.addLayout(bottom_horizontal_layout)

        self.list_categories.itemClicked.connect(self._handle_category_list_click)
        self.list_genres.itemClicked.connect(self._handle_genre_list_click)

    def _create_parameter_group(self, title: str, table_name: str, has_parent: bool) -> QGroupBox:
        """Factorise la création d'une section pour Catégorie, Genre ou Sous-genre."""
        group_box = QGroupBox()
        title_label = QLabel(f"Table: {title}")
        title_label.setObjectName("GroupBoxCustomTitle")
        item_exists_label = QLabel("Liste des valeurs existantes:")
        item_exists_label.setObjectName("GroupBoxCustomSubTitle")
        vertical_layout = QVBoxLayout(group_box)
        vertical_layout.addWidget(title_label)
        vertical_layout.addWidget(item_exists_label)

        # Utilisation du FocusListWidget
        list_widget = FocusListWidget()
        setattr(self, f"list_{table_name}", list_widget)
        list_widget.setObjectName(f"List_{table_name}")
        list_widget.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        vertical_layout.addWidget(list_widget)

        # Ajout d'une nouvelle valeur
        ajout_item = QLabel("Ajout d'une nouvelle valeur")
        ajout_item.setObjectName("GroupBoxCustomSubTitle")
        vertical_layout.addWidget(ajout_item)
        # Zone de saisie
        input_line = QLineEdit()
        setattr(self, f"input_{table_name}", input_line)
        input_line.setPlaceholderText(f"Nom de la nouvelle valeur...")
        vertical_layout.addWidget(input_line)
        # Bouton Ajouter
        btn_add = QPushButton("")
        setattr(self, f"btn_add_{table_name}", btn_add)
        btn_add.setIcon(QIcon(":/buttons_icons/add_white.svg"))
        btn_add.setIconSize(QSize(18, 18))
        btn_add.setObjectName("AddActionButton")
        btn_add.setToolTip("Ajouter un nouvel élément")
        btn_add.clicked.connect(lambda: self._handle_add_item(table_name, has_parent))
        btn_add.setEnabled(False)
        input_line.textChanged.connect(
            lambda text: btn_add.setEnabled(bool(text.strip()))
        )
        # Groupe de composant horizontal
        horizontal_layout = QHBoxLayout()
        horizontal_layout.addWidget(input_line)
        horizontal_layout.addWidget(btn_add)
        vertical_layout.addLayout(horizontal_layout)
        vertical_layout.addSpacing(10)


        instruction_label = QLabel("Cliquer en premier sur une valeur existante, dans la liste ci-dessus, pour l'<b>éditer</b> ou pour la <b>supprimer</b>")
        instruction_label.setWordWrap(True)
        instruction_label.setObjectName("GroupBoxCustomSubTitle")
        vertical_layout.addWidget(instruction_label)

        btn_layout = QHBoxLayout()

        # Bouton Editer
        btn_edit = QPushButton("")
        setattr(self, f"btn_edit_{table_name}", btn_edit)
        btn_edit.setObjectName("EditActionButton")
        btn_edit.setIcon(QIcon(":/buttons_icons/edit_white.svg"))
        btn_edit.setIconSize(QSize(24, 24))
        btn_edit.setToolTip("Éditer l'élément sélectionné")
        btn_edit.clicked.connect(lambda: self._handle_edit_item(table_name))
        btn_edit.setEnabled(False)
        btn_edit.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        btn_layout.addWidget(btn_edit)

        # Bouton Supprimer
        btn_delete = QPushButton("")
        setattr(self, f"btn_delete_{table_name}", btn_delete)
        btn_delete.setObjectName("DangerActionButton")
        btn_delete.setIcon(QIcon(":/buttons_icons/delete_white.svg"))
        btn_delete.setIconSize(QSize(24, 24))
        btn_delete.setToolTip("Supprimer l'élément sélectionné")
        btn_delete.clicked.connect(lambda: self._handle_delete_item(table_name))
        btn_delete.setEnabled(False)
        btn_delete.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        btn_layout.addWidget(btn_delete)
        vertical_layout.addLayout(btn_layout)

        list_widget.itemSelectionChanged.connect(
            lambda: self._toggle_crud_buttons(table_name, bool(list_widget.selectedItems()))
        )

        return group_box

    def _get_list_widget(self, table_name: str) -> QListWidget:
        """Récupère le QListWidget associé au nom de la table."""
        return getattr(self, f"list_{table_name}")

    def _get_input_line(self, table_name: str) -> QLineEdit:
        """Récupère le QLineEdit associé au nom de la table."""
        return getattr(self, f"input_{table_name}")

    def load_categories(self):
        """Point d'entrée pour charger les catégories et vider les listes enfants."""
        self._load_classification_list(DBSchema.TABLE_CATEGORIES)

    def _load_classification_list(self, table_name: str, parent_id: Optional[int] = None):
        """Logique de chargement pour les listes hiérarchiques."""
        list_widget = self._get_list_widget(table_name)
        list_widget.clear()
        data: List[Tuple[int, str]] = []

        if table_name == DBSchema.TABLE_CATEGORIES:
            data = self.db_manager.get_all_categories()
        elif table_name == DBSchema.TABLE_GENRES and parent_id is not None:
            data = self.db_manager.get_genres_by_category_id(parent_id)
        elif table_name == DBSchema.TABLE_SOUS_GENRES and parent_id is not None:
            data = self.db_manager.get_subgenres_by_genre_id(parent_id)
        else:
             return

        for id, nom in data:
            item = QListWidgetItem(nom)
            item.setData(Qt.ItemDataRole.UserRole, id)
            list_widget.addItem(item)

        if table_name == DBSchema.TABLE_CATEGORIES:
             self._get_list_widget(DBSchema.TABLE_GENRES).clear()
             self._get_list_widget(DBSchema.TABLE_SOUS_GENRES).clear()
        elif table_name == DBSchema.TABLE_GENRES:
             self._get_list_widget(DBSchema.TABLE_SOUS_GENRES).clear()

    def _handle_category_list_click(self, item: QListWidgetItem):
        """Charge les genres si une catégorie est sélectionnée."""
        category_id = item.data(Qt.ItemDataRole.UserRole)
        self._load_classification_list(DBSchema.TABLE_GENRES, category_id)
        self._get_list_widget(DBSchema.TABLE_SOUS_GENRES).clear()

    def _handle_genre_list_click(self, item: QListWidgetItem):
        """Charge les sous-genres si un genre est sélectionné."""
        genre_id = item.data(Qt.ItemDataRole.UserRole)
        self._load_classification_list(DBSchema.TABLE_SOUS_GENRES, genre_id)

    def _toggle_crud_buttons(self, table_name: str, enabled: bool):
        """Active/désactive les boutons Editer/Supprimer."""
        btn_edit = getattr(self, f"btn_edit_{table_name}", None)
        btn_delete = getattr(self, f"btn_delete_{table_name}", None)

        if btn_edit:
            btn_edit.setEnabled(enabled)
        if btn_delete:
            btn_delete.setEnabled(enabled)
        if enabled:
            self._get_input_line(table_name).clear()

    def _handle_add_item(self, table_name: str, has_parent: bool):
        """Ajoute un nouvel élément hiérarchique (Catégorie, Genre, Sous-genre)."""
        input_line = self._get_input_line(table_name)
        nom = input_line.text().strip()

        if not nom:
            show_custom_message_box(
                self,
                'Warning',
                "Règle de Validation",
                "Veuillez saisir un nom."
            )
            return

        parent_id: Optional[int] = None

        if has_parent:
            parent_list: QListWidget = None
            parent_name: str = ""

            if table_name == DBSchema.TABLE_GENRES:
                parent_list = self._get_list_widget(DBSchema.TABLE_CATEGORIES)
                parent_name = "Catégorie"
            elif table_name == DBSchema.TABLE_SOUS_GENRES:
                parent_list = self._get_list_widget(DBSchema.TABLE_GENRES)
                parent_name = "Genre"

            selected_parent = parent_list.currentItem()
            if selected_parent:
                parent_id = selected_parent.data(Qt.ItemDataRole.UserRole)

            if parent_id is None:
                show_custom_message_box(
                    self,
                    'WARNING',
                    "Règle de Validation",
                    f'Veuillez sélectionner un(e) {parent_name} parent(e) dans la colonne de gauche.'
                )
                return

        if self.db_manager.add_classification_item(table_name, nom, parent_id):
            input_line.clear()
            self._load_classification_list(table_name, parent_id)
            show_custom_message_box(
                self,
                'SUCCESS',
                "Enregistrement Item Réussi",
                f"'<b>{nom}</b>' ajouté aux <b>{table_name}</b>."
                )
            self.data_updated.emit()
        else:
            show_custom_message_box(
                self,
                'ERROR',
                "Erreur Enregistrement Iteam",
                "Veuiller regarder le journal d'activité pour plus d\'information."
            )

    def _handle_edit_item(self, table_name: str):
        """Modifie le nom de l'élément sélectionné."""
        list_widget = self._get_list_widget(table_name)
        selected_item = list_widget.currentItem()

        if not selected_item:
            show_custom_message_box(
                self,
                'WARNING',
                "Règle de Validation",
                "Veuillez sélectionner une valeur à modifier."
            )
            return

        current_name = selected_item.text()
        item_id = selected_item.data(Qt.ItemDataRole.UserRole)

        new_name, ok = QInputDialog.getText(
            self, f"Modifier {table_name}", f"Nouveau nom pour '<b>{current_name}</b>' :",
            QLineEdit.EchoMode.Normal, current_name
        )

        if ok and new_name and new_name.strip() != current_name:
            if self.db_manager.update_classification_item(table_name, item_id, new_name.strip()):
                show_custom_message_box(
                    self,
                    'SUCCESS',
                    "Mise à jour Item Réussie",
                    f"'<b>{current_name}' renommé en '<b>{new_name.strip()}</b>'."
                )
                self.load_categories()
                self.data_updated.emit()
            else:
                show_custom_message_box(
                    self,
                    'ERROR',
                    "Erreur Mise à Jour Item",
                    "Veuiller regarder le journal d'activité pour plus d\'information.")

    def _handle_delete_item(self, table_name: str):
        """Supprime l'élément sélectionné."""
        list_widget = self._get_list_widget(table_name)
        selected_item = list_widget.currentItem()

        if not selected_item:
            show_custom_message_box(
                self,
                'WARNING',
                "Règle de Validation",
                "Veuillez sélectionner une valeur à supprimer.")
            return

        item_name = selected_item.text()
        item_id = selected_item.data(Qt.ItemDataRole.UserRole)

        result = show_custom_message_box(
            self,
            'QUESTION',
            "Confirmation Suppression",
            f"Êtes-vous sûr de vouloir supprimer '<b>{item_name}</b>' des <b>{table_name}</b> ?",
            "<b>ATTENTION</b>: Tous les ouvrages associés à cet élément perdront cette classification !",
            buttons=['Yes', 'No']
        )

        if result == QMessageBox.StandardButton.Yes:
            if self.db_manager.delete_classification_item(table_name, item_id):
                show_custom_message_box(
                    self,
                    'SUCCESS',
                    "Suppression Item Réussie",
                    f"'<b>{item_name}</b>' a été supprimé des '<b>{table_name}</b>'."
                    )
                self.load_categories()
                self.data_updated.emit()
            else:
                show_custom_message_box(
                    self,
                    'ERROR',
                    "Erreur Suppression Item",
                    "Veuiller regarder le journal d'activité pour plus d\'information.")

    def _import_classifications(self):
        """Ouvre une boîte de dialogue pour importer un fichier JSON de classifications."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner le fichier JSON des Classifications",
            os.path.expanduser("~"),
            "Fichiers JSON (*.json)"
        )

        if not file_path:
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            if 'categories' not in json_data or not isinstance(json_data.get('categories'), dict):
                show_custom_message_box(
                    self,
                    'ERROR',
                    "Erreur Import JSON",
                    "Le fichier JSON doit contenir une clé \'categories\' principale"
                )
                return
            success, message = self.db_manager.import_classification_from_json(json_data)
            if success:
                show_custom_message_box(
                    self,
                    'SUCCESS',
                    "Importation Classification Réussie",
                    message,
                    "(Les doublons ont été ignorés.)"
                )
            else:
                show_custom_message_box(
                    self,
                    'ERROR',
                    "Erreur Importation Classification",
                    message
                )
            self.load_categories()
            self.data_updated.emit()
        except json.JSONDecodeError:
            show_custom_message_box(
                self,
                'ERROR',
                "Erreur Validité JSON",
                "Le fichier sélectionné n\'est pas un fichier JSON valide.")
        except Exception as e:
            show_custom_message_box(
                self,
                'ERROR',
                "Erreur Importation Classification",
                "Veuiller regarder le journal d'activité pour plus d\'information.")