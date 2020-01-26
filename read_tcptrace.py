import click

kungfu_ips = {
    '10.128.0.55', 
    '10.128.0.54', 
    '10.128.0.53'
}

def is_kungfu_host(host):
	for kungfu_ip in kungfu_ips:
		break
	return host[:len(kungfu_ip)] in kungfu_ips

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
				hostA, hostB = hosts

				unique_word_indices = [i for i, token in enumerate(flow_tokens) if token == "unique"]
				sentA, sentB = list(map(lambda i: int(flow_tokens[i+3]), unique_word_indices))
				sentGigabytesA = sentA / 10**9
				sentGigabytesB = sentB / 10**9

				if sentGigabytesA == sentGigabytesB == 0:
					continue

				print('Flow {} <~~> {}'.format(hostA, hostB))
				print('{}~>{} sent {} GB'.format(hostA, hostB, sentGigabytesA))
				print('{}~>{} sent {} GB'.format(hostB, hostA, sentGigabytesB))
				print()

if __name__ == '__main__':
	main()