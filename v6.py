import ipaddress
import subprocess
import random

# CONFIG
# Public /48 range
public_prefix = "2001:db8::/48"
# Private range to be SNAT'ted from
privateV6 = "fdbf:e8f7:b417:575a::/64"
# END CONFIG

def split_ipv6_prefix(prefix):
    # Convert the prefix to an IPv6 network object
    network = ipaddress.ip_network(prefix, strict=False)
    
    subnets = list(network.subnets(new_prefix=64))
    
    return subnets

def random_ipv6_address(subnet):
    # Generate a random host part within the /64 subnet
    host_part = random.randint(1, 2**64 - 1)
    
    # Combine the network address of the subnet with the random host part
    return subnet.network_address + host_part

def balance_snat_traffic(public_prefix, privateV6):
    public_subnets = split_ipv6_prefix(public_prefix)
    
    with open("/proc/sys/net/ipv4/ip_local_port_range", "r") as f:
        content = f.readline()
        PORT_RANGE_START, PORT_RANGE_END = map(int, content.split())

    print(f"PORT_RANGE_START: {PORT_RANGE_START}, PORT_RANGE_END: {PORT_RANGE_END}")
    PORT_RANGE_COUNT = PORT_RANGE_END - PORT_RANGE_START + 1
    i = 0

    for port_index in range(PORT_RANGE_COUNT):
        random_subnet = random.choice(public_subnets)
        random_ip = random_ipv6_address(random_subnet)
        random_port = PORT_RANGE_START + port_index
        print(f"{random_port} -> {random_ip}")
        
        subprocess.run(
            ["ip6tables", "-t", "nat", "-A", "POSTROUTING", "-p", "udp", "--sport", str(random_port), "-s",
             privateV6, "-j", "SNAT", "--to-source", str(random_ip)])
        subprocess.run(
            ["ip6tables", "-t", "nat", "-A", "POSTROUTING", "-p", "tcp", "--sport", str(random_port), "-s",
             privateV6, "-j", "SNAT", "--to-source", str(random_ip)])

if __name__ == "__main__":
    balance_snat_traffic(public_prefix, privateV6)
