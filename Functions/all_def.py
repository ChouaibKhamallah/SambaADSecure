
import json
from colorama import Fore, Back, Style
import argparse
import re
import sys
import os
from subprocess import check_output,run,call,DEVNULL,STDOUT
import netifaces
import requests
import hashlib
import apt

script_directory = os.path.dirname(os.path.abspath(sys.argv[0]))

global ScriptSettings
global SambaADRequirements
global args


with open(f'{script_directory}/Configuration/ScriptSettings.json') as json_file:
  ScriptSettings = json.load(json_file)

with open(f'{script_directory}/Configuration/SambaADRequirements.json') as json_file:
  SambaADRequirements = json.load(json_file)

parser = argparse.ArgumentParser()
parser.add_argument('--dryrun', action="store_true",dest='dryrun',help='print your choices but does not actually perform the actions',default=False)
parser.add_argument('--create-domain', action="store_true",dest='create',help='install OS prerequites and create new Active Directory domain',default=False)
parser.add_argument('--join-domain', action="store_true",dest='join',help='add a Samba AD server to existing Active Directory domain',default=False)
parser.add_argument('--debug', action="store_true",dest='debug',help='add more infos',default=False)

args = parser.parse_args()
dryrun = args.dryrun
create_domain = args.create
join_domain = args.join
debug = args.debug

class Messages:

    def start_script_message(ScriptSettings):
        print(f'{ScriptSettings["Messages"]["Welcome"]}')
        print(f'{Fore.WHITE}{parser.print_help()}\n')

    def get_user_choices(ScriptSettings):
        global user_choices 
        user_choices = {}
        for section in ScriptSettings["Questions"]:

            if "description" in ScriptSettings["Questions"][section]:
                print(f'{Fore.GREEN}{ScriptSettings["Questions"][section]["description"]}')
        
            for question in ScriptSettings["Questions"][section]["question"]:
                
                if ScriptSettings["Questions"][section]["question"][question] == ["yes","no"]:
                    while True:
                        user_input = input(f'{Fore.CYAN}{question} {Fore.WHITE}{ScriptSettings["Questions"][section]["question"][question]}: {Fore.GREEN}')
                        if user_input.lower() in ["yes", "y"]:
                            user_input = True
                            break
                        elif user_input.lower() in ["no", "n"]:
                            user_input = False
                            break
                        else:
                            print(f'{Fore.WHITE}{Back.RED}Invalid input. Please enter yes/no.{Style.RESET_ALL}')

                elif type(ScriptSettings["Questions"][section]["question"][question]) is dict:

                    print(f'ℹ️ {Fore.WHITE} {question}')

                    for option in ScriptSettings["Questions"][section]["question"][question]:
                        print(f'{Fore.CYAN}{option} {Fore.YELLOW}{ScriptSettings["Questions"][section]["question"][question][option]}')

                    while True:
                        user_input = input(f'{Fore.CYAN}Choose an option... {Fore.WHITE}{[x for x in ScriptSettings["Questions"][section]["question"][question]]}: {Fore.GREEN}')
                        if user_input in [x for x in ScriptSettings["Questions"][section]["question"][question]]:
                            break
                        else:
                            print(f'{Fore.WHITE}{Back.RED}Invalid input, Please enter valid data{Style.RESET_ALL}')

                else:
                    while True:

                        user_input = input(f'{Fore.CYAN}{question} {Fore.WHITE}{ScriptSettings["Questions"][section]["question"][question]}: {Fore.GREEN}')
                        
                        if "regex" in ScriptSettings["Questions"][section]:
                            if re.match(ScriptSettings["Questions"][section]["regex"],user_input) is not None:
                                break
                            else:
                                print(f'{Fore.WHITE}{Back.RED}Invalid input, Please enter valid data{Style.RESET_ALL}')

                        elif user_input != "":
                            break

                        else:
                            print(f'{Fore.WHITE}{Back.RED}Invalid input, Please enter valid data{Style.RESET_ALL}')

            print(f"{Style.RESET_ALL}")

            if type(user_input) is str:
                user_input = user_input.lower()

            user_choices[section] = user_input
        
        return user_choices

class System:

    def get_host_infos():

        host_infos = {}

        host_infos["ip_addresses"]          =    check_output(['hostname', '--all-ip-addresses']).decode('utf-8').split()
        host_infos["hostname"]              =    check_output(['cat', '/etc/hostname']).decode('utf-8').replace("\n","")
        host_infos["distribution"]          =    check_output(['lsb_release', '-s','-i']).decode('utf-8').replace("\n","").lower()
        host_infos["distribution_codename"] =    check_output(['lsb_release', '-s','-c']).decode('utf-8').replace("\n","")
        host_infos["distribution_release"]  =    check_output(['lsb_release', '-s','-r']).decode('utf-8').replace("\n","")

        return host_infos

    def interface_configuration(host_infos):

        while True:

            if len(host_infos["ip_addresses"]) > 0:

                print(f'ℹ️ {Fore.WHITE} IP(s) detected, please select an interface to deploy Samba-AD\n')

                for ip in host_infos["ip_addresses"]:
                    print(f'{Fore.CYAN}{host_infos["ip_addresses"].index(ip)} {Fore.YELLOW}{ip}')

                print()

                while True:
                    user_input = input(f'{Fore.CYAN}Choose an option... {Fore.WHITE}{list(range(0,len(host_infos["ip_addresses"])))}: {Fore.GREEN}')
                    if user_input in [str(x) for x in list(range(0,len(host_infos["ip_addresses"])))]:
                        break
                    else:
                        print(type(user_input))
                        print(f'{Fore.WHITE}{Back.RED}Invalid input, Please enter valid data{Style.RESET_ALL}')

                user_choices["sambaad_ip"] = host_infos['ip_addresses'][int(user_input)]
            else:
                user_choices["sambaad_ip"] = host_infos['ip_addresses'][0]

            for iface in netifaces.interfaces():
                for details in netifaces.ifaddresses(iface):
                    if netifaces.ifaddresses(iface)[details][0]['addr'] == user_choices["sambaad_ip"]:
                        user_choices["sambaad_interface"] = iface

            print(f'\n{Fore.GREEN}Selected IP: {user_choices["sambaad_ip"]}')
            print(f'{Fore.GREEN}Interface: {user_choices["sambaad_interface"]}\n')

            user_input = input(f"{Fore.CYAN}Do you confirm? {Fore.WHITE}['yes','no']: {Fore.GREEN}")
            if user_input.lower() in ["yes", "y"]:
                print(f'✅ {Fore.WHITE}SELECTED IP: {user_choices["sambaad_ip"]}')
                print(f'✅ {Fore.WHITE}INTERFACE: {user_choices["sambaad_interface"]}')
                break
            elif user_input.lower() in ["no", "n"]:
                continue
            else:
                print(f'{Fore.WHITE}{Back.RED}Invalid input. Please enter yes/no.{Style.RESET_ALL}')

        while True:
            user_input = input(f"\n{Fore.CYAN}Do you want to disable ipv6? {Fore.WHITE}['yes','no']: {Fore.GREEN}")
            if user_input.lower() in ["yes", "y"]:
                user_choices["disable_ipv6"] = True
                break
            elif user_input.lower() in ["no", "n"]:
                user_choices["disable_ipv6"] = False
                break
            else:
                print(f'{Fore.WHITE}{Back.RED}Invalid input. Please enter yes/no.{Style.RESET_ALL}')

    def disable_ipv6(configuration_file=None):

        ipv6_configuration = {  "net.ipv6.conf.all.disable_ipv6":"1",
                                "net.ipv6.conf.default.disable_ipv6":"1"
                            }

        if os.path.isfile(configuration_file):
            with open(configuration_file, "r") as config:
                data = config.readlines()
        
        for config in ipv6_configuration:
            for line in data:
                if config in line:
                    data.remove(line)

        for config in ipv6_configuration:
            data.append(f"{config}={ipv6_configuration[config]}\n")

        with open(configuration_file,"w") as config_file:
            config_file.writelines(data)

        if not dryrun:
            try:
                run(['sysctl','-p'])
                print(f'✅ {Fore.WHITE}SYSCTL FORCE RELOAD CONFIGURATION')
            except Exception as e:
                print(e)
                print(f'❌ {Fore.WHITE}SYSCTL FAILED TO FORCE RELOAD CONFIGURATION')

    def set_hostname(host_infos,ScriptSettings):

        print(f"\n{Fore.GREEN}{ScriptSettings['choices_details']['hostname']['description']}")

        for question in ScriptSettings["choices_details"]["hostname"]["question"]:
            
            while True:
                user_input = input(f"{Fore.CYAN}{question} {Fore.WHITE}{ScriptSettings['choices_details']['hostname']['question'][question]}: {Fore.GREEN}")
                if re.match(ScriptSettings["choices_details"]["hostname"]["regex"],user_input) is not None:
                    break
                else:
                    print(f'{Fore.WHITE}{Back.RED}Invalid input, Please enter valid data{Style.RESET_ALL}')
        
        user_choices["hostname"] = user_input

        if f'{user_choices["hostname"]}.{user_choices["domain_full_name"]}' != host_infos["hostname"]:

            while True:
                user_input = input(f"{Fore.CYAN}Do you want to confirm to rename server from {host_infos['hostname']} to {user_choices['hostname']}.{user_choices['domain_full_name']} ? {Fore.WHITE}['yes','no']: {Fore.GREEN}")
                if user_input.lower() in ["yes", "y"]:
                    if not dryrun:
                        print(f'✅ {Fore.WHITE}SET HOSTNAME {user_choices["hostname"]}.{user_choices["domain_full_name"]}')
                        run(['hostnamectl','set-hostname',f'{user_choices["hostname"]}.{user_choices["domain_full_name"]}'])
                        break
                elif user_input.lower() in ["no", "n"]:
                    break
                else:
                    print(f'{Fore.WHITE}{Back.RED}Invalid input. Please enter yes/no.{Style.RESET_ALL}')

    def configure_hosts_file(user_choices):

        print(f"\nℹ️ {Fore.WHITE} /ETC/HOSTS CONFIGURATION")

        with open("/etc/hosts","r") as hosts_file:
            data = hosts_file.readlines()
        
        for line in data:
            if user_choices["sambaad_ip"] in line:
                data.remove(line)
        
        data.append(f'{user_choices["sambaad_ip"]} {user_choices["hostname"]}.{user_choices["domain_full_name"]}   {user_choices["hostname"]}\n')

        with open("/etc/hosts","w") as hosts_file:
            hosts_file.writelines(data)

    def download_file(url=None,destination=None,sha256=None):

        response = requests.get(url)
        file_Path = destination
    
        if response.status_code == 200:
            with open(file_Path, 'wb') as file:
                file.write(response.content)
            print(f'✅ {Fore.WHITE}FILE DOWNLOADED {url} to {destination}')
        else:
            print(f'❌ {Fore.WHITE}Failed to download {url}')

        if sha256 is not None:
            with open(destination, "rb") as f:
                bytes = f.read()
                readable_hash = hashlib.sha256(bytes).hexdigest()

            if readable_hash == sha256:
                print(f'✅ {Fore.WHITE}HASH OK for file {destination} : {readable_hash}')
            else:
                print(f'❌ {Fore.WHITE}HASH NOT OK for file {destination}')

    def add_samba_repository(SambaADRequirements,host_infos):

        repository_url = SambaADRequirements[host_infos["distribution"]]["repository"][host_infos["distribution_codename"]]["url"]
        repository_file = gpg_key_url = SambaADRequirements[host_infos["distribution"]]["repository"]["file"]
        gpg_key_url = SambaADRequirements[host_infos["distribution"]]["repository"]["gpg_key"]
        gpg_key_file = SambaADRequirements[host_infos["distribution"]]["repository"]["gpg_key_dest"]
        gpg_key_sha256 = SambaADRequirements[host_infos["distribution"]]["repository"]["sha256"]

        if not dryrun:
            
            print(f"\nℹ️ {Fore.WHITE} DOWNLOAD REPOSITORY KEY")
            System.download_file(url=gpg_key_url,destination=gpg_key_file,sha256=gpg_key_sha256)
            
            print(f"\nℹ️ {Fore.WHITE} ADD SAMBA REPOSITORY")
            repository = f'deb [signed-by={gpg_key_file}] {repository_url}'
            with open(repository_file, "w") as repo:
                repo.write(repository)

            if os.path.isfile(repository_file):
                with open(repository_file,"r") as repo:
                    repo_line = repo.readline()

                if repo_line == repository:
                    print(f'✅ {Fore.WHITE}ADDED REPOSITORY "{repository_url}" in {repository_file}')
                else:
                    print(f'❌ {Fore.WHITE}ERROR IN REPOSITORY {repository_file}')
            else:
                print(f'❌ {Fore.WHITE}REPOSITORY NOT EXISTS {repository_file}')

            try:
                call(['apt','update'],stdout=DEVNULL,stderr=STDOUT)
                print(f'✅ {Fore.WHITE}UPDATE PACKAGES')
            except Exception as e:
                print(e)
                print(f'❌ {Fore.WHITE}FAILED TO RUN UPDATE PACKAGES')


    def install_packages(packages):

        cache = apt.Cache()
        cache.open()

        print(f"\nℹ️ {Fore.WHITE} INSTALL PACKAGES")

        for package in packages:
            if cache[package].is_installed:
              print(f'ℹ️  {Fore.WHITE}{package} already installed')
            else:
                if not dryrun:
                    call(["apt","install","-y",package],stdout=DEVNULL,stderr=STDOUT)
                print(f'✅ {Fore.WHITE}{package} freshly installed')
    
    def disable_services(services):

        print(f"\nℹ️ {Fore.WHITE} DISABLE SERVICES")

        for service in services:
            service_is_active = True
            if call(["systemctl","is-active","--quiet",service],stdout=DEVNULL,stderr=STDOUT) == 0:
                print(f"❌ {Fore.WHITE}{service} service is active")
            else:
                print(f"ℹ️ {Fore.WHITE}{service} service is inactive")
                service_is_active = False
            
            if service_is_active:
                try:
                    call(["systemctl","stop",service],stdout=DEVNULL,stderr=STDOUT)
                    print(f'✅ {Fore.WHITE}{service} service stopped')
                except Exception as e:
                    print(f'❌ {Fore.WHITE}{service} unable to stop service')

            try:
                call(["systemctl","disable",service],stdout=DEVNULL,stderr=STDOUT)
                print(f'✅ {Fore.WHITE}{service} service disabled')
            except Exception as e:
                print(f'❌ {Fore.WHITE}{service} unable to disable service')
    
    def install_samba_ad(packages):

        print(f"\nℹ️ {Fore.WHITE} SAMBA-AD PACKAGES INSTALLATION")
        run(["export","DEBIAN_FRONTEND=noninteractive"])
        System.install_packages(packages)
        run(["unset","DEBIAN_FRONTEND"])
    
    def configure_krb5_file(user_choices):

        print(f"\nℹ️ {Fore.WHITE} KRB5.CONF CONFIGURATION")

        krb5_datas = """[libdefaults]
default_realm = %s
dns_lookup_kdc = true
dns_lookup_realm = false
""" % (user_choices["domain_full_name"].upper())
        
        with open("/etc/krb5.conf", "w") as krb5_file:
            krb5_file.write(krb5_datas)


    def samba_ad_provision(user_choices):
        pass
    


