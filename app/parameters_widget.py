# pylint: disable=no-name-in-module
"""
Widget principal de l'onglet 'Paramètres'.
Utilise un QStackedWidget pour organiser la navigation entre les différents outils
de configuration : paramètres utilisateur, gestion des listes de classification
(hiérarchiques et non hiérarchiques), et journal d'activité.
"""

from typing import Optional
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QListWidget, QStackedWidget,
    QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from app.db_manager import DBManager
from app.config_manager import ConfigManager
from app.data_models import DBSchema
from app.parameters.hierarchy_management_widget import HierarchyManagementWidget
from app.parameters.list_management_widget import ListManagementWidget
from app.parameters.log_viewer_widget import LogViewerWidget
from app.parameters.user_settings_widget import UserSettingsWidget

class ParametersWidget(QWidget):
    """
    Widget pour l'onglet de gestion des classifications et des configurations.
    Utilise une structure Menu/StackedWidget pour organiser les différents types de listes.
    Ce widget est le conteneur principal refactorisé.
    """
    # Signal requis par main_app.py
    configuration_updated = pyqtSignal()
    theme_changed = pyqtSignal(str)
    db_path_changed = pyqtSignal(str)

    def __init__(self, db_manager: DBManager, config_manager: ConfigManager):
        super().__init__()
        self.db_manager = db_manager
        self.config_manager = config_manager
        self.setObjectName("ParametersPage")

        # Initialisation des attributs de l'UI
        self.list_menu: Optional[QListWidget] = None
        self.stacked_content: Optional[QStackedWidget] = None
        self.user_settings_widget: Optional[UserSettingsWidget] = None

        # Attributs des autres widgets pour la méthode refresh_classifications
        self.hierarchy_widget: Optional[HierarchyManagementWidget] = None
        self.illustrations_widget: Optional[ListManagementWidget] = None
        self.periods_widget: Optional[ListManagementWidget] = None
        self.bindings_widget: Optional[ListManagementWidget] = None
        self.locations_widget: Optional[ListManagementWidget] = None
        self.log_viewer_widget: Optional[LogViewerWidget] = None

        self._setup_ui()

    def _setup_ui(self):
        """
        Configure la disposition principale (Menu/Contenu empilé) et les connexions.
        """
        h_layout = QHBoxLayout(self)

        # 1. Menu de navigation
        self.list_menu = QListWidget()
        self.list_menu.setObjectName("ParameterMenu")
        self.list_menu.setMaximumWidth(200)
        self._setup_navigation_menu()
        h_layout.addWidget(self.list_menu)

        # 2. Zone de contenu
        self.stacked_content = QStackedWidget()
        self._setup_content_stack()
        h_layout.addWidget(self.stacked_content)

        # 3. Connexions
        self.list_menu.currentRowChanged.connect(self._handle_navigation_change)
        self.list_menu.setCurrentRow(0)

    def _setup_navigation_menu(self):
        """Crée le menu de navigation à gauche (QListWidget)."""
        self.list_menu.setSizePolicy(QSizePolicy.Policy.Minimum,QSizePolicy.Policy.Expanding)
        self.list_menu.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.list_menu.setSizeAdjustPolicy(QListWidget.SizeAdjustPolicy.AdjustToContents)

        self.list_menu.setObjectName("NavigationMenu")

        # Index 0
        self.list_menu.addItem("Mes Paramètres")
        # Index 1
        self.list_menu.addItem("Catégories & Genres")
        # Index 2
        self.list_menu.addItem("Illustrations")
        # Index 3
        self.list_menu.addItem("Périodes")
        # Index 4
        self.list_menu.addItem("Reliures")
        # Index 5
        self.list_menu.addItem("Localisations")
        # Index 6
        self.list_menu.addItem("Journal d'activité")

        self.list_menu.updateGeometries()

    def _setup_content_stack(self):
        """Crée le QStackedWidget et ajoute les widgets de gestion refactorisés."""

        # Index 0 : Mes Paramètres (NOUVEAU)
        self.user_settings_widget = UserSettingsWidget(self.config_manager, self.db_manager)
        self.user_settings_widget.theme_changed.connect(self.theme_changed.emit)
        self.user_settings_widget.db_path_changed.connect(self.db_path_changed.emit)
        self.user_settings_widget.username_changed.connect(lambda _: self.configuration_updated.emit())
        self.stacked_content.addWidget(self.user_settings_widget)

        # Index 1 : Hiérarchie (Catégories/Genres)
        self.hierarchy_widget = HierarchyManagementWidget(self.db_manager)
        self.hierarchy_widget.data_updated.connect(self.configuration_updated.emit)
        self.stacked_content.addWidget(self.hierarchy_widget)

        # Index 2 : Illustrations
        self.illustrations_widget = ListManagementWidget(self.db_manager, "Illustrations", DBSchema.TABLE_ILLUSTRATIONS)
        self.illustrations_widget.data_updated.connect(self.configuration_updated.emit)
        self.stacked_content.addWidget(self.illustrations_widget)

        # Index 3 : Périodes
        self.periods_widget = ListManagementWidget(self.db_manager, "Périodes", DBSchema.TABLE_PERIODES)
        self.periods_widget.data_updated.connect(self.configuration_updated.emit)
        self.stacked_content.addWidget(self.periods_widget)

        # Index 4 : Reliures
        self.bindings_widget = ListManagementWidget(self.db_manager, "Reliures", DBSchema.TABLE_RELIURES)
        self.bindings_widget.data_updated.connect(self.configuration_updated.emit)
        self.stacked_content.addWidget(self.bindings_widget)

        # Index 5 : Localisations
        self.locations_widget = ListManagementWidget(self.db_manager, "Localisations", DBSchema.TABLE_LOCALISATIONS)
        self.locations_widget.data_updated.connect(self.configuration_updated.emit)
        self.stacked_content.addWidget(self.locations_widget)

        # Index 6 : Journal d'activité
        self.log_viewer_widget = LogViewerWidget(self.db_manager)
        self.stacked_content.addWidget(self.log_viewer_widget)

    def _handle_navigation_change(self, index: int):
        """Gère le changement d'onglet de navigation et charge les données au besoin."""
        self.stacked_content.setCurrentIndex(index)
        if index == 6:
            self.log_viewer_widget.load_activity_log()

    # --- API PUBLIQUE REQUISE PAR main_app.py ---
    def refresh_classifications(self):
        """
        Méthode publique requise par main_app.py pour rafraîchir les données de
        classification lorsque l'onglet 'Paramètres' est sélectionné.
        """
        self.hierarchy_widget.load_categories()
        self.illustrations_widget.load_list()
        self.periods_widget.load_list()
        self.bindings_widget.load_list()
        self.locations_widget.load_list()
