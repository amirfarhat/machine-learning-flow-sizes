
"""
This script assumes that the base directory that you're working
off of is:
~/Desktop/machine-learning-flow-sizes/
"""

# ---------------------- STEP 1: on servers
 
# tcpdump command on each of the four servers
sudo /usr/sbin/tcpdump -s 150 -w hvd_mobilenet_iters200_vm1.pcap
sudo /usr/sbin/tcpdump -s 150 -w hvd_mobilenet_iters200_vm2.pcap
sudo /usr/sbin/tcpdump -s 150 -w hvd_mobilenet_iters200_vm3.pcap
sudo /usr/sbin/tcpdump -s 150 -w hvd_mobilenet_iters200_vm4.pcap


# ---------------------- STEP 2: on servers

# 200 iterationss, 1 batch per iteration, 5 warmup batches
mpirun --allow-run-as-root \
		--verbose \
		--tag-output \
		--oversubscribe \
		-np 16 \
		-H gcp_ghobadi_google_mit_edu@hvd-t4-vm-1,gcp_ghobadi_google_mit_edu@hvd-t4-vm-2,gcp_ghobadi_google_mit_edu@hvd-t4-vm-3,gcp_ghobadi_google_mit_edu@hvd-t4-vm-4 \
		-bind-to none \
		-map-by slot \
		-mca pml ob1 \
		-mca btl ^openib \
		-mca btl_tcp_if_include ens8 \
		-x HOROVOD_TIMELINE=timeline_mobilenet.json \
		-x NCCL_DEBUG=INFO \
		-x NCCL_SOCKET_IFNAME=ens8 \
		-x CONDA_SHLVL \
		-x LD_LIBRARY_PATH \
		-x CONDA_EXE \
		-x SSH_CONNECTION \
		-x LANG \
		-x CONDA_PREFIX \
		-x _CE_M \
		-x XDG_SESSION_ID \
		-x USER \
		-x PWD \
		-x HOME \
		-x SSH_CLIENT \
		-x _CE_CONDA \
		-x CONDA_PROMPT_MODIFIER \
		-x SSH_TTY \
		-x MAIL \
		-x TERM \
		-x SHELL \
		-x SHLVL \
		-x LOGNAME \
		-x PATH \
		-x CONDA_DEFAULT_ENV \
		python horovod_source/horovod/examples/tensorflow_synthetic_benchmark.py --model MobileNet --num-iters 200 --batch-size 64 --num-warmup-batches 5 --num-batches-per-iter 1 &> hvd_out_mobilenet


# ---------------------- STEP 3: on servers

# terminate the tcpdump command when training ends


# ---------------------- STEP 4: on local machine

# make all required directories
mkdir -p cerberus_experiments/mobilenet
mkdir -p cerberus_experiments/mobilenet/figures
mkdir -p cerberus_experiments/mobilenet/tcpdumps
mkdir -p cerberus_experiments/mobilenet/tcptraces
mkdir -p cerberus_experiments/mobilenet/filtered_dumps
mkdir -p cerberus_experiments/mobilenet/flow_pickles
mkdir -p cerberus_experiments/mobilenet/flow_pickles/slice
mkdir -p cerberus_experiments/mobilenet/flow_pickles/squeeze
mkdir -p cerberus_experiments/mobilenet/flow_cdfs

# scp training iteration times
gcloud compute scp gcp_ghobadi_google_mit_edu@hvd-t4-vm-1:~/hvd_out_mobilenet ~/Desktop/machine-learning-flow-sizes/cerberus_experiments/mobilenet/

# scp tcpdumps to local machine
gcloud compute scp gcp_ghobadi_google_mit_edu@hvd-t4-vm-1:~/hvd_mobilenet_iters200_vm1.pcap ~/Desktop/machine-learning-flow-sizes/cerberus_experiments/mobilenet/tcpdumps &
gcloud compute scp gcp_ghobadi_google_mit_edu@hvd-t4-vm-2:~/hvd_mobilenet_iters200_vm2.pcap ~/Desktop/machine-learning-flow-sizes/cerberus_experiments/mobilenet/tcpdumps &
gcloud compute scp gcp_ghobadi_google_mit_edu@hvd-t4-vm-3:~/hvd_mobilenet_iters200_vm3.pcap ~/Desktop/machine-learning-flow-sizes/cerberus_experiments/mobilenet/tcpdumps &
gcloud compute scp gcp_ghobadi_google_mit_edu@hvd-t4-vm-4:~/hvd_mobilenet_iters200_vm4.pcap ~/Desktop/machine-learning-flow-sizes/cerberus_experiments/mobilenet/tcpdumps &

# plot iteration data, save to: figures/iterations_plot.png
python3 hvd_analyze_iterations.py -m mobilenet -f cerberus_experiments/mobilenet/hvd_out_mobilenet -o cerberus_experiments/mobilenet/flow_cdfs/cdf_iteration_durations.csv


# ---------------------- STEP 5: on local machine

# run tcptrace on the dumps to get human-readable tcp flow information
tcptrace -ln cerberus_experiments/mobilenet/tcpdumps/hvd_mobilenet_iters200_vm1.pcap > cerberus_experiments/mobilenet/tcptraces/hvd_mobilenet_iters200_vm1.trace &
tcptrace -ln cerberus_experiments/mobilenet/tcpdumps/hvd_mobilenet_iters200_vm2.pcap > cerberus_experiments/mobilenet/tcptraces/hvd_mobilenet_iters200_vm2.trace &
tcptrace -ln cerberus_experiments/mobilenet/tcpdumps/hvd_mobilenet_iters200_vm3.pcap > cerberus_experiments/mobilenet/tcptraces/hvd_mobilenet_iters200_vm3.trace &
tcptrace -ln cerberus_experiments/mobilenet/tcpdumps/hvd_mobilenet_iters200_vm4.pcap > cerberus_experiments/mobilenet/tcptraces/hvd_mobilenet_iters200_vm4.trace &

# print summary of the flow size for only the flows we care about
python3 read_tcptrace.py -t cerberus_experiments/mobilenet/tcptraces/hvd_mobilenet_iters200_vm1.trace
python3 read_tcptrace.py -t cerberus_experiments/mobilenet/tcptraces/hvd_mobilenet_iters200_vm2.trace
python3 read_tcptrace.py -t cerberus_experiments/mobilenet/tcptraces/hvd_mobilenet_iters200_vm3.trace
python3 read_tcptrace.py -t cerberus_experiments/mobilenet/tcptraces/hvd_mobilenet_iters200_vm4.trace

# read the dump file to get only packet sizes
gtime tcpdump -tt -n -r cerberus_experiments/mobilenet/tcpdumps/hvd_mobilenet_iters200_vm1.pcap | awk '{print $1," ",$3," ",$5," ",$(NF-1)," ",$NF}' > cerberus_experiments/mobilenet/filtered_dumps/hvd_mobilenet_iters200_vm1.txt &
gtime tcpdump -tt -n -r cerberus_experiments/mobilenet/tcpdumps/hvd_mobilenet_iters200_vm2.pcap | awk '{print $1," ",$3," ",$5," ",$(NF-1)," ",$NF}' > cerberus_experiments/mobilenet/filtered_dumps/hvd_mobilenet_iters200_vm2.txt &
gtime tcpdump -tt -n -r cerberus_experiments/mobilenet/tcpdumps/hvd_mobilenet_iters200_vm3.pcap | awk '{print $1," ",$3," ",$5," ",$(NF-1)," ",$NF}' > cerberus_experiments/mobilenet/filtered_dumps/hvd_mobilenet_iters200_vm3.txt & 
gtime tcpdump -tt -n -r cerberus_experiments/mobilenet/tcpdumps/hvd_mobilenet_iters200_vm4.pcap | awk '{print $1," ",$3," ",$5," ",$(NF-1)," ",$NF}' > cerberus_experiments/mobilenet/filtered_dumps/hvd_mobilenet_iters200_vm4.txt &


# ---------------------- STEP 6: on local machine

# observe packet timestamps relative to training iterations
python3 hvd_plot_timestamps.py -f cerberus_experiments/mobilenet/filtered_dumps/hvd_mobilenet_iters200_vm1.txt -i cerberus_experiments/mobilenet/hvd_out_mobilenet &
python3 hvd_plot_timestamps.py -f cerberus_experiments/mobilenet/filtered_dumps/hvd_mobilenet_iters200_vm2.txt -i cerberus_experiments/mobilenet/hvd_out_mobilenet &
python3 hvd_plot_timestamps.py -f cerberus_experiments/mobilenet/filtered_dumps/hvd_mobilenet_iters200_vm3.txt -i cerberus_experiments/mobilenet/hvd_out_mobilenet &
python3 hvd_plot_timestamps.py -f cerberus_experiments/mobilenet/filtered_dumps/hvd_mobilenet_iters200_vm4.txt -i cerberus_experiments/mobilenet/hvd_out_mobilenet &

# observe the left-side gap between the iteration start and flow data
# to decide on packet binning strategy in the next step


# ---------------------- STEP 7: on local machine

# slice
python3 hvd_read_simple.py -s slice -f cerberus_experiments/mobilenet/filtered_dumps/hvd_mobilenet_iters200_vm1.txt -i cerberus_experiments/mobilenet/hvd_out_mobilenet -o cerberus_experiments/mobilenet/flow_pickles/slice/mobilenet_iters200_vm1_flows.pickle &
python3 hvd_read_simple.py -s slice -f cerberus_experiments/mobilenet/filtered_dumps/hvd_mobilenet_iters200_vm2.txt -i cerberus_experiments/mobilenet/hvd_out_mobilenet -o cerberus_experiments/mobilenet/flow_pickles/slice/mobilenet_iters200_vm2_flows.pickle & 
python3 hvd_read_simple.py -s slice -f cerberus_experiments/mobilenet/filtered_dumps/hvd_mobilenet_iters200_vm3.txt -i cerberus_experiments/mobilenet/hvd_out_mobilenet -o cerberus_experiments/mobilenet/flow_pickles/slice/mobilenet_iters200_vm3_flows.pickle &
python3 hvd_read_simple.py -s slice -f cerberus_experiments/mobilenet/filtered_dumps/hvd_mobilenet_iters200_vm4.txt -i cerberus_experiments/mobilenet/hvd_out_mobilenet -o cerberus_experiments/mobilenet/flow_pickles/slice/mobilenet_iters200_vm4_flows.pickle &


# graph the sliced packets and save figures
python3 flow_cdf_plot.py -m mobilenet -f cerberus_experiments/mobilenet/flow_pickles/slice/mobilenet_iters200_vm1_flows.pickle & 
python3 flow_cdf_plot.py -m mobilenet -f cerberus_experiments/mobilenet/flow_pickles/slice/mobilenet_iters200_vm2_flows.pickle &
python3 flow_cdf_plot.py -m mobilenet -f cerberus_experiments/mobilenet/flow_pickles/slice/mobilenet_iters200_vm3_flows.pickle &
python3 flow_cdf_plot.py -m mobilenet -f cerberus_experiments/mobilenet/flow_pickles/slice/mobilenet_iters200_vm4_flows.pickle &


# ---------------------- STEP 8: on local machine

# make csv files of the slice flows
python3 write_flow_cdf.py -f cerberus_experiments/mobilenet/flow_pickles/slice/mobilenet_iters200_vm1_flows.pickle -o cerberus_experiments/mobilenet/flow_cdfs/slice_cdf_flow_size_mobilenet_iters200_vm1.csv &
python3 write_flow_cdf.py -f cerberus_experiments/mobilenet/flow_pickles/slice/mobilenet_iters200_vm2_flows.pickle -o cerberus_experiments/mobilenet/flow_cdfs/slice_cdf_flow_size_mobilenet_iters200_vm2.csv &
python3 write_flow_cdf.py -f cerberus_experiments/mobilenet/flow_pickles/slice/mobilenet_iters200_vm3_flows.pickle -o cerberus_experiments/mobilenet/flow_cdfs/slice_cdf_flow_size_mobilenet_iters200_vm3.csv &
python3 write_flow_cdf.py -f cerberus_experiments/mobilenet/flow_pickles/slice/mobilenet_iters200_vm4_flows.pickle -o cerberus_experiments/mobilenet/flow_cdfs/slice_cdf_flow_size_mobilenet_iters200_vm4.csv &






