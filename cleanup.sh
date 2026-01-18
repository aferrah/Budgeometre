kubectl delete namespace budgeometre
kubectl wait --for=delete namespace/budgeometre --timeout=120s
./deploy.sh