# Hướng dẫn cài đặt các công cụ khác

## 1. Cài đặt Rancher (trên 1 server riêng)

### Gán disk (ổ cứng) vào trong thư mục `/data`
```bash
sudo mkfs.ext4 -m 0 /dev/sdb

mkdir /data

echo "/dev/sdb  /data  ext4  defaults  0  0" | sudo tee -a /etc/fstab

mount -a

sudo df -h
```

### Cài đặt Docker
```bash
apt update

apt install docker.io

apt install docker-compose

docker -v && docker-compose -v
```

### File `docker-compose.yml` tạo Rancher
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

### Lấy mật khẩu Rancher
```bash
docker logs rancher-server 2>&1 | grep "Bootstrap Password:"
```

---

# Phần 2 và 3 thực hiện trên k8s-master-1, user root
## 2. Cài đặt Helm
```bash
wget https://get.helm.sh/helm-v3.17.3-linux-amd64.tar.gz

tar xvf helm-v3.17.3-linux-amd64.tar.gz

mv linux-amd64/helm /usr/bin

helm version
```

---

## 3. Cài đặt Ingress Controller
```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx

helm repo update

helm pull ingress-nginx/ingress-nginx

tar -xzf ingress-nginx-4.12.x.tgz

nano ingress-nginx/values.yaml
```

> **Chính sửa trong `values.yaml`:**
> - `type: LoadBalancer` → `type: NodePort`
> - `nodePort.http: ""` → `http: "30080"`
> - `nodePort.https: ""` → `https: "30443"`

```bash
cp -rf ingress-nginx /home/anhquan

su - anhquan

kubectl create ns ingress-nginx

helm -n ingress-nginx install ingress-nginx -f ingress-nginx/values.yaml ingress-nginx
```

---

## 4. Cấu hình NGINX server Load Balancer
### Cài đặt nginx
```sh
sudo apt install nginx -y
```
### Cập nhật port trong nginx default
```bash
nano /etc/nginx/sites-available/default
```
> Sửa `listen 80` → `listen 9999;`

### Thêm config `<name>.vn.conf`
```bash
nano /etc/nginx/conf.d/<name>.vn.conf
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


## 5. Cài đặt và cấu hình NFS Server 
### Thực hiện trên database server
```sh
sudo apt install nfs-server -y

sudo mkdir /data

sudo chown -R nobody:nogroup /data

sudo chmod -R 777 /data

sudo nano /etc/exports

/data *(rw,sync,no_subtree_check,no_root_squash)

sudo exportfs -rav

sudo systemctl restart nfs-server
```

### Cài đặt và cấu hình NFS client (Thực hiện trên cả 3 servers k8s-master-1, k8s-master-2, k8s-master-3)
```sh
sudo apt install nfs-common -y
```

---

## 6. Cài đặt Prometheus và Grafana


---

## 7. Backup hệ thống với Velero

### Docker Compose MinIO (trên `database-server`)
```yaml
version: '3'
services:
  minio:
    image: minio/minio
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

### Cài Velero client (trên k8s-master hoặc kubectl shell trong Rancher)
```bash
wget https://github.com/vmware-tanzu/velero/releases/download/v1.15.2/velero-v1.15.2-linux-amd64.tar.gz
tar -xvf velero-v1.15.2-linux-amd64.tar.gz
sudo mv velero-v1.15.2-linux-amd64/velero /usr/local/bin
```

### Cài Velero sử dụng MinIO
```bash
cat <<EOF > credentials-velero
[default]
aws_access_key_id=<access_key>
aws_secret_access_key=<secret_key>
EOF

velero install \
  --provider aws \
  --plugins velero/velero-plugin-for-aws:v1.5.2 \
  --bucket <bucket_name> \
  --secret-file ./credentials-velero \
  --use-node-agent \
  --backup-location-config region=minio,s3ForcePathStyle="true",s3Url=http://192.168.164.206:9000 \
  --namespace velero
```

