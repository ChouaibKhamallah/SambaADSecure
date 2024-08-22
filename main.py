#!/usr/bin/python
# -*- coding: utf-8 -*-

from Functions.functions import *

with open('Configuration/ScriptSettings.json') as json_file:
  ScriptSettings = json.load(json_file)

def launch_script_process():
  start_script_message(ScriptSettings)
  user_choices = get_user_choices(ScriptSettings)

  print(f'\n{Fore.RED}{Back.WHITE}{user_choices["create_domain"]}{Style.RESET_ALL}')

  print(Style.RESET_ALL + "\nThe End!")

if __name__ == "__main__":
    launch_script_process()