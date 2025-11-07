import subprocess
import os
import sys
import re

# Chemin vers l'exécutable rcc.exe de PySide6 (doit être ajusté si votre installation est différente)
# Basé sur le chemin trouvé dans le script Batch.
PYSIDE6_RCC_EXE = r"C:\Users\quent\AppData\Local\Programs\Python\Python313\Lib\site-packages\PySide6\rcc.exe"
RESOURCES_QRC = "resources.qrc"
RESOURCES_RC = "resources_rc.py"

def compile_resources():
    """
    Compile le fichier .qrc en .py en utilisant rcc.exe de PySide6,
    puis corrige le fichier généré pour utiliser les imports PyQt6.
    """
    print("--- Etape 1.5 : Compilation & Correction des ressources Qt (via Python) ---")

    if not os.path.exists(RESOURCES_QRC):
        print(f"[SKIP] Fichier {RESOURCES_QRC} non trouvé. L'étape est ignorée.")
        return True # Succès logique si le fichier n'existe pas

    # --- 1. Compilation avec PySide6 rcc.exe ---
    print(f"[EXEC] Compilation de {RESOURCES_QRC} vers {RESOURCES_RC} en utilisant rcc.exe...")
    try:
        # Commande : "rcc.exe" -g python resources.qrc -o resources_rc.py
        command = [PYSIDE6_RCC_EXE, "-g", "python", RESOURCES_QRC, "-o", RESOURCES_RC]

        # Le 'check=True' lèvera une exception en cas de code de retour non nul
        subprocess.run(command, check=True, capture_output=True, text=True)
        print("[OK] Fichier de ressources temporaire généré par PySide6.")

    except FileNotFoundError:
        print(f"[ERREUR CRITIQUE] L'exécutable rcc.exe est introuvable au chemin: {PYSIDE6_RCC_EXE}")
        print("Veuillez ajuster la variable PYSIDE6_RCC_EXE dans compile_resources.py.")
        return False
    except subprocess.CalledProcessError as e:
        print(f"[ERREUR CRITIQUE] Echec de la compilation par rcc.exe.")
        print(f"Sortie standard : {e.stdout}")
        print(f"Sortie erreur  : {e.stderr}")
        return False

    if not os.path.exists(RESOURCES_RC):
        print(f"[ERREUR CRITIQUE] {RESOURCES_RC} n'a pas été créé malgré le succès apparent de rcc.exe.")
        return False

    # --- 2. Correction des imports PySide6 -> PyQt6 ---
    print(f"[EXEC] Correction des imports PySide6 -> PyQt6 dans {RESOURCES_RC}...")
    try:
        with open(RESOURCES_RC, 'r', encoding='utf-8') as f:
            content = f.read()

        # Remplacement des imports : 'from PySide6' -> 'from PyQt6'
        new_content = re.sub(r'from\s+PySide6', r'from PyQt6', content)

        with open(RESOURCES_RC, 'w', encoding='utf-8') as f:
            f.write(new_content)

        print(f"[OK] Imports mis à jour de PySide6 à PyQt6.")
        return True

    except Exception as e:
        print(f"[ERREUR CRITIQUE] Echec lors de la lecture/écriture de {RESOURCES_RC} ou du remplacement des imports: {e}")
        return False

if __name__ == "__main__":
    if not compile_resources():
        sys.exit(1) # Quitter avec un code d'erreur si la compilation échoue
