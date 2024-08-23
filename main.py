#!/usr/bin/python
# -*- coding: utf-8 -*-
from Functions.all_def import *

script_directory = os.path.dirname(os.path.abspath(sys.argv[0]))

with open(f'{script_directory}/Configuration/ScriptSettings.json') as json_file:
  ScriptSettings = json.load(json_file)

with open(f'{script_directory}/Configuration/SambaADRequirements.json') as json_file:
  SambaADRequirements = json.load(json_file)

parser = argparse.ArgumentParser(description=ScriptSettings["Messages"]["Welcome"])
parser.add_argument('--dryrun', action=argparse.BooleanOptionalAction,dest='dryrun',help='print your choices but does not actually perform the actions',default=False)
args = parser.parse_args()

def launch_script_process():
  start_script_message(ScriptSettings)
  #user_choices = get_user_choices(ScriptSettings)

  host_infos = get_host_infos()

  print(host_infos["distribution_codename"])
  print(f"{SambaADRequirements[host_infos['distribution'].lower()]['samba_repository'][host_infos['distribution_codename']]['repository_url']}")


if __name__ == "__main__":

  try:
    launch_script_process()
    print(Style.RESET_ALL + "\nThe End!")
  except KeyboardInterrupt:
    print(Style.RESET_ALL + "\nInterrupted - Ctrl+C pressed")