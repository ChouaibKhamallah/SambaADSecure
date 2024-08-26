#!/usr/bin/python
# -*- coding: utf-8 -*-

from Functions.all_def import *

def launch_script_process():

  if init:
    start_script_message(ScriptSettings)
    user_choices = get_user_choices(ScriptSettings)

    host_infos = get_host_infos()

    if args.dryrun:
      host_infos["distribution_codename"] = "bookworm"
      host_infos['distribution'] = "debian"
      print(f"{SambaADRequirements[host_infos['distribution'].lower()]['repository'][host_infos['distribution_codename']]['url']}")

    if user_choices['create_domain']:
      interface_configuration(host_infos)
      set_hostname(host_infos,ScriptSettings)

if __name__ == "__main__":

  try:
    launch_script_process()
    print(Style.RESET_ALL + "\nThe End!")
  except KeyboardInterrupt:
    print(Style.RESET_ALL + "\nInterrupted - Ctrl+C pressed")