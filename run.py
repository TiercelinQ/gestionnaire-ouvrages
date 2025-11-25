# pylint: disable=no-name-in-module

import sys
import logging
import resources_rc # pylint: disable=unused-import
from app.log.init_logging import setup_exception_hook
from PyQt6.QtWidgets import QApplication
from app.main_app import GestionnaireOuvrageApp
from app.app_info import VERSION

logger = logging.getLogger(__name__)

def main():
    """
    Point d'entrée principal de l'application.
    """
    logger.info("Ouverture Application - version %s", VERSION)
    # 1. Gestion des erreurs
    setup_exception_hook()
    # 2. Initialisation de l'application
    app = QApplication(sys.argv)
    # 3. Comportement de fermeture (Personnalisation)
    app.setQuitOnLastWindowClosed(False)
    # 4. Création de l'Interface Utilisateur
    # Instancie la classe représentant la fenêtre principale de l'application.
    main_window = GestionnaireOuvrageApp()
    # 5. Affichage
    # Rend la fenêtre principale visible à l'utilisateur.
    main_window.show()
    # 6. Démarrage de la Boucle d'Événements
    # Lance la boucle principale de l'application. Le programme bloque ici
    # jusqu'à ce que l'utilisateur ou le code appelle app.quit().
    # 'result' récupère le code de sortie (0 = succès par convention).
    result = app.exec()
    # 7. Sortie finale
    # Quitte le script Python avec le code de sortie retourné par app.exec().
    sys.exit(result)

# L'idiome standard de Python : cette condition assure que main() est appelée
# uniquement si le script est exécuté directement (et non s'il est importé comme module).
if __name__ == "__main__":
    main()