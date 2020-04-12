
# restart shell
exec $SHELL
sudo chown -R $USER $HOME

# add conda activate as a default startup to bashrc and source it
echo 'conda activate $HOME/gpu-tf' >> ~/.bashrc
source ~/.bashrc