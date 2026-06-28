"""
🌿 COMPLANT - Ponto de entrada para o Flet
Este arquivo é necessário para o build do APK
"""

import flet as ft
from complant_app import CompantApp

def main(page: ft.Page):
    app = CompantApp()
    app.build(page)

if __name__ == "__main__":
    ft.app(target=main)