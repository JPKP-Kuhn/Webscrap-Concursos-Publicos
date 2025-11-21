#!/usr/bin/env python
import sys
import warnings

from pyrogram.raw import base

from projeto_poo.crew import ProjetoPoo

from projeto_poo.telegram_bot import bot_main

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Inicia a Crew e o bot
    """
    bot_main.main() # Inicia o bot