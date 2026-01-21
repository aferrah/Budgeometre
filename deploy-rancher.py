#!/usr/bin/env python3
import subprocess
import os
import time
import shutil

def run_command(cmd, description="", check=True):
    """Exécute une commande et affiche le résultat"""
    if description:
        print(f"\n>>> {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=False, capture_output=True, text=True, encoding='utf-8', errors='replace')
        if result.stdout:
            print(result.stdout.strip())
        if result.stderr and "forbidden" not in result.stderr.lower():
            print(result.stderr.strip())
        if check and result.returncode != 0:
            print(f"❌ Erreur lors de l'exécution de: {cmd}")
            return False
        return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def main():
    print("""
  ____            _                                  _            
 |  _ \          | |                                | |           
 | |_) |_   _  __| | __ _  ___  ___  _ __ ___   ___| |_ _ __ ___ 
 |  _ <| | | |/ _` |/ _` |/ _ \/ _ \| '_ ` _ \ / _ \ __| '__/ _ \\
 | |_) | |_| | (_| | (_| |  __/ (_) | | | | | |  __/ |_| | |  __/
 |____/ \__,_|\__,_|\__, |\___|\___/|_| |_| |_|\___|\__|_|  \___|
                     __/ |                                        
                    |___/                                         
""")
    
    print("=" * 42)
    print("  Déploiement sur Cluster Rancher")
    print("=" * 42)
    
    # Configuration
    DOCKER_USERNAME = os.environ.get("DOCKER_USERNAME", "eclairz422")
    IMAGE_TAG = os.environ.get("IMAGE_TAG", "latest")
    
    print(f"\nConfiguration:")
    print(f"  Docker Hub User: {DOCKER_USERNAME}")
    print(f"  Image Tag: {IMAGE_TAG}")
    
    # Vérifier la connexion au cluster
    if not run_command("kubectl cluster-info", "Vérification de la connexion au cluster", check=False):
        print("❌ Impossible de se connecter au cluster Kubernetes")
        return 1
    
    result = subprocess.run("kubectl config current-context", shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    CURRENT_CONTEXT = result.stdout.strip()
    print(f"✓ Connecté au cluster: {CURRENT_CONTEXT}")
    
    # Vérifier Docker
    if not run_command("docker version", "Vérification de Docker", check=False):
        print("❌ Docker n'est pas disponible")
        return 1
    print("✓ Docker est disponible")
    
    # Demander confirmation
    response = input(f"\nVoulez-vous continuer le déploiement sur '{CURRENT_CONTEXT}' ? (y/n) ")
    if response.lower() != 'y':
        print("Déploiement annulé")
        return 0
    
    # Demander si on veut build les images
    build_images = input("\nVoulez-vous build et push les images Docker ? (y/n) ")
    
    if build_images.lower() == 'y':
        # Build et push des images
        print("\n>>> Build et push des images Docker...")
        
        images = [
            ("./gateway", f"{DOCKER_USERNAME}/budgeometre-gateway:{IMAGE_TAG}", "Gateway"),
            (".", f"{DOCKER_USERNAME}/budgeometre-ecriture:{IMAGE_TAG}", "Service Écriture", "services/ecriture/Dockerfile"),
            (".", f"{DOCKER_USERNAME}/budgeometre-lecture:{IMAGE_TAG}", "Service Lecture", "services/lecture/Dockerfile")
        ]
        
        for item in images:
            if len(item) == 3:
                build_context, image_name, description = item
                dockerfile = ""
            else:
                build_context, image_name, description, dockerfile = item
            
            print(f"\n  - {description}...")
            cmd = f"docker build -t {image_name}"
            if dockerfile:
                cmd += f" -f {dockerfile}"
            cmd += f" {build_context}"
            
            if not run_command(cmd):
                return 1
            if not run_command(f"docker push {image_name}"):
                return 1
        
        print("\n✓ Images créées et poussées vers Docker Hub")
    else:
        print("\n⊳ Skip du build des images")
    
    # Déployer sur Kubernetes
    print("\n>>> Déploiement Kubernetes...")
    run_command("kubectl apply -f k8s/", "Application des manifests", check=False)
    
    print("\n>>> Attente du démarrage des pods...")
    time.sleep(10)
    
    # Statut du déploiement
    print("\n" + "=" * 42)
    print("  Statut du déploiement")
    print("=" * 42 + "\n")
    
    run_command("kubectl get pods -n u-grp5")
    print()
    run_command("kubectl get services -n u-grp5")
    print()
    run_command("kubectl get ingress -n u-grp5")
    
    print("\n" + "=" * 42)
    print("  Déploiement terminé !")
    print("=" * 42)
    print("\nPour accéder à l'application:")
    print("  1. Via port-forward:")
    print("     kubectl port-forward -n u-grp5 service/gateway 8080:5000")
    print("     Accéder à: http://localhost:8080")
    print("\n  2. Via Ingress (si configuré):")
    print("     Vérifier l'URL avec: kubectl get ingress -n u-grp5")
    print()

if __name__ == "__main__":
    exit(main())
