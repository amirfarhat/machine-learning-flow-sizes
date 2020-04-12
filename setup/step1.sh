# -------------------------- A- CUDA & NCCL 

sudo apt-get -y install vim
sudo apt-get -y install lsof
sudo apt-get -y install tcptrace
sudo apt-get -y install pssh
echo 'alias pssh=parallel-ssh' >> ~/.bashrc ; source ~/.bashrc

# add gcloud commands to path 
export PATH=$PATH:/snap/bin

# Add driver package repo
sudo add-apt-repository ppa:graphics-drivers

# Add NVIDIA package repos for cuda toolkit 10.0
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/cuda-repo-ubuntu1804_10.0.130-1_amd64.deb

# Depackage and update cuda toolkit
sudo apt-key adv --fetch-keys http://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/7fa2af80.pub
sudo dpkg -i cuda-repo-ubuntu1804_10.0.130-1_amd64.deb
sudo apt-get update

# Add NVIDIA package repos for cudnn and nccl2
wget http://developer.download.nvidia.com/compute/machine-learning/repos/ubuntu1804/x86_64/nvidia-machine-learning-repo-ubuntu1804_1.0.0-1_amd64.deb
sudo apt install ./nvidia-machine-learning-repo-ubuntu1804_1.0.0-1_amd64.deb
sudo apt-get update

# Install development and runtime libraries
sudo apt-get -y install --no-install-recommends  cuda-10-0 libcudnn7=7.4.1.5-1+cuda10.0 libcudnn7-dev=7.4.1.5-1+cuda10.0  libnccl-dev=2.4.7-1+cuda10.0 libnccl2=2.4.7-1+cuda10.0

# Add things to bashrc and source it
echo 'export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib:/usr/local/cuda-10.0/lib64:/usr/local/cuda-10.0/extras/CUPTI/lib64' >> ~/.bashrc
echo 'export PATH=/usr/local/cuda-10.0/bin${PATH:+:${PATH}}$' >> ~/.bashrc
source ~/.bashrc

# Install open mpi
sudo apt-get -y install openmpi-bin openmpi-common openssh-client openssh-server libopenmpi-dev

# -------------------------- B- CONDA

# Download the Anaconda Bash Script
cd /tmp
curl -O https://repo.anaconda.com/archive/Anaconda3-2019.03-Linux-x86_64.sh

# Run the script
bash Anaconda3-2019.03-Linux-x86_64.sh

# add conda to path
export PATH=~/anaconda3/bin:$PATH

# make tensorflow environment
sudo chown -R $USER $HOME
sudo ~/anaconda3/bin/conda create -p $HOME/gpu-tf tensorflow-gpu=1.13 keras

# add conda activate as a default startup to bashrc and source it
echo 'conda activate $HOME/gpu-tf' >> ~/.bashrc
source ~/.bashrc