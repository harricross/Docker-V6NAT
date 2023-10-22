import ipaddress
import subprocess
import random

# CONFIG
# Public /48 range
public_prefix = "2a0e:1cc0:12::1/48"
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

def create_ipset_set(public_subnets):
    # Create an ipset set to store the random IPs
    subprocess.run(["ipset", "create", "random_ips", "hash:ip", "maxelem", str(len(public_subnets))])

def add_ips_to_ipset(public_subnets):
    # Add random IPs to the ipset set
    for subnet in public_subnets:
        random_ip = random_ipv6_address(subnet)
        subprocess.run(["ipset", "add", "random_ips", str(random_ip)])

def balance_snat_traffic(public_prefix, privateV6):
    public_subnets = split_ipv6_prefix(public_prefix)
    
    with open("/proc/sys/net/ipv4/ip_local_port_range", "r") as f:
        content = f.readline()
        PORT_RANGE_START, PORT_RANGE_END = map(int, content.split())

    print(f"PORT_RANGE_START: {PORT_RANGE_START}, PORT_RANGE_END: {PORT_RANGE_END}")
    PORT_RANGE_COUNT = PORT_RANGE_END - PORT_RANGE_START + 1

    # Create an ipset set and add random IPs to it
    create_ipset_set(public_subnets)
    add_ips_to_ipset(public_subnets)

    # Iterate through local ports and apply SNAT rules
    for port_index in range(PORT_RANGE_COUNT):
        random_port = PORT_RANGE_START + port_index
        print(f"{random_port} -> SNAT from ipset set")
        
        subprocess.run(
            ["ip6tables", "-t", "nat", "-A", "POSTROUTING", "-p", "udp", "--sport", str(random_port), "-s",
             privateV6, "-m", "set", "--match-set", "random_ips", "src", "-j", "SNAT"])
        subprocess.run(
            ["ip6tables", "-t", "nat", "-A", "POSTROUTING", "-p", "tcp", "--sport", str(random_port), "-s",
             privateV6, "-m", "set", "--match-set", "random_ips", "src", "-j", "SNAT"])

if __name__ == "__main__":
    balance_snat_traffic(public_prefix, privateV6)
