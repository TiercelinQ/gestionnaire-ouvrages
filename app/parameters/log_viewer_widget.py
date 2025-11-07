# pylint: disable=no-name-in-module
"""
Module contenant la classe LogViewerWidget, un widget PyQt6
pour l'affichage, le tri et le filtrage des entrées du journal d'activité (logs)
stockées dans la base de données. Il interagit avec le DBManager
pour récupérer les données de log et les présenter dans un QTableWidget.
"""

from typing import List, Tuple
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QTableWidget, QHeaderView, QTableWidgetItem, QGroupBox
)
from PyQt6.QtCore import Qt
from app.db_manager import DBManager

class LogViewerWidget(QWidget):
    """
    Widget pour l'affichage et le filtrage du journal d'activité (Logs) de la BDD.
    """
    def __init__(self, db_manager: DBManager):
        super().__init__()
        self.db_manager = db_manager
        self._setup_ui()
        self._initialize_filters()
        self.load_activity_log()

    def _setup_ui(self):
        """
        Configure tous les éléments visuels (widgets et layouts) du journal d'activité.
        """
        v_layout = QVBoxLayout(self)
        v_layout.setContentsMargins(0, 0, 0, 0)

        title_label_main = QLabel("<h2>Journal d'activité</h2>")
        title_label_main.setObjectName("ActivityLogTitle")
        v_layout.addWidget(title_label_main)

        content_group = QGroupBox()
        content_group.setObjectName("LogContentGroup")
        group_layout = QVBoxLayout(content_group)

        title_label_group = QLabel(f"Table: Logs")
        title_label_group.setObjectName("GroupBoxCustomTitle")
        group_layout.addWidget(title_label_group)

        filter_layout = QHBoxLayout()
        filter_layout.setObjectName("LogFilters")

        self.filter_level = self._create_log_filter_combobox("level")
        self.filter_source = self._create_log_filter_combobox("source_module")
        self.filter_error_type = self._create_log_filter_combobox("error_type")

        level_label = QLabel("Niveau: ")
        level_label.setObjectName("ParametersPage")
        filter_layout.addWidget(level_label)
        filter_layout.addWidget(self.filter_level)
        source_label = QLabel("Source: ")
        source_label.setObjectName("ParametersPage")
        filter_layout.addWidget(source_label)
        filter_layout.addWidget(self.filter_source)
        error_label = QLabel("Erreur: ")
        error_label.setObjectName("ParametersPage")
        filter_layout.addWidget(error_label)
        filter_layout.addWidget(self.filter_error_type)
        filter_layout.addStretch(1)
        group_layout.addLayout(filter_layout)

        self.log_table = QTableWidget()
        self.log_table.setObjectName("LogTable")
        self.log_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.log_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.log_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.log_table.setSortingEnabled(True)

        headers = ["Date", "Heure", "Niveau", "Source", "Type d'erreur", "Message"]
        self.log_table.setColumnCount(len(headers))
        self.log_table.setHorizontalHeaderLabels(headers)

        header = self.log_table.horizontalHeader()
        for i in range(len(headers)):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)

        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)

        group_layout.addWidget(self.log_table, 1)
        v_layout.addWidget(content_group, 1)

    def _create_log_filter_combobox(self, column_name: str) -> QComboBox:
        """Crée une QComboBox pour un filtre de log."""
        combo = QComboBox()
        combo.setObjectName(f"LogFilter_{column_name}")
        combo.currentIndexChanged.connect(self.load_activity_log)
        return combo

    def _initialize_filters(self):
        """Récupère et remplit initialement les options de filtre."""
        for combo, col_name in [
            (self.filter_level, 'level'),
            (self.filter_source, 'source_module'),
            (self.filter_error_type, 'error_type')
        ]:
            distinct_values = self.db_manager.get_distinct_log_values(col_name)

            combo.currentIndexChanged.disconnect(self.load_activity_log)
            combo.clear()
            combo.addItem(f"Tous", userData="")
            for value in distinct_values:
                combo.addItem(value, userData=value)
            combo.currentIndexChanged.connect(self.load_activity_log)

    def load_activity_log(self):
        """Charge les données de log de la BDD et les affiche, en appliquant les filtres."""

        filter_params = {}

        for combo, col_name in [
            (self.filter_level, 'level'),
            (self.filter_source, 'source_module'),
            (self.filter_error_type, 'error_type')
        ]:
            selected_value = combo.currentData()
            if selected_value:
                filter_params[col_name] = selected_value

        log_data: List[Tuple] = self.db_manager.get_activity_log(filters=filter_params)

        self.log_table.setRowCount(0)
        if not log_data:
            return

        self.log_table.setRowCount(len(log_data))

        for row_idx, log_entry in enumerate(log_data):
            timestamp_str = log_entry[1]
            date_part, time_part = self._format_timestamp(timestamp_str)

            self.log_table.setItem(row_idx, 0, QTableWidgetItem(date_part))
            self.log_table.setItem(row_idx, 1, QTableWidgetItem(time_part))
            self.log_table.setItem(row_idx, 2, QTableWidgetItem(log_entry[2]))
            self.log_table.setItem(row_idx, 3, QTableWidgetItem(log_entry[3]))
            self.log_table.setItem(row_idx, 4, QTableWidgetItem(log_entry[4]))
            self.log_table.setItem(row_idx, 5, QTableWidgetItem(log_entry[5]))
            self.log_table.setItem(row_idx, 6, QTableWidgetItem(log_entry[6]))

        self.log_table.resizeRowsToContents()

    def _format_timestamp(self, timestamp_str: str) -> Tuple[str, str]:
        """Formate le timestamp 'YYYY-MM-DD HH:MM:SS' en Date et Heure séparées."""
        try:
            date_part, time_part = timestamp_str.split(' ')
            year, month, day = date_part.split('-')
            formatted_date = f"{day}-{month}-{year}"
            return formatted_date, time_part
        except Exception:
            return timestamp_str, "N/A"