
"""
This script assumes that the base directory that you're working
off of is:
~/Desktop/machine-learning-flow-sizes/
"""

# ---------------------- STEP 1: on servers
 
# clone the gpt-2-simple fork ON EACH SERVER
git clone https://github.com/amirfarhat/gpt-2-simple.git

# install python3 virtual environment
cd gpt-2-simple/
sudo apt-get install python3-venv

# create a virtual environment with tensorflow 1.13
python3 -m venv tf-1.13

# activate the virtual environment ON EACH TERMINAL WINDOW
source tf-1.13/bin/activate

# install gpt-2 requirements
pip3 install -r requirements.txt

# the requirements step will install tensorflow 1.14.0
# but we want 1.13.1, so we override the version
pip3 install tensorflow==1.13.1

# the tensorflow version should now be 1.13.1, which you
# can validate by running
pip3 show tensorflow

# now we add gpu support to tensorflow
pip3 install tensorflow-gpu==1.13.1

# and validate the version by running
pip3 show tensorflow-gpu

# install KungFu
git clone https://github.com/lsds/KungFu.git
cd KungFu
pip3 install --no-index -U .
GOBIN=$(pwd)/bin go install -v ./srcs/go/cmd/kungfu-run

# validate by running
./bin/kungfu-run -help

cd ..

# install gpt-2 requirements
pip3 install gpt-2-simple


# ---------------------- STEP 2: on servers

# make all required directories
mkdir -p cachenet_experiments/gpt2-744m
mkdir -p cachenet_experiments/gpt2-744m/iterations
mkdir -p cachenet_experiments/gpt2-744m/tcpdumps
mkdir -p cachenet_experiments/gpt2-744m/tcptraces
mkdir -p cachenet_experiments/gpt2-744m/filtered_dumps
mkdir -p cachenet_experiments/gpt2-744m/flow_pickles
mkdir -p cachenet_experiments/gpt2-744m/flow_pickles/slice
mkdir -p cachenet_experiments/gpt2-744m/flow_pickles/squeeze
mkdir -p cachenet_experiments/gpt2-744m/flow_cdfs

# transfer the models to whatever servers are missing them
gcloud compute scp --recurse kungfu-gpu-vm-v100-39:/home/ghobadi_mit_edu/gpt-2-simple/models /home/ghobadi_mit_edu/gpt-2-simple

# tcpdump command on each of the four servers
sudo /usr/sbin/tcpdump -s 150 -w gpt2_744m_iters200_vm39.pcap
sudo /usr/sbin/tcpdump -s 150 -w gpt2_744m_iters200_vm40.pcap
sudo /usr/sbin/tcpdump -s 150 -w gpt2_744m_iters200_vm41.pcap
sudo /usr/sbin/tcpdump -s 150 -w gpt2_744m_iters200_vm42.pcap

# run gpt-2 training ON EACH SERVER
# model 774M, 200 iteration steps, batch size of 2
sudo rm -r checkpoint/ ; mkdir checkpoint
KungFu/bin/kungfu-run -np 16 -H 10.128.0.51:4,10.128.0.53:4,10.128.0.54:4,10.128.0.55:4 -strategy RING -nic eth0 -logdir logs/debug python3 my_run_script.py -m 774M --steps 200 --batch-size 2

# ---------------------- STEP 3: on local machine

# get iterations
# vm 39
gcloud compute scp kungfu-gpu-vm-v100-39:~/gpt-2-simple/logs/debug/10.128.0.51.10000.stdout.log ~/Desktop/machine-learning-flow-sizes/cachenet_experiments/gpt2-744m/iterations/iterations_gpt2_vm39_10.128.0.51.10000.txt
# vm 40
gcloud compute scp kungfu-gpu-vm-v100-40:~/gpt-2-simple/logs/debug/10.128.0.53.10000.stdout.log ~/Desktop/machine-learning-flow-sizes/cachenet_experiments/gpt2-744m/iterations/iterations_gpt2_vm40_10.128.0.53.10000.txt
# vm 41
gcloud compute scp kungfu-gpu-vm-v100-41:~/gpt-2-simple/logs/debug/10.128.0.55.10000.stdout.log ~/Desktop/machine-learning-flow-sizes/cachenet_experiments/gpt2-744m/iterations/iterations_gpt2_vm41_10.128.0.55.10000.txt
# vm 42
gcloud compute scp kungfu-gpu-vm-v100-42:~/gpt-2-simple/logs/debug/10.128.0.54.10000.stdout.log ~/Desktop/machine-learning-flow-sizes/cachenet_experiments/gpt2-744m/iterations/iterations_gpt2_vm42_10.128.0.54.10000.txt

# plot iteration data, save to: figures/iterations_plot_vm{x}.png
# vm 39
python3 analyze_iterations.py -f cachenet_experiments/gpt2-744m/iterations/iterations_gpt2_vm39_10.128.0.51.10000.txt -m gpt2
# vm 40
python3 analyze_iterations.py -f cachenet_experiments/gpt2-744m/iterations/iterations_gpt2_vm40_10.128.0.53.10000.txt -m gpt2
# vm 41
python3 analyze_iterations.py -f cachenet_experiments/gpt2-744m/iterations/iterations_gpt2_vm41_10.128.0.55.10000.txt -m gpt2
# vm 42
python3 analyze_iterations.py -f cachenet_experiments/gpt2-744m/iterations/iterations_gpt2_vm42_10.128.0.54.10000.txt -m gpt2

# fetch the tcpdumps from each server
# vm 39
gcloud compute scp kungfu-gpu-vm-v100-39:~/gpt-2-simple/gpt2_744m_iters200_vm39.pcap ~/Desktop/machine-learning-flow-sizes/cachenet_experiments/gpt2-744m/tcpdumps
# vm 40
gcloud compute scp kungfu-gpu-vm-v100-40:~/gpt-2-simple/gpt2_744m_iters200_vm40.pcap ~/Desktop/machine-learning-flow-sizes/cachenet_experiments/gpt2-744m/tcpdumps
# vm 41
gcloud compute scp kungfu-gpu-vm-v100-41:~/gpt-2-simple/gpt2_744m_iters200_vm41.pcap ~/Desktop/machine-learning-flow-sizes/cachenet_experiments/gpt2-744m/tcpdumps
# vm 42
gcloud compute scp kungfu-gpu-vm-v100-42:~/gpt-2-simple/gpt2_744m_iters200_vm42.pcap ~/Desktop/machine-learning-flow-sizes/cachenet_experiments/gpt2-744m/tcpdumps


# ---------------------- STEP 4: on local machine

# run tcptrace on the dumps to get human-readable tcp flow information
tcptrace -bl cachenet_experiments/gpt2-744m/tcpdumps/gpt2_744m_iters200_vm39.pcap > cachenet_experiments/gpt2-744m/tcptraces/gpt2_744m_iters200_vm39.trace
tcptrace -bl cachenet_experiments/gpt2-744m/tcpdumps/gpt2_744m_iters200_vm40.pcap > cachenet_experiments/gpt2-744m/tcptraces/gpt2_744m_iters200_vm40.trace
tcptrace -bl cachenet_experiments/gpt2-744m/tcpdumps/gpt2_744m_iters200_vm41.pcap > cachenet_experiments/gpt2-744m/tcptraces/gpt2_744m_iters200_vm41.trace
tcptrace -bl cachenet_experiments/gpt2-744m/tcpdumps/gpt2_744m_iters200_vm42.pcap > cachenet_experiments/gpt2-744m/tcptraces/gpt2_744m_iters200_vm42.trace

# print summary of the flow size for only the flows we care about
python3 read_tcptrace.py -t cachenet_experiments/gpt2-744m/tcptraces/gpt2_744m_iters200_vm39.trace
python3 read_tcptrace.py -t cachenet_experiments/gpt2-744m/tcptraces/gpt2_744m_iters200_vm40.trace
python3 read_tcptrace.py -t cachenet_experiments/gpt2-744m/tcptraces/gpt2_744m_iters200_vm41.trace
python3 read_tcptrace.py -t cachenet_experiments/gpt2-744m/tcptraces/gpt2_744m_iters200_vm42.trace

# read the dump file to get only packet sizes
gtime tcpdump -tt -n -r cachenet_experiments/gpt2-744m/tcpdumps/gpt2_744m_iters200_vm39.pcap | awk '{print $1," ",$3," ",$5," ",$(NF-1)," ",$NF}' > cachenet_experiments/gpt2-744m/filtered_dumps/gpt2_744m_iters200_vm39.txt
gtime tcpdump -tt -n -r cachenet_experiments/gpt2-744m/tcpdumps/gpt2_744m_iters200_vm40.pcap | awk '{print $1," ",$3," ",$5," ",$(NF-1)," ",$NF}' > cachenet_experiments/gpt2-744m/filtered_dumps/gpt2_744m_iters200_vm40.txt
gtime tcpdump -tt -n -r cachenet_experiments/gpt2-744m/tcpdumps/gpt2_744m_iters200_vm41.pcap | awk '{print $1," ",$3," ",$5," ",$(NF-1)," ",$NF}' > cachenet_experiments/gpt2-744m/filtered_dumps/gpt2_744m_iters200_vm41.txt
gtime tcpdump -tt -n -r cachenet_experiments/gpt2-744m/tcpdumps/gpt2_744m_iters200_vm42.pcap | awk '{print $1," ",$3," ",$5," ",$(NF-1)," ",$NF}' > cachenet_experiments/gpt2-744m/filtered_dumps/gpt2_744m_iters200_vm42.txt


# ---------------------- STEP 5: on local machine

# observe packet timestamps relative to training iterations
python3 plot_timestamps.py -f cachenet_experiments/gpt2-744m/filtered_dumps/gpt2_744m_iters200_vm39.txt -i cachenet_experiments/gpt2-744m/iterations/iterations_gpt2_vm39_10.128.0.51.10000.txt
python3 plot_timestamps.py -f cachenet_experiments/gpt2-744m/filtered_dumps/gpt2_744m_iters200_vm40.txt -i cachenet_experiments/gpt2-744m/iterations/iterations_gpt2_vm40_10.128.0.53.10000.txt
python3 plot_timestamps.py -f cachenet_experiments/gpt2-744m/filtered_dumps/gpt2_744m_iters200_vm41.txt -i cachenet_experiments/gpt2-744m/iterations/iterations_gpt2_vm41_10.128.0.55.10000.txt
python3 plot_timestamps.py -f cachenet_experiments/gpt2-744m/filtered_dumps/gpt2_744m_iters200_vm42.txt -i cachenet_experiments/gpt2-744m/iterations/iterations_gpt2_vm42_10.128.0.54.10000.txt


# ---------------------- STEP 6: on local machine

# bin flows' packets into iterations using `slice` strategy and then pickle the flows 

# slice
python3 read_simple.py -s slice -f cachenet_experiments/gpt2-744m/filtered_dumps/gpt2_744m_iters200_vm39.txt -i cachenet_experiments/gpt2-744m/iterations/iterations_gpt2_vm39_10.128.0.51.10000.txt -o cachenet_experiments/gpt2-744m/flow_pickles/slice/gpt2_744m_iters200_vm39_flows.pickle
python3 read_simple.py -s slice -f cachenet_experiments/gpt2-744m/filtered_dumps/gpt2_744m_iters200_vm40.txt -i cachenet_experiments/gpt2-744m/iterations/iterations_gpt2_vm40_10.128.0.53.10000.txt -o cachenet_experiments/gpt2-744m/flow_pickles/slice/gpt2_744m_iters200_vm40_flows.pickle
python3 read_simple.py -s slice -f cachenet_experiments/gpt2-744m/filtered_dumps/gpt2_744m_iters200_vm41.txt -i cachenet_experiments/gpt2-744m/iterations/iterations_gpt2_vm41_10.128.0.55.10000.txt -o cachenet_experiments/gpt2-744m/flow_pickles/slice/gpt2_744m_iters200_vm41_flows.pickle
python3 read_simple.py -s slice -f cachenet_experiments/gpt2-744m/filtered_dumps/gpt2_744m_iters200_vm42.txt -i cachenet_experiments/gpt2-744m/iterations/iterations_gpt2_vm42_10.128.0.54.10000.txt -o cachenet_experiments/gpt2-744m/flow_pickles/slice/gpt2_744m_iters200_vm42_flows.pickle

# graph the sliced packets and save figures
python3 flow_cdf_plot.py -m gpt2 -f cachenet_experiments/gpt2-744m/flow_pickles/slice/gpt2_744m_iters200_vm39_flows.pickle
python3 flow_cdf_plot.py -m gpt2 -f cachenet_experiments/gpt2-744m/flow_pickles/slice/gpt2_744m_iters200_vm40_flows.pickle
python3 flow_cdf_plot.py -m gpt2 -f cachenet_experiments/gpt2-744m/flow_pickles/slice/gpt2_744m_iters200_vm41_flows.pickle
python3 flow_cdf_plot.py -m gpt2 -f cachenet_experiments/gpt2-744m/flow_pickles/slice/gpt2_744m_iters200_vm42_flows.pickle


# ---------------------- STEP 7: on local machine
# 
# make csv files of the slice flows
python3 write_flow_cdf.py -f cachenet_experiments/gpt2-744m/flow_pickles/slice/gpt2_744m_iters200_vm39_flows.pickle -o cachenet_experiments/gpt2-744m/flow_cdfs/slice_cdf_flow_size_gpt2_744m_iters200_vm39.csv
python3 write_flow_cdf.py -f cachenet_experiments/gpt2-744m/flow_pickles/slice/gpt2_744m_iters200_vm40_flows.pickle -o cachenet_experiments/gpt2-744m/flow_cdfs/slice_cdf_flow_size_gpt2_744m_iters200_vm40.csv
python3 write_flow_cdf.py -f cachenet_experiments/gpt2-744m/flow_pickles/slice/gpt2_744m_iters200_vm41_flows.pickle -o cachenet_experiments/gpt2-744m/flow_cdfs/slice_cdf_flow_size_gpt2_744m_iters200_vm41.csv
python3 write_flow_cdf.py -f cachenet_experiments/gpt2-744m/flow_pickles/slice/gpt2_744m_iters200_vm42_flows.pickle -o cachenet_experiments/gpt2-744m/flow_cdfs/slice_cdf_flow_size_gpt2_744m_iters200_vm42.csv



