# views/mobile_tasker.py
import flet as ft
from database.db_manager import listar_tareas_supervisor, actualizar_estado_tarea

class MobileTasker(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(route="/supervisor")
        self.page = page
        self.nombre_usuario = page.session.get("user_name")
        self.id_usuario = page.session.get("user_id")

        self.lista_tareas = ft.Column(spacing=15, scroll=ft.ScrollMode.AUTO, expand=True)

        self.controls = [
            ft.AppBar(
                title=ft.Text(f"Hola, {self.nombre_usuario}"),
                bgcolor=ft.colors.BLUE_700,
                actions=[
                    ft.IconButton(
                        icon=ft.icons.LOGOUT,
                        tooltip="Cerrar sesion",
                        icon_color=ft.colors.WHITE,
                        on_click=self.cerrar_sesion
                    )
                ]
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text("Mis Tareas", size=20, weight=ft.FontWeight.BOLD),
                    self.lista_tareas,
                ], spacing=15, expand=True),
                padding=20,
                expand=True
            ),
            ft.FloatingActionButton(icon=ft.icons.REFRESH, on_click=self.cargar_tareas)
        ]
        self.cargar_tareas(None)

    def cerrar_sesion(self, e):
        self.page.session.clear()
        self.page.go("/")

    def cargar_tareas(self, e):
        self.lista_tareas.controls.clear()
        tareas = listar_tareas_supervisor(self.id_usuario)

        if not tareas:
            self.lista_tareas.controls.append(
                ft.Text("No tenes tareas asignadas.", color=ft.colors.GREY_600)
            )

        for t in tareas:
            completada = t['estado'] == 'Completada'
            estado_color = ft.colors.GREEN_700 if completada else ft.colors.ORANGE_700

            card = ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.ListTile(
                            leading=ft.Icon(ft.icons.ASSIGNMENT, color=ft.colors.BLUE_700),
                            title=ft.Text(t['titulo'], weight=ft.FontWeight.BOLD),
                            subtitle=ft.Text(t['descripcion'] or ""),
                        ),
                        ft.Row([
                            ft.Text(f"Estado: {t['estado']}", color=estado_color, size=13),
                            ft.TextButton(
                                "Marcar como Hecho",
                                icon=ft.icons.CHECK_CIRCLE,
                                on_click=lambda _, tid=t['id']: self.completar_tarea(tid),
                                disabled=completada
                            )
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                    ]),
                    padding=10
                )
            )
            self.lista_tareas.controls.append(card)
        self.page.update()

    def completar_tarea(self, id_tarea):
        resultado = actualizar_estado_tarea(id_tarea, "Completada")
        if resultado:
            self.page.snack_bar = ft.SnackBar(ft.Text("Tarea marcada como completada"))
            self.page.snack_bar.open = True
            self.cargar_tareas(None)
        else:
            self.page.snack_bar = ft.SnackBar(ft.Text("Error al actualizar la tarea"))
            self.page.snack_bar.open = True
        self.page.update()
