
import json
from colorama import Fore, Back, Style
import argparse
import re

def start_script_message(ScriptSettings):


    print(f'{Fore.WHITE}{ScriptSettings["Messages"]["Welcome"]}')

def get_user_choices(ScriptSettings):

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
                        if ScriptSettings["Questions"][section]["regex_validation"] == "contains":
                            if re.search(ScriptSettings["Questions"][section]["regex"],user_input):
                                break
                        if ScriptSettings["Questions"][section]["regex_validation"] == "notcontains":
                            if not re.search(ScriptSettings["Questions"][section]["regex"],user_input):
                                break
                    elif not user_input == "":
                        break
                    else:
                        print(f'{Fore.WHITE}{Back.RED}Invalid input, Please enter valid data{Style.RESET_ALL}')
                        

        user_choices[section] = user_input
    
    return user_choices

def help():
    pass