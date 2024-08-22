
import json
from colorama import Fore, Back, Style
import argparse

def start_script_message(ScriptSettings):


    print(f'{Fore.WHITE}{ScriptSettings["Messages"]["Welcome"]}')

def get_user_choices(ScriptSettings):

    user_choices = {}

    for section in ScriptSettings["Questions"]:
    
        for question in ScriptSettings["Questions"][section]:
            
            if ScriptSettings["Questions"][section][question] == ["yes","no"]:
                while True:
                    user_input = input(f'{Fore.CYAN}{question} {Fore.WHITE}{ScriptSettings["Questions"][section][question]}: {Fore.GREEN}')
                    if user_input.lower() in ["yes", "y"]:
                        user_input = True
                        break
                    elif user_input.lower() in ["no", "n"]:
                        user_input = False
                        break
                    else:
                        print("Invalid input. Please enter yes/no.")

            elif type(ScriptSettings["Questions"][section][question]) is dict:

                print(f'{Fore.WHITE}{question}')

                for option in ScriptSettings["Questions"][section][question]:
                    print(f'{Fore.CYAN}{option} {Fore.YELLOW}{ScriptSettings["Questions"][section][question][option]}')

                while True:
                    user_input = input(f'{Fore.CYAN}Choose an option... {Fore.WHITE}{[x for x in ScriptSettings["Questions"][section][question]]}: {Fore.GREEN}')
                    if user_input in [x for x in ScriptSettings["Questions"][section][question]]:
                        break
                    else:
                        print("Invalid input, Please enter valid data")

            else:
                while True:
                    user_input = input(f'{Fore.CYAN}{question} {Fore.WHITE}{ScriptSettings["Questions"][section][question]}: {Fore.GREEN}')
                    if not user_input == "":
                        break
                    else:
                        print("Invalid input, Please enter valid data")

        user_choices[section] = user_input
    
    return user_choices

def help():
    pass