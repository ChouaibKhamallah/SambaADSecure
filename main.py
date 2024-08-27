#!/usr/bin/python
# -*- coding: utf-8 -*-

from Functions.all_def import *

def launch_script_process():

  Messages.start_script_message(ScriptSettings)

  if create_domain:
    user_choices = Messages.get_user_choices(ScriptSettings)

    host_infos = System.get_host_infos()

    if user_choices['create_domain']:

      System.interface_configuration(host_infos)
      
      if user_choices["disable_ipv6"]:
        System.disable_ipv6(configuration_file="/etc/sysctl.conf")

      System.set_hostname(host_infos,ScriptSettings)
      System.add_samba_repository(SambaADRequirements,host_infos)
      System.configure_hosts_file(user_choices)
      System.disable_services(SambaADRequirements[host_infos['distribution']]["services_to_disable_before_install"])
      System.install_packages(SambaADRequirements[host_infos['distribution']]["system_packages"])
      System.install_packages(SambaADRequirements[host_infos['distribution']]["samba_packages"])
      System.disable_services(SambaADRequirements[host_infos['distribution']]["services_to_disable_after_install"])
  
  if join_domain:
    pass

if __name__ == "__main__":

  try:

    launch_script_process()
    print(Style.RESET_ALL + "\nThe End!")

  except KeyboardInterrupt:

    print(Style.RESET_ALL + "\nInterrupted - Ctrl+C pressed")

  except Exception as e:

    print(f'\n{Style.RESET_ALL} {e}')
    print(Fore.RED + "\nInterrupted - Program error")
    print(Style.RESET_ALL + "")