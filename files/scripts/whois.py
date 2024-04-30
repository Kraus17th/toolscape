import dns.resolver
import dns.exception
import ipwhois
import argparse
import ipaddress
from tabulate import tabulate

headers = ["host", "domain", "cidr", "type", "name", "description"]
data4 = {}
data6 = {}
resolved = []
notresolved = []
targets = []

def return_print(text, chars_to_clean):
    textlen = len(text)
    print(" " * chars_to_clean, end="\r")
    print(text, end="\r")
    return(textlen)

def list_get (list, i, default=None):
    try:
        return list[i]
    except IndexError:
        return default

def DnsDataUpdate(ip, domain, datadict):
    if ip not in datadict:
        datadict.update({ip: {"domains": [domain] if domain else [], "netinfo": []}})
    elif domain and domain not in datadict[ip]["domains"]:
        datadict[ip]["domains"].append(domain)

def AddToList(list, elem):
    if elem not in list:
        list.append(elem)

def ResoveTarget(target, query, datadict, tcp=False):
    try:
        results = dns.resolver.resolve(target, query, search=True, tcp=tcp)
        for ipval in results:
            DnsDataUpdate(ip=ipval.to_text(), domain=target, datadict=datadict)
            AddToList(resolved, target)
            
    except (dns.resolver.NoAnswer, dns.resolver.NoNameservers, dns.resolver.NXDOMAIN, dns.exception.Timeout):
        if target not in resolved:
            AddToList(notresolved, target)

def WhoisTarget(ip, list):
    try:
        obj = ipwhois.IPWhois(ip)
        result = obj.lookup_whois()
        list.append([result.get("asn_cidr", None), "ASN", result.get("asn", None), result.get("asn_description", None)])
        for j in result.get("nets", []):
            list.append([j.get("cidr", None), "NET", j.get("name", None), j.get("description", None)])
    except:
        list.append(["?", "?", "?"])

def MakeTable(data, table):
    ipsorted = [str(i) for i in sorted([ipaddress.ip_address(j) for j in data.keys()])]
    for ip in ipsorted:
        iter = max(len(data[ip]["domains"]), len(data[ip]["netinfo"]))
        for i in range(0, iter):
            table.append([ip if i==0 else None, 
                         list_get(data[ip]["domains"], i),
                         list_get(list_get(data[ip]["netinfo"], i, default=[]), 0),
                         list_get(list_get(data[ip]["netinfo"], i, default=[]), 1),
                         list_get(list_get(data[ip]["netinfo"], i, default=[]), 2),
                         list_get(list_get(data[ip]["netinfo"], i, default=[]), 3)]
                         )

def RunResolver(targets):
    textlen = 1
    for target in targets:
        textlen = return_print(f'Resolving {target} ...', textlen)
        ResoveTarget(target, "A", datadict=data4)
        ResoveTarget(target, "AAAA", datadict=data6)

    print(" " * textlen, end="\r")
    print("Resolve complete")

def RunWhois():
    textlen = 1
    for ip in data4.keys():
        textlen = return_print(f'Whois {ip} ...', textlen)
        WhoisTarget(ip, data4[ip]["netinfo"])

    for ip in data6.keys():
        textlen = return_print(f'Whois {ip} ...', textlen)
        WhoisTarget(ip, data6[ip]["netinfo"])

    print(" " * textlen, end="\r")
    print("Whois complete")
    print()

def ReadFiles(files):
    out = []
    for file in files:
        with open(file, encoding='utf8') as f:
            lines = f.readlines()
        out.extend([string.strip() for string in lines])
    return(out)

def IPType(ip):
    try:
        return(type(ipaddress.ip_address(ip)))
    except:
        return(None)

#############
# Старт    
parser = argparse.ArgumentParser()
parser.add_argument("--domains", nargs='*')
parser.add_argument("--domains-files", nargs='*')
parser.add_argument("--ips", nargs='*')
parser.add_argument("--ips-files", nargs='*')
parser.add_argument("--output")
args = parser.parse_args()

# Считывание доменов
if args.domains:
    targets.extend(args.domains)

if args.domains_files:
    targets.extend(ReadFiles(args.domains_files))

uniq_targets = []
for target in targets:
    if target not in uniq_targets:
        uniq_targets.append(target)

# Считывание IP
readed_ips = []
if args.ips_files:
    readed_ips.extend(ReadFiles(args.ips_files))
if args.ips:
    readed_ips.extend(args.ips)

if readed_ips:
    for ip in readed_ips:
        if IPType(ip) is ipaddress.IPv4Address:
            DnsDataUpdate(ip, None, data4)
        if IPType(ip) is ipaddress.IPv6Address:
            DnsDataUpdate(ip, None, data6)

print()
if uniq_targets:
    RunResolver(uniq_targets)
if data4 or data6:
    RunWhois()


table = []
MakeTable(data4, table)
MakeTable(data6, table)
if table:
    out_table=f'{tabulate(table, headers, tablefmt="simple")}\n\n\n'
    print(out_table, end='')
else:
    print("Nothing found\n")

if notresolved:
    out_not_resolved=f'Not resolved: {", ".join(notresolved)}\n\n\n'
    print(out_not_resolved, end='')

if args.output:
    with open(args.output, 'a', encoding="utf-8") as fp:
        fp.write(out_table)
        if notresolved: fp.write(out_not_resolved)