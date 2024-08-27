#!/usr/bin/python
# -*- coding: utf-8 -*-

from Functions.all_def import *

def launch_script_process():

  if create_domain:
    Messages.start_script_message(ScriptSettings)
    user_choices = Messages.get_user_choices(ScriptSettings)

    host_infos = System.get_host_infos()

    if dryrun:
      host_infos["distribution_codename"] = "bookworm"
      host_infos['distribution'] = "debian"

    if user_choices['create_domain']:
      System.interface_configuration(host_infos)
      System.set_hostname(host_infos,ScriptSettings)
      System.add_samba_repository(SambaADRequirements,host_infos)
  
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