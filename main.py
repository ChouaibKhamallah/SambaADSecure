#!/usr/bin/python
# -*- coding: utf-8 -*-
from Functions.all_def import *

if "__file__" in locals():
    sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

with open('Configuration/ScriptSettings.json') as json_file:
  ScriptSettings = json.load(json_file)

parser = argparse.ArgumentParser(description=ScriptSettings["Messages"]["Welcome"])
parser.add_argument('--dryrun', action=argparse.BooleanOptionalAction,dest='dryrun',help='print your choices but does not actually perform the actions',default=False)
args = parser.parse_args()

def launch_script_process():
  start_script_message(ScriptSettings)
  user_choices = get_user_choices(ScriptSettings)

  print(f'\n{Fore.RED}{Back.WHITE}{user_choices["create_domain"]}{Style.RESET_ALL}')

  

if __name__ == "__main__":

  try:
    launch_script_process()
    print(Style.RESET_ALL + "\nThe End!")
  except KeyboardInterrupt:
    print(Style.RESET_ALL + "\nInterrupted - Ctrl+C pressed")