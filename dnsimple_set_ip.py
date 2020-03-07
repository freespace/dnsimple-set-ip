#!/usr/bin/env python3

from requests import get

import click

from dnsimple import DNSimple

def print_records(records):
  for rec in records:
    print(f"{rec['name']:16s} {rec['type']:8s} {rec['ttl']:6d} {rec['content']}")

def create_subdomain(dns, domain, subdomain):
  print(f'Creating {subdomain}.{domain}')
  dns.add_record(domain, {
    'type': 'A',
    'name': subdomain,
    'content':get_public_ip(),
    'ttl': 60
  })

def update_subdomain(dns, domain, subdomain_record):
  print(f"Updating IP for {subdomain_record['name']}.{domain}")
  dns.update_record(domain, subdomain_record['id'], {
    'content':get_public_ip()
  })

def get_public_ip():
  ip = get('https://api.ipify.org').text
  print(f'Public IP: {ip}')
  return ip

@click.command()
@click.option('-t', '--api-token', required=True,
              help='API token')
@click.option('--list-records', is_flag=True,
              help='Instead of setting IP lists the records')
@click.option('-s', '--subdomain', required=True,
              help='Subdomain whose IP to set. Will be created if it does not exist')
@click.option('-d', '--domain', required=True,
              help='The top level domain to which the subdomain belongs to')
def main(*args, **kwargs):
  dnsimple_set_ip(*args, **kwargs)

def dnsimple_set_ip(api_token, list_records, domain, subdomain, **kwargs):
  dns = DNSimple(api_token=api_token)

  records = [x['record'] for x in dns.records(domain)]
  if list_records:
    print_records(records)
    return

  subdomain_record = None
  for rec in records:
    if subdomain == rec['name']:
      subdomain_record = rec
      break

  if subdomain_record is None:
    create_subdomain(dns, domain, subdomain)
  else:
    update_subdomain(dns, domain, subdomain_record)

if __name__ == '__main__':
  main()
