# views/login_view.py
import flet as ft
from database.db_manager import obtener_usuarios

class LoginView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(
            route="/",
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            vertical_alignment=ft.MainAxisAlignment.CENTER,
        )
        self.page = page
        
        self.email_input = ft.TextField(label="Correo Electronico", width=300)
        self.controls = [
            ft.Text("TACTICAL TASKER", size=30, weight=ft.FontWeight.BOLD),
            self.email_input,
            ft.ElevatedButton("Entrar", on_click=self.intentar_login, width=300)
        ]

    def intentar_login(self, e):
        usuarios = obtener_usuarios()
        usuario_encontrado = next((u for u in usuarios if u['email'] == self.email_input.value), None)

        if usuario_encontrado:
            self.page.session.set("user_id", usuario_encontrado['id'])
            self.page.session.set("user_name", usuario_encontrado['nombre'])
            self.page.session.set("user_role", usuario_encontrado['rol'])

            # Redireccion por Rol
            if usuario_encontrado['rol'] == 'Gerente':
                self.page.go("/gerente")
            elif usuario_encontrado['rol'] == 'Admin':
                self.page.go("/admin")
            elif usuario_encontrado['rol'] == 'Supervisor':
                self.page.go("/supervisor")
        else:
            self.page.snack_bar = ft.SnackBar(ft.Text("Usuario no encontrado"))
            self.page.snack_bar.open = True
            self.page.update()