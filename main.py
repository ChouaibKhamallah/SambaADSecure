#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
from colorama import Fore, Back, Style
from Functions import *

with open('Configuration/ScriptSettings.json') as json_file:
  ScriptSettings = json.load(json_file)

print(ScriptSettings["Messages"]["Welcome!"])