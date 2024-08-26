
import json
from colorama import Fore, Back, Style
import argparse
import re
import sys
import os
from subprocess import check_output,run
import netifaces
import requests
import hashlib

script_directory = os.path.dirname(os.path.abspath(sys.argv[0]))

global ScriptSettings
global SambaADRequirements
global args


with open(f'{script_directory}/Configuration/ScriptSettings.json') as json_file:
  ScriptSettings = json.load(json_file)

with open(f'{script_directory}/Configuration/SambaADRequirements.json') as json_file:
  SambaADRequirements = json.load(json_file)

parser = argparse.ArgumentParser(description=ScriptSettings["Messages"]["Welcome"])
parser.add_argument('--dryrun', action=argparse.BooleanOptionalAction,dest='dryrun',help='print your choices but does not actually perform the actions',default=False)
parser.add_argument('--init-install', action=argparse.BooleanOptionalAction,dest='init',help='initiate the script for install OS prerequites before install Samba-AD',default=False)
parser.add_argument('--debug', action=argparse.BooleanOptionalAction,dest='debug',help='add more infos',default=False)

args = parser.parse_args()

dryrun = args.dryrun
init = args.init
debug = args.debug

def question_yes_no():
    pass

def start_script_message(ScriptSettings):
    print(f'{Fore.WHITE}{ScriptSettings["Messages"]["Welcome"]}')

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

                print(f'{Fore.WHITE}{question}')

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
        user_choices[section] = user_input
    
    return user_choices

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

            print(f'{Fore.WHITE}Multiple ips detected, please select an interface to deploy Samba-AD\n')

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
            break
        elif user_input.lower() in ["no", "n"]:
            continue
        else:
            print(f'{Fore.WHITE}{Back.RED}Invalid input. Please enter yes/no.{Style.RESET_ALL}')

    while True:
        user_input = input(f"{Fore.CYAN}Do you want to disable ipv6? {Fore.WHITE}['yes','no']: {Fore.GREEN}")
        if user_input.lower() in ["yes", "y"]:
            user_choices["disable_ipv6"] = True
            break
        elif user_input.lower() in ["no", "n"]:
            user_choices["disable_ipv6"] = False
            break
        else:
            print(f'{Fore.WHITE}{Back.RED}Invalid input. Please enter yes/no.{Style.RESET_ALL}')

def disable_ipv6():
    pass

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

        print(f'SET HOSTNAME {user_choices["hostname"]}.{user_choices["domain_full_name"]}')

        while True:
            user_input = input(f"{Fore.CYAN}Do you want to confirm to rename server from {host_infos['hostname']} to {user_choices['hostname']}.{user_choices['domain_full_name']} ? {Fore.WHITE}['yes','no']: {Fore.GREEN}")
            if user_input.lower() in ["yes", "y"]:
                if not dryrun:
                    run(['hostnamectl','set-hostname',f'{user_choices["hostname"]}.{user_choices["domain_full_name"]}'])
                    break
            elif user_input.lower() in ["no", "n"]:
                break
            else:
                print(f'{Fore.WHITE}{Back.RED}Invalid input. Please enter yes/no.{Style.RESET_ALL}')

def download_file(url=None,destination=None,sha256=None):

    response = requests.get(url)
    file_Path = destination
 
    if response.status_code == 200:
        with open(file_Path, 'wb') as file:
            file.write(response.content)
        print(f'File {destination} downloaded successfully')
    else:
        print('Failed to download {url}')

    if sha256 is not None:
        with open(destination, "rb") as f:
            bytes = f.read()
            readable_hash = hashlib.sha256(bytes).hexdigest()

        if readable_hash == sha256:
            print(f'HASH OK : {readable_hash}')
        else:
            print(f'NOT OK')

def add_samba_repository(SambaADRequirements,host_infos):

    repository_url = SambaADRequirements[host_infos["distribution"]]["repository"][host_infos["distribution_codename"]]["url"]
    gpg_key_url = SambaADRequirements[host_infos["distribution"]]["repository"]["gpg_key"]
    gpg_key_file = SambaADRequirements[host_infos["distribution"]]["repository"]["gpg_key_dest"]
    gpg_key_sha256 = SambaADRequirements[host_infos["distribution"]]["repository"]["sha256"]

    download_file(  url=gpg_key_url,
                    destination=gpg_key_file,
                    sha256=gpg_key_sha256
                )
    
    run(f'echo "deb [signed-by={gpg_key_file}] {repository_url}" > /etc/apt/sources.list.d/tissamba.list')


