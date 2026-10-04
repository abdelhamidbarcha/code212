import os

# Hna k-n-goulou lih chno l-dossiers li y-t-jahalhom w may-qrahomch
dossiers_interdits = ['venv', '.git', '__pycache__', '.pytest_cache']
fichiers_interdits = ['projet_kamel.txt', 'export.py', '.env'] 

with open('projet_kamel.txt', 'w', encoding='utf-8') as outfile:
    # K-n-dourou 3la ga3 l-fichiers f l-projet dyalk (code212)
    for root, dirs, files in os.walk('.'):
        # K-n-7iydou l-dossiers l-interdits bach may-dkholch l-venv w .git
        dirs[:] = [d for d in dirs if d not in dossiers_interdits]
        
        for file in files:
            # K-n-t2akdou bli l-fichier machi mn l-interdits w y-koun mn had l-anwa3
            if file not in fichiers_interdits and file.endswith(('.py', '.sql', '.yml', '.yaml', 'Dockerfile', '.example', '.gitignore', '.md')):
                path = os.path.join(root, file)
                outfile.write(f"\n\n{'='*50}\n--- Fichier : {path} ---\n{'='*50}\n")
                try:
                    with open(path, 'r', encoding='utf-8') as infile:
                        outfile.write(infile.read())
                except Exception as e:
                    outfile.write(f"Maqderch n-qra l-fichier: {e}\n")

print("Tbarkellah 3lik! L-projet dyalek t-jme3 kamel w nqi f 'projet_kamel.txt'")