# -------------------------- C- Horovod

sudo chown -R $USER $HOME
pip install gpustat

cd $HOME
sudo rm -r horovod_source/
sudo rm -r tf_benchmark/

# clone horovod source
mkdir horovod_source
cd horovod_source
git clone --recursive --branch v0.18.1 https://github.com/uber/horovod.git
cd horovod

# install gxx_linux
conda install -yc anaconda gxx_linux-64

echo 'export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/lib/x86_64-linux-gnu' >> ~/.bashrc ; source ~/.bashrc

# clean the folder as safe measure
python setup.py clean

# build wheel
HAVE_MPI=1 HAVE_NCCL=1 HOROVOD_NCCL_INCLUDE=/usr/include HOROVOD_NCCL_LIB=/usr/lib/x86_64-linux-gnu python setup.py bdist_wheel

# record horovod's dist
MY_HVD_WHL=$(ls dist/ | grep horovod)

# install horovod built from source 
HOROVOD_GPU_ALLREDUCE=NCCL HOROVOD_GPU_BROADCAST=NCCL HAVE_MPI=1 HAVE_NCCL=1 HOROVOD_NCCL_INCLUDE=/usr/include HOROVOD_NCCL_LIB=/usr/lib/x86_64-linux-gnu pip install --no-cache-dir dist/$MY_HVD_WHL