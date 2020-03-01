
# -------------------------- A- CUDA & NCCL 

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

# other cuda install
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1604/x86_64/cuda-ubuntu1604.pin
sudo mv cuda-ubuntu1604.pin /etc/apt/preferences.d/cuda-repository-pin-600
sudo apt-key adv --fetch-keys http://developer.download.nvidia.com/compute/cuda/repos/ubuntu1604/x86_64/7fa2af80.pub
sudo add-apt-repository "deb http://developer.download.nvidia.com/compute/cuda/repos/ubuntu1604/x86_64/ /"
sudo apt-get update
sudo apt-get -y install cuda

# Install development and runtime libraries
sudo apt-get -y install --no-install-recommends  cuda-10-0 libcudnn7=7.4.1.5-1+cuda10.0 libcudnn7-dev=7.4.1.5-1+cuda10.0  libnccl-dev=2.4.7-1+cuda10.0 libnccl2=2.4.7-1+cuda10.0

# Add things to bashrc and source it
echo 'export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib:/usr/local/cuda-10.0/lib64:/usr/local/cuda-10.0/extras/CUPTI/lib64' >> ~/.bashrc
echo 'export PATH=/usr/local/cuda-10.0/bin${PATH:+:${PATH}}$' >> ~/.bashrc
source ~/.bashrc

# Install open mpi
sudo apt-get -y install openmpi-bin openmpi-common openssh-client openssh-server libopenmpi-dev

# -------------------------- B- Tensorflow-GPU

# Download the Anaconda Bash Script
cd /tmp
curl -O https://repo.anaconda.com/archive/Anaconda3-2019.03-Linux-x86_64.sh

# Run the script
bash Anaconda3-2019.03-Linux-x86_64.sh

# add conda to path
export PATH=~/anaconda3/bin:$PATH

# make tensorflow environment
sudo chown -R $USER $HOME
sudo ~/anaconda3/bin/conda create -p $HOME/gpu-tf tensorflow-gpu=1.13


# -------------------------- C- Horovod

# go to home and clone horovod source
cd $HOME
mkdir horovod_source
cd horovod_source
git clone --recursive https://github.com/uber/horovod.git

# init conda
conda init bash
conda init fish
conda init powershell
conda init tcsh
conda init xonsh
conda init zsh

# restart shell
exec $SHELL

# activate conda
conda activate $HOME/gpu-tf
cd horovod

# clean the folder as safe measure
python setup.py clean

# build wheel
HAVE_MPI=1 HAVE_NCCL=1 HOROVOD_NCCL_INCLUDE=/usr/include HOROVOD_NCCL_LIB=/usr/lib/x86_64-linux-gnu python setup.py bdist_wheel

# record horovod's dist
MY_HVD_WHL=$(ls dist/ | grep horovod)

# install horovod built from source 
HAVE_MPI=1 HAVE_NCCL=1 HOROVOD_NCCL_INCLUDE=/usr/include HOROVOD_NCCL_LIB=/usr/lib/x86_64-linux-gnu pip install --no-cache-dir dist/$MY_HVD_WHL


# -------------------------- D- Running tensorflow benchmarks (v1.13)

# clone and cd into benchmark repo
cd $HOME
mkdir tf_benchmark
cd tf_benchmark
git clone --single-branch --branch cnn_tf_v1.13_compatible https://github.com/tensorflow/benchmarks.git
cd benchmarks

# activate conda env
conda activate $HOME/gpu-tf

# run training locally
mpirun --oversubscribe \
		-npernode 4 \
		-H localhost \
		python scripts/tf_cnn_benchmarks/tf_cnn_benchmarks.py --model resnet101 --batch_size 64 --variable_update horovod










