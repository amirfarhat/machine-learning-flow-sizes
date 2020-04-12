

lsof /dev/nvidia*
lsof /dev/nvidia* | awk '{print $2}' | xargs -I {} kill {}




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
		-x HOROVOD_TIMELINE=timeline.json \
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
		python horovod_source/horovod/examples/tensorflow_synthetic_benchmark.py --model ResNet50 --num-iters 200 --batch-size 64 --num-warmup-batches 5 --num-batches-per-iter 1 &> out_resnet50

sudo tcpdump -s 150 -w resnet50_1.pcap





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
		-x HOROVOD_TIMELINE=timeline.json \
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
		python horovod_source/horovod/examples/tensorflow_synthetic_benchmark.py --model VGG19 --num-iters 200 --batch-size 64 --num-warmup-batches 5 --num-batches-per-iter 1 &> out_vgg19

sudo tcpdump -s 150 -w vgg19_1.pcap
















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
		-x PYTHONPATH=~/gpt-2/src \
		~/gpt-2/src/train-horovod.py --num_iters 200 --model_name 355M --batch_size 1 --dataset ~/gpt-2/shakespeare.txt &> ~/out_gpt2

sudo tcpdump -s 150 -w gpt2_1.pcap