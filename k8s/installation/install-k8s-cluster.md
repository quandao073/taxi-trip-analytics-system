# Kubernetes (K8s) Cluster Installation Guide

## Important Notes
Verify valid IP address ranges and Gateway IP before configuring server IPs to ensure internet connectivity.

### In VMware Workstation: Edit → Virtual Network Editor
![VMware Workstation](./installation_1.png)

### Select NAT network type → DHCP Settings. Valid IP ranges will be displayed
![Virtual Network Editor](./installation_2.png)

![DHCP Settings](./installation_3.png)

### Check Gateway IP: NAT Settings → Shows Subnet IP, Subnet mask, and Gateway IP
![DHCP Settings](./installation_4.png)

## 1. System Preparation

### Node Specifications

| Hostname      | OS            | IP              | RAM  | CPU Cores |
|--------------|--------------|----------------|------|-----|
| k8s-master-1 | Ubuntu 22.04 | 192.168.164.201 | 12 GB | 8   |
| k8s-master-2 | Ubuntu 22.04 | 192.168.164.202 | 12 GB | 8   |
| k8s-master-3 | Ubuntu 22.04 | 192.168.164.203 | 12 GB | 8   |

## 2. Execute on All 3 Servers
Add hosts:
```sh
sudo nano /etc/hosts
```
Configuration content:
```sh
192.168.164.201 k8s-master-1
192.168.164.202 k8s-master-2
192.168.164.203 k8s-master-3
```
Update and upgrade system:
```sh
sudo apt update -y && sudo apt upgrade -y
```
Create user *anhquan* and switch to it:
```sh
adduser anhquan

usermod -aG sudo anhquan

su anhquan

cd /home/anhquan
```
Disable swap:
```sh
sudo swapoff -a

sudo sed -i '/swap.img/s/^/#/' /etc/fstab
```
Configure kernel modules:

```sh
sudo nano /etc/modules-load.d/containerd.conf
# Add these lines:
overlay
br_netfilter
```
Load kernel modules:

```sh
sudo modprobe overlay

sudo modprobe br_netfilter
```

Configure network settings:
```sh
cat <<EOF | sudo tee /etc/sysctl.d/k8kubernetes.conf
net.bridge.bridge-nf-call-iptables  = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward                 = 1
EOF
```

Apply changes without reboot:
```sh
sudo sysctl --system
```
Install dependencies and add Docker repository:
```sh
sudo apt install -y curl gnupg2 software-properties-common apt-transport-https ca-certificates

sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmour -o /etc/apt/trusted.gpg.d/docker.gpg

sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
```
Install *containerd*:
```sh
sudo apt update -y

sudo apt install -y containerd.io
```

Configure *containerd*:
```sh
containerd config default | sudo tee /etc/containerd/config.toml >/dev/null 2>&1

sudo sed -i 's/SystemdCgroup = false/SystemdCgroup = true/g' /etc/containerd/config.toml
```
Start *containerd*:

```sh
sudo systemctl restart containerd

sudo systemctl enable containerd

sudo systemctl status containerd
```

Add Kubernetes repository:
```sh
echo "deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.30/deb/ /" | sudo tee /etc/apt/sources.list.d/kubernetes.list

curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.30/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
```
Install Kubernetes packages:
```sh
sudo apt update -y

sudo apt install -y kubelet kubeadm kubectl

sudo apt-mark hold kubelet kubeadm kubectl
```

## 3. Deploy 1 Master + 2 Workers Model
### On k8s-master-node:
```sh
sudo kubeadm init
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
kubectl apply -f https://raw.githubusercontent.com/projectcalico/calico/v3.25.0/manifests/calico.yaml
```
### On worker nodes (k8s-worker-node-1 and k8s-worker-node-2):
```sh
sudo kubeadm join 192.168.1.111:6443 --token your_token --discovery-token-ca-cert-hash your_sha
```

## Cluster Reset Command (For Reinstallation)
```sh
sudo kubeadm reset -f
sudo rm -rf /var/lib/etcd
sudo rm -rf /etc/kubernetes/manifests/*

sudo rm -rf /etc/kubernetes /var/lib/kubelet /var/lib/etcd /var/lib/cni /etc/cni
sudo systemctl restart kubelet

```
## 4. Deploy 3-Master HA Model
### On k8s-master-1:
```sh
sudo kubeadm init --control-plane-endpoint "192.168.164.201:6443" --upload-certs

mkdir -p $HOME/.kube

sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config 

sudo chown $(id -u):$(id -g) $HOME/.kube/config

kubectl apply -f https://raw.githubusercontent.com/projectcalico/calico/v3.25.0/manifests/calico.yaml
```

### On k8s-master-2 and k8s-master-3:
```sh
sudo kubeadm join 192.168.1.111:6443 --token your_token --discovery-token-ca-cert-hash your_sha --control-plane --certificate-key your_cert

mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config 
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```
### Configure All Nodes as Schedulable (Run on k8s-master-1)
```sh
kubectl taint nodes k8s-master-1 node-role.kubernetes.io/control-plane:NoSchedule-

kubectl taint nodes k8s-master-2 node-role.kubernetes.io/control-plane:NoSchedule-

kubectl taint nodes k8s-master-3 node-role.kubernetes.io/control-plane:NoSchedule-
```