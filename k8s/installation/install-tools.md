# Additional Tools Installation Guide

## 1. Install Rancher (on a dedicated server)

### Mount disk to `/data` directory
```bash
sudo mkfs.ext4 -m 0 /dev/sdb
sudo mkdir /data
echo "/dev/sdb  /data  ext4  defaults  0  0" | sudo tee -a /etc/fstab
sudo mount -a
sudo df -h
```

### Install Docker and Docker-compose
```bash
apt update

apt install docker.io

apt install docker-compose

docker -v && docker-compose -v
```

### Create Rancher using `docker-compose.yml`
```sh
mkdir /data/rancher/

cd /data/rancher/
nano docker-compose.yml
```
---
```yaml
version: '3'
services:
  rancher-server:
    image: rancher/rancher:v2.10.1
    container_name: rancher-server
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /data/rancher/data:/var/lib/rancher
    privileged: true
```

```sh
docker-compose up -d
```

### Retrieve Rancher bootstrap password
```bash
docker logs rancher-server 2>&1 | grep "Bootstrap Password:"
```

---

# Execute Part 2 and 3 on k8s-master-1 as root
```bash
sudo -i
```
## 2. Install Helm
```bash
wget https://get.helm.sh/helm-v3.17.3-linux-amd64.tar.gz

tar xvf helm-v3.17.3-linux-amd64.tar.gz

mv linux-amd64/helm /usr/bin

helm version
```

---

## 3. Install Ingress Controller
```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx

helm repo update

helm pull ingress-nginx/ingress-nginx

tar -xzf ingress-nginx-4.12.x.tgz

nano ingress-nginx/values.yaml
```
---
> **Modify in `values.yaml`:**
> - `type: LoadBalancer` → `type: NodePort`
> - `nodePort.http: ""` → `http: "30080"`
> - `nodePort.https: ""` → `https: "30443"`
---

```bash
cp -rf ingress-nginx /home/anhquan

su - anhquan

kubectl create ns ingress-nginx

helm -n ingress-nginx install ingress-nginx -f ingress-nginx/values.yaml ingress-nginx
```

---

## 4. Configure NGINX Load Balancer
### Install nginx
```sh
sudo apt install nginx -y
```
### Update default port configuration
```bash
nano /etc/nginx/sites-available/default
```
> Sửa `listen 80` → `listen 9999;`

### Add custom configuration
```bash
nano /etc/nginx/conf.d/quanda.vn.conf
```

```nginx
upstream my_servers {
    # địa chỉ của các server k8s
    server 192.168.164.201:30080;
    server 192.168.164.202:30080;
    server 192.168.164.203:30080;
}

server {
    listen 80;

    location / {
        proxy_pass http://my_servers;
        proxy_redirect off;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
systemctl restart nginx
```

---


## 5. Install and Configure NFS Server
### On nfs-server
```sh
# Install NFS server
sudo apt install nfs-server -y

# Create and mount directories
sudo mkdir /A
sudo mkdir /B

sudo mkfs.ext4 -m 0 /dev/sdb
echo "/dev/sdb  /A  ext4  defaults  0  0" | sudo tee -a /etc/fstab

sudo mkfs.ext4 -m 0 /dev/sdc
echo "/dev/sdc  /B  ext4  defaults  0  0" | sudo tee -a /etc/fstab

mount -a
sudo df -h

# Configure permissions
sudo chown -R nobody:nogroup /A
sudo chmod -R 777 /A

sudo chown -R nobody:nogroup /B
sudo chmod -R 777 /B

# Configure exports
sudo nano /etc/exports

/A *(rw,sync,no_subtree_check,no_root_squash)
/B *(rw,sync,no_subtree_check,no_root_squash)

# Apply configuration
sudo exportfs -rav
sudo systemctl restart nfs-server
```

### Install NFS client (on all k8s master nodes)
```sh
sudo apt install nfs-common -y
```

---

## 6. Install Prometheus and Grafana
### Install Prometheus (on k8s-master-1)

Add PV for Prometheus via Rancher UI: [monitoring-pv.yaml](../prometheus/monitoring-pv.yaml)
```sh
kubectl create ns monitoring

helm repo add prometheus-community https://prometheus-community.github.io/helm-charts

helm install quanda prometheus-community/kube-prometheus-stack --namespace monitoring --set prometheus.prometheusSpec.storageSpec.volumeClaimTemplate.spec.accessModes[0]=ReadWriteOnce --set prometheus.prometheusSpec.storageSpec.volumeClaimTemplate.spec.resources.requests.storage=10Gi --set prometheus.prometheusSpec.storageSpec.volumeClaimTemplate.spec.storageClassName=nfs-storage
```

Add Ingress configurations for [Prometheus](../prometheus/prometheus-ingress.yaml) and [Grafana](../prometheus/grafana-ingress.yaml)
access

---

## 7. System Backup with Velero

### Docker Compose MinIO (on `nfs-server`)
```yml
version: '3'
services:
  minio:
    image: minio/minio:RELEASE.2022-12-12T19-27-27Z
    container_name: minio
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - ./storage:/data
    environment:
      MINIO_ROOT_USER: <username>
      MINIO_ROOT_PASSWORD: <password>
    command: server --console-address ":9001" /data
```

### Install Velero client (on k8s-master or Rancher kubectl shell)
```bash
wget https://github.com/vmware-tanzu/velero/releases/download/v1.16.1/velero-v1.16.1-linux-amd64.tar.gz
tar -xvf velero-v1.16.1-linux-amd64.tar.gz
sudo mv velero-v1.16.1-linux-amd64/velero /usr/local/bin
```

### Install Velero using MinIO
```bash
cat <<EOF > credentials-velero
[default]
aws_access_key_id=<access_key>
aws_secret_access_key=<secret_key>
EOF

velero install \
  --provider aws \
  --plugins velero/velero-plugin-for-aws:v1.11.0 \
  --bucket <bucket_name> \
  --secret-file ./credentials-velero \
  --use-node-agent \
  --backup-location-config region=minio,s3ForcePathStyle="true",s3Url=http://192.168.164.206:9000 \
  --namespace velero
```

### Example: Backup `bigdata` namespace
```bash
# Create backup named `k8s-bigdata-v1`
velero backup create k8s-bigdata-v1 --include-namespaces bigdata --snapshot-volumes=false

# List all backups
velero backup get

# Restore from specific backup
velero restore create k8s-bigdata-v1 --from-backup k8s-bigdata-v1 --include-namespaces bigdata
```