#!/usr/bin/env python3
import subprocess
import time

def run_command(cmd, description=""):
    """Exécute une commande et affiche le résultat"""
    if description:
        print(f"\n>>> {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=False, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.stderr and "forbidden" not in result.stderr.lower():
            print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"Erreur: {e}")
        return False

def main():
    print("=" * 42)
    print("  Nettoyage des anciennes ressources")
    print("=" * 42)
    
    NAMESPACE = "u-grp5"
    
    run_command(
        f"kubectl delete deployment --all -n {NAMESPACE} --ignore-not-found=true",
        "Suppression de tous les deployments"
    )
    
    run_command(
        f"kubectl delete statefulset postgres -n {NAMESPACE} --ignore-not-found=true",
        "Suppression du statefulset postgres"
    )
    
    print("\n>>> Attente de la suppression des pods...")
    time.sleep(10)
    
    print("\n✓ Nettoyage terminé\n")
    
    print(">>> État du namespace:")
    run_command(f"kubectl get pods -n {NAMESPACE}")

if __name__ == "__main__":
    main()
