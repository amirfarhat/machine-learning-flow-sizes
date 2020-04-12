import click

kungfu_ips = {
    '10.128.0.55', 
    '10.128.0.54', 
    '10.128.0.53',
    '10.128.0.52',
    '10.128.0.51',
    'kungfu-gpu-vm-v100-39',
    'kungfu-gpu-vm-v100-40',
    'kungfu-gpu-vm-v100-41',
    'kungfu-gpu-vm-v100-42',
    'horovod-vm-t4-1',
    'horovod-vm-t4-2',
    'horovod-vm-t4-3',
    'horovod-vm-t4-4',
    'hvd-t4-vm-1',
    'hvd-t4-vm-2',
    'hvd-t4-vm-3',
    'hvd-t4-vm-4',
}

def is_kungfu_host(host):
	for kungfu_ip in kungfu_ips:
		break
	for ip in kungfu_ips:
		if host.startswith(ip):
			return True
	return False

def are_kungfu_hosts(hosts):
	return all(is_kungfu_host(host) for host in hosts)

@click.command()
@click.option(
    "-t",
    "--trace-file",
    type=str,
    required=True,
    help="trace file generated from the tcptrace"
)
def main(
    trace_file,
):
	with open(trace_file, 'r') as tf:
		flow_text = tf.read().split('================================')
		for flow_tokens in map(str.split, flow_text):
			host_word_indices = [i for i, token in enumerate(flow_tokens) if token == "host"]
			hosts = [flow_tokens[host_i+2] for host_i in host_word_indices]
			if are_kungfu_hosts(hosts):
				try: 				
					hostA, hostB = hosts

					unique_word_indices = [i for i, token in enumerate(flow_tokens) if token == "unique"]
					sentA, sentB = list(map(lambda i: int(flow_tokens[i+3]), unique_word_indices))
					sentGigabytesA = sentA / 10**9
					sentGigabytesB = sentB / 10**9

					if sentGigabytesA == sentGigabytesB == 0:
						continue

					if sentGigabytesA < 10e-3 and sentGigabytesB < 10e-3:
						continue

					print('Flow {} <~~> {}'.format(hostA, hostB))
					print('{}~>{} sent {} GB'.format(hostA, hostB, sentGigabytesA))
					print('{}~>{} sent {} GB'.format(hostB, hostA, sentGigabytesB))
					print()
				except:
					continue

if __name__ == '__main__':
	main()