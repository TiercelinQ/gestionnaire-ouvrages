# pylint: disable=no-name-in-module
"""
Module contenant la classe ListManagementWidget.

Ce widget générique est utilisé pour gérer les listes de classifications
non-hiérarchiques (Illustrations, Périodes, Reliures, Localisations)
dans l'application. Il fournit une interface standardisée pour les opérations
CRUD (Créer, Lire, Mettre à jour, Supprimer) sur une table de base de données
spécifiée, en utilisant un QListWidget pour l'affichage.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QListWidget, QGroupBox, QInputDialog, QListWidgetItem, QMessageBox
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QIcon
from app.db_manager import DBManager
from app.data_models import DBSchema
from app.utils import show_custom_message_box, FocusListWidget

class ListManagementWidget(QWidget):
    """
    Widget générique pour la gestion des classifications non-hiérarchiques
    (Illustrations, Périodes, Reliures, Localisations).
    """
    data_updated = pyqtSignal()

    def __init__(self, db_manager: DBManager, title: str, table_name: str):
        super().__init__()
        self.db_manager = db_manager
        self.table_name = table_name
        self.title = title
        self._setup_ui(title)
        self.load_list()

    def _setup_ui(self, title:str):
        """
        Configure tous les éléments visuels (widgets et layouts) de la gestion
        des lits.
        """
        v_layout = QVBoxLayout(self)
        v_layout.setContentsMargins(0, 0, 0, 0)

        v_layout.addWidget(QLabel(f"<h2>{title}</h2>"))
        v_layout.addWidget(self._create_parameter_group(title))
        v_layout.addStretch(1)

    def _get_db_data_function(self):
        """Détermine la méthode du DBManager à appeler en fonction du nom de la table."""
        if self.table_name == DBSchema.TABLE_ILLUSTRATIONS:
            return self.db_manager.get_all_illustrations
        elif self.table_name == DBSchema.TABLE_PERIODES:
            return self.db_manager.get_all_periodes
        elif self.table_name == DBSchema.TABLE_RELIURES:
            return self.db_manager.get_all_reliures
        elif self.table_name == DBSchema.TABLE_LOCALISATIONS:
            return self.db_manager.get_all_localisations
        return None

    def load_list(self):
        """Charge les données de classification dans le QListWidget."""
        data_func = self._get_db_data_function()
        if not data_func:
            return

        self.list_widget.clear()
        data = data_func()

        for id, nom in data:
            item = QListWidgetItem(nom)
            item.setData(Qt.ItemDataRole.UserRole, id)
            self.list_widget.addItem(item)

    def _create_parameter_group(self, title: str) -> QGroupBox:
        """Crée la section (GroupBox) de gestion de la liste."""
        group_box = QGroupBox()
        title_label = QLabel(f"Table: {title}")
        title_label.setObjectName("GroupBoxCustomTitle")
        item_exists_label = QLabel("Liste des valeurs existantes:")
        item_exists_label.setObjectName("GroupBoxCustomSubTitle")
        vertical_layout = QVBoxLayout(group_box)
        vertical_layout.addWidget(title_label)
        vertical_layout.addWidget(item_exists_label)

        self.list_widget = FocusListWidget()
        self.list_widget.setObjectName(f"List_{self.table_name}")
        self.list_widget.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        vertical_layout.addWidget(self.list_widget)
        vertical_layout.addSpacing(10)

        # Ajout d'une nouvelle valeur
        ajout_item = QLabel("Ajout d'une nouvelle valeur")
        ajout_item.setObjectName("GroupBoxCustomSubTitle")
        vertical_layout.addWidget(ajout_item)
        self.input_line = QLineEdit()
        # Zone de saisie
        self.input_line.setPlaceholderText(f"Nom de la nouvelle valeur...")
        # Bouton Ajouter
        self.btn_add = QPushButton("")
        self.btn_add.setIcon(QIcon(":/buttons_icons/add_white.svg"))
        self.btn_add.setObjectName("AddActionButton")
        self.btn_add.setIconSize(QSize(18, 18))
        self.btn_add.setToolTip("Ajouter un nouvel élément")
        self.btn_add.clicked.connect(self._handle_add_item)
        self.btn_add.setEnabled(False)
        self.input_line.textChanged.connect(
            lambda text: self.btn_add.setEnabled(bool(text.strip()))
        )
        # Groupe de composant horizontal
        horizontal_layout = QHBoxLayout()
        horizontal_layout.addWidget(self.input_line)
        horizontal_layout.addWidget(self.btn_add)
        vertical_layout.addLayout(horizontal_layout)
        vertical_layout.addSpacing(10)

        instruction_label = QLabel("Cliquer en premier sur une valeur existante, dans la liste ci-dessus, pour l'<b>éditer</b> ou pour la <b>supprimer</b>")
        instruction_label.setWordWrap(True)
        instruction_label.setObjectName("GroupBoxCustomSubTitle")
        vertical_layout.addWidget(instruction_label)

        btn_layout = QHBoxLayout()

        # Bouton Editer
        self.btn_edit = QPushButton("")
        self.btn_edit.setObjectName("EditActionButton")
        self.btn_edit.setIcon(QIcon(":/buttons_icons/edit_white.svg"))
        self.btn_edit.setIconSize(QSize(24, 24))
        self.btn_edit.setToolTip("Éditer la valeur sélectionnée")
        self.btn_edit.clicked.connect(self._handle_edit_item)
        self.btn_edit.setEnabled(False)

        self.btn_edit.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        btn_layout.addWidget(self.btn_edit)

        # Bouton Supprimer
        self.btn_delete = QPushButton("")
        self.btn_delete.setObjectName("DangerActionButton")
        self.btn_delete.setIcon(QIcon(":/buttons_icons/delete_white.svg"))
        self.btn_delete.setIconSize(QSize(24, 24))
        self.btn_delete.setToolTip("Supprimer la valeur sélectionnée")
        self.btn_delete.clicked.connect(self._handle_delete_item)
        self.btn_delete.setEnabled(False)

        # --- CORRECTION DE FOCUS ---
        self.btn_delete.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        btn_layout.addWidget(self.btn_delete)

        vertical_layout.addLayout(btn_layout)

        # Connexion pour activer/désactiver les boutons CRUD
        self.list_widget.itemSelectionChanged.connect(
            lambda: self._toggle_crud_buttons(bool(self.list_widget.selectedItems()))
        )

        return group_box

    def _toggle_crud_buttons(self, enabled: bool):
        """Active/désactive les boutons Editer/Supprimer."""
        self.btn_edit.setEnabled(enabled)
        self.btn_delete.setEnabled(enabled)
        if enabled:
            self.input_line.clear()

    def _handle_add_item(self):
        """Ajoute un nouvel élément."""
        nom = self.input_line.text().strip()
        if not nom:
            show_custom_message_box(
                self,
                'WARNING',
                "Règle de Validation",
                "Veuillez saisir un nom."
            )
            return

        if self.db_manager.add_classification_item(self.table_name, nom, None):
            self.input_line.clear()
            self.load_list()
            show_custom_message_box(
                self,
                'SUCCESS',
                "Enregistrement Item Réussi",
                f"'<b>{nom}</b>' ajouté aux <b>{self.title}</b>."
            )
            self.data_updated.emit()
        else:
            show_custom_message_box(
                self,
                'ERROR',
                "Erreur Enregistrement Item",
                "Veuiller regarder le journal d'activité pour plus d\'information."
            )

    def _handle_edit_item(self):
        """Modifie l'élément sélectionné."""
        selected_item = self.list_widget.currentItem()
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
            self, f"Modifier {self.title}", f"Nouveau nom pour '<b>{current_name}</b>' :",
            QLineEdit.EchoMode.Normal, current_name
        )

        if ok and new_name and new_name.strip() != current_name:
            if self.db_manager.update_classification_item(self.table_name, item_id, new_name.strip()):
                show_custom_message_box(
                    self,
                    'SUCCESS',
                    "Mise à Jour Iteam Réussie",
                    f"'<b>{current_name}</b>' renommé en '<b>{new_name.strip()}</b>'."
                    )
                self.load_list()
                self.data_updated.emit()
            else:
                show_custom_message_box(
                    self,
                    'ERROR',
                    "Échec de la modification",
                    "Veuiller regarder le journal d'activité pour plus d\'information.")

    def _handle_delete_item(self):
        """Supprime l'élément sélectionné."""
        selected_item = self.list_widget.currentItem()
        if not selected_item:
            show_custom_message_box(
                self,
                'WARNING',
                'Validation !',
                'Veuillez sélectionner une valeur à supprimer.'
                )
            return

        item_name = selected_item.text()
        item_id = selected_item.data(Qt.ItemDataRole.UserRole)

        result = show_custom_message_box(
            self,
            'QUESTION',
            "Confirmation Suppression",
            f"Êtes-vous sûr de vouloir supprimer '<b>{item_name}</b>' des <b>{self.title}</b> ?",
            "<b>ATTENTION</b>: Tous les ouvrages associés à cet élément perdront cette classification !",
            buttons=['Yes', 'No']
        )

        if result == QMessageBox.StandardButton.Yes:
            if self.db_manager.delete_classification_item(self.table_name, item_id):
                show_custom_message_box(
                    self,
                    'SUCCESS',
                    "Suppression Item Réussie",
                    f"'<b>{item_name}</b>' a été supprimé des </b>{self.title}</b>."
                )
                self.load_list()
                self.data_updated.emit()
            else:
                show_custom_message_box(
                    self,
                    'ERROR',
                    "Échec Suppression Item",
                    "Veuiller regarder le journal d'activité pour plus d\'information."
                )
