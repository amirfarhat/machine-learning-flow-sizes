
"""
This script assumes that the base directory that you're working
off of is:
~/Desktop/machine-learning-flow-sizes/
"""

# ---------------------- STEP 1: on servers
 
# tcpdump command on each of the four servers
sudo /usr/sbin/tcpdump -s 150 -w vgg19_iters200_vm39.pcap
sudo /usr/sbin/tcpdump -s 150 -w vgg19_iters200_vm40.pcap
sudo /usr/sbin/tcpdump -s 150 -w vgg19_iters200_vm41.pcap
sudo /usr/sbin/tcpdump -s 150 -w vgg19_iters200_vm42.pcap


# ---------------------- STEP 2: on servers

# 200 iterationss, 1 batch per iteration, 0 warmup batches
kungfu-run -np 16 -H 10.128.0.55:4,10.128.0.54:4,10.128.0.53:4,10.128.0.51:4 -strategy RING -nic eth0 -logdir logs/debug python benchmarks/system/benchmark_kungfu_tf2.py --model VGG19 --num-iters 200 --num-batches-per-iter 1 --num-warmup-batches 0


# ---------------------- STEP 3: on servers

# terminate the tcpdump command when training ends


# ---------------------- STEP 4: on local machine

# make all required directories
mkdir -p cachenet_experiments/vgg19
mkdir -p cachenet_experiments/vgg19/tcpdumps
mkdir -p cachenet_experiments/vgg19/tcptraces
mkdir -p cachenet_experiments/vgg19/filtered_dumps
mkdir -p cachenet_experiments/vgg19/flow_pickles
mkdir -p cachenet_experiments/vgg19/flow_pickles/slice
mkdir -p cachenet_experiments/vgg19/flow_pickles/squeeze
mkdir -p cachenet_experiments/vgg19/flow_cdfs

# scp training iteration times
gcloud compute scp kungfu-gpu-vm-v100-41:~/src/KungFu/iterations_vgg19_iters200.txt ~/Desktop/machine-learning-flow-sizes/cachenet_experiments/vgg19/

# scp tcpdumps to local machine
gcloud compute scp kungfu-gpu-vm-v100-39:~/src/KungFu/vgg19_iters200_vm39.pcap ~/Desktop/machine-learning-flow-sizes/cachenet_experiments/vgg19/tcpdumps
gcloud compute scp kungfu-gpu-vm-v100-40:~/src/KungFu/vgg19_iters200_vm40.pcap ~/Desktop/machine-learning-flow-sizes/cachenet_experiments/vgg19/tcpdumps
gcloud compute scp kungfu-gpu-vm-v100-41:~/src/KungFu/vgg19_iters200_vm41.pcap ~/Desktop/machine-learning-flow-sizes/cachenet_experiments/vgg19/tcpdumps
gcloud compute scp kungfu-gpu-vm-v100-42:~/src/KungFu/vgg19_iters200_vm42.pcap ~/Desktop/machine-learning-flow-sizes/cachenet_experiments/vgg19/tcpdumps

# plot iteration data, save to: figures/iterations_plot.png
python3 analyze_iterations.py -f cachenet_experiments/vgg19/iterations_vgg19_iters200.txt -m vgg19


# ---------------------- STEP 5: on local machine

# run tcptrace on the dumps to get human-readable tcp flow information
tcptrace -bl cachenet_experiments/vgg19/tcpdumps/vgg19_iters200_vm39.pcap > cachenet_experiments/vgg19/tcptraces/vgg19_iters200_vm39.trace
tcptrace -bl cachenet_experiments/vgg19/tcpdumps/vgg19_iters200_vm40.pcap > cachenet_experiments/vgg19/tcptraces/vgg19_iters200_vm40.trace
tcptrace -bl cachenet_experiments/vgg19/tcpdumps/vgg19_iters200_vm41.pcap > cachenet_experiments/vgg19/tcptraces/vgg19_iters200_vm41.trace
tcptrace -bl cachenet_experiments/vgg19/tcpdumps/vgg19_iters200_vm42.pcap > cachenet_experiments/vgg19/tcptraces/vgg19_iters200_vm42.trace

# print summary of the flow size for only the flows we care about
python3 read_tcptrace.py -t cachenet_experiments/vgg19/tcptraces/vgg19_iters200_vm39.trace
python3 read_tcptrace.py -t cachenet_experiments/vgg19/tcptraces/vgg19_iters200_vm40.trace
python3 read_tcptrace.py -t cachenet_experiments/vgg19/tcptraces/vgg19_iters200_vm41.trace
python3 read_tcptrace.py -t cachenet_experiments/vgg19/tcptraces/vgg19_iters200_vm42

# read the dump file to get only packet sizes
gtime tcpdump -tt -n -r cachenet_experiments/vgg19/tcpdumps/vgg19_iters200_vm39.pcap | awk '{print $1," ",$3," ",$5," ",$(NF-1)," ",$NF}' > cachenet_experiments/vgg19/filtered_dumps/vgg19_iters200_vm39.txt
gtime tcpdump -tt -n -r cachenet_experiments/vgg19/tcpdumps/vgg19_iters200_vm40.pcap | awk '{print $1," ",$3," ",$5," ",$(NF-1)," ",$NF}' > cachenet_experiments/vgg19/filtered_dumps/vgg19_iters200_vm40.txt
gtime tcpdump -tt -n -r cachenet_experiments/vgg19/tcpdumps/vgg19_iters200_vm41.pcap | awk '{print $1," ",$3," ",$5," ",$(NF-1)," ",$NF}' > cachenet_experiments/vgg19/filtered_dumps/vgg19_iters200_vm41.txt
gtime tcpdump -tt -n -r cachenet_experiments/vgg19/tcpdumps/vgg19_iters200_vm42.pcap | awk '{print $1," ",$3," ",$5," ",$(NF-1)," ",$NF}' > cachenet_experiments/vgg19/filtered_dumps/vgg19_iters200_vm42.txt


# ---------------------- STEP 6: on local machine

# observe packet timestamps relative to training iterations
python3 plot_timestamps.py -f cachenet_experiments/vgg19/filtered_dumps/vgg19_iters200_vm39.txt -i cachenet_experiments/vgg19/iterations_vgg19_iters200.txt
python3 plot_timestamps.py -f cachenet_experiments/vgg19/filtered_dumps/vgg19_iters200_vm40.txt -i cachenet_experiments/vgg19/iterations_vgg19_iters200.txt
python3 plot_timestamps.py -f cachenet_experiments/vgg19/filtered_dumps/vgg19_iters200_vm41.txt -i cachenet_experiments/vgg19/iterations_vgg19_iters200.txt
python3 plot_timestamps.py -f cachenet_experiments/vgg19/filtered_dumps/vgg19_iters200_vm42.txt -i cachenet_experiments/vgg19/iterations_vgg19_iters200.txt

# observe the left-side gap between the iteration start and flow data
# to decide on packet binning strategy in the next step


# ---------------------- STEP 7: on local machine

# bin flows' packets into iterations using and `slice` or `squeeze` strategy and then pickle the flows 

# slice
python3 read_simple.py -s slice -f cachenet_experiments/vgg19/filtered_dumps/vgg19_iters200_vm39.txt -i cachenet_experiments/vgg19/iterations_vgg19_iters200.txt -o cachenet_experiments/vgg19/flow_pickles/slice/vgg19_iters200_vm39_flows.pickle
python3 read_simple.py -s slice -f cachenet_experiments/vgg19/filtered_dumps/vgg19_iters200_vm40.txt -i cachenet_experiments/vgg19/iterations_vgg19_iters200.txt -o cachenet_experiments/vgg19/flow_pickles/slice/vgg19_iters200_vm40_flows.pickle
python3 read_simple.py -s slice -f cachenet_experiments/vgg19/filtered_dumps/vgg19_iters200_vm41.txt -i cachenet_experiments/vgg19/iterations_vgg19_iters200.txt -o cachenet_experiments/vgg19/flow_pickles/slice/vgg19_iters200_vm41_flows.pickle
python3 read_simple.py -s slice -f cachenet_experiments/vgg19/filtered_dumps/vgg19_iters200_vm42.txt -i cachenet_experiments/vgg19/iterations_vgg19_iters200.txt -o cachenet_experiments/vgg19/flow_pickles/slice/vgg19_iters200_vm42_flows.pickle

# graph the sliced packets and save figures
python3 flow_cdf_plot.py -m vgg19 -f cachenet_experiments/vgg19/flow_pickles/slice/vgg19_iters200_vm39_flows.pickle
python3 flow_cdf_plot.py -m vgg19 -f cachenet_experiments/vgg19/flow_pickles/slice/vgg19_iters200_vm40_flows.pickle
python3 flow_cdf_plot.py -m vgg19 -f cachenet_experiments/vgg19/flow_pickles/slice/vgg19_iters200_vm41_flows.pickle
python3 flow_cdf_plot.py -m vgg19 -f cachenet_experiments/vgg19/flow_pickles/slice/vgg19_iters200_vm42_flows.pickle

# squeeze
python3 read_simple.py -s squeeze -f cachenet_experiments/vgg19/filtered_dumps/vgg19_iters200_vm39.txt -i cachenet_experiments/vgg19/iterations_vgg19_iters200.txt -o cachenet_experiments/vgg19/flow_pickles/squeeze/vgg19_iters200_vm39_flows.pickle
python3 read_simple.py -s squeeze -f cachenet_experiments/vgg19/filtered_dumps/vgg19_iters200_vm40.txt -i cachenet_experiments/vgg19/iterations_vgg19_iters200.txt -o cachenet_experiments/vgg19/flow_pickles/squeeze/vgg19_iters200_vm40_flows.pickle
python3 read_simple.py -s squeeze -f cachenet_experiments/vgg19/filtered_dumps/vgg19_iters200_vm41.txt -i cachenet_experiments/vgg19/iterations_vgg19_iters200.txt -o cachenet_experiments/vgg19/flow_pickles/squeeze/vgg19_iters200_vm41_flows.pickle
python3 read_simple.py -s squeeze -f cachenet_experiments/vgg19/filtered_dumps/vgg19_iters200_vm42.txt -i cachenet_experiments/vgg19/iterations_vgg19_iters200.txt -o cachenet_experiments/vgg19/flow_pickles/squeeze/vgg19_iters200_vm42_flows.pickle

# graph the sliced packets and save figures
python3 flow_cdf_plot.py -m vgg19 -f cachenet_experiments/vgg19/flow_pickles/squeeze/vgg19_iters200_vm39_flows.pickle
python3 flow_cdf_plot.py -m vgg19 -f cachenet_experiments/vgg19/flow_pickles/squeeze/vgg19_iters200_vm40_flows.pickle
python3 flow_cdf_plot.py -m vgg19 -f cachenet_experiments/vgg19/flow_pickles/squeeze/vgg19_iters200_vm41_flows.pickle
python3 flow_cdf_plot.py -m vgg19 -f cachenet_experiments/vgg19/flow_pickles/squeeze/vgg19_iters200_vm42_flows.pickle


# ---------------------- STEP 8: on local machine

# make csv files of the slice flows
python3 write_flow_cdf.py -f cachenet_experiments/vgg19/flow_pickles/slice/vgg19_iters200_vm39_flows.pickle -o cachenet_experiments/vgg19/flow_cdfs/slice_cdf_flow_size_vgg19_iters200_vm39.csv
python3 write_flow_cdf.py -f cachenet_experiments/vgg19/flow_pickles/slice/vgg19_iters200_vm40_flows.pickle -o cachenet_experiments/vgg19/flow_cdfs/slice_cdf_flow_size_vgg19_iters200_vm40.csv
python3 write_flow_cdf.py -f cachenet_experiments/vgg19/flow_pickles/slice/vgg19_iters200_vm41_flows.pickle -o cachenet_experiments/vgg19/flow_cdfs/slice_cdf_flow_size_vgg19_iters200_vm41.csv
python3 write_flow_cdf.py -f cachenet_experiments/vgg19/flow_pickles/slice/vgg19_iters200_vm42_flows.pickle -o cachenet_experiments/vgg19/flow_cdfs/slice_cdf_flow_size_vgg19_iters200_vm42.csv

# make csv files of the squeeze flows
python3 write_flow_cdf.py -f cachenet_experiments/vgg19/flow_pickles/squeeze/vgg19_iters200_vm39_flows.pickle -o cachenet_experiments/vgg19/flow_cdfs/squeeze_cdf_flow_size_vgg19_iters200_vm39.csv
python3 write_flow_cdf.py -f cachenet_experiments/vgg19/flow_pickles/squeeze/vgg19_iters200_vm40_flows.pickle -o cachenet_experiments/vgg19/flow_cdfs/squeeze_cdf_flow_size_vgg19_iters200_vm40.csv
python3 write_flow_cdf.py -f cachenet_experiments/vgg19/flow_pickles/squeeze/vgg19_iters200_vm41_flows.pickle -o cachenet_experiments/vgg19/flow_cdfs/squeeze_cdf_flow_size_vgg19_iters200_vm41.csv
python3 write_flow_cdf.py -f cachenet_experiments/vgg19/flow_pickles/squeeze/vgg19_iters200_vm42_flows.pickle -o cachenet_experiments/vgg19/flow_cdfs/squeeze_cdf_flow_size_vgg19_iters200_vm42.csv






