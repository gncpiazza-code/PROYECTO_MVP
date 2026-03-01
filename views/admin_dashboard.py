import flet as ft
from database.db_manager import obtener_usuarios, crear_nueva_tarea, listar_todas_tareas
from services.telegram_notifier import enviar_notificacion_tarea

class AdminDashboard(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(route="/admin", scroll=ft.ScrollMode.AUTO)
        self.page = page
        self.usuarios_sistema = []

        # Elementos del Formulario
        self.txt_titulo = ft.TextField(
            label="Titulo de la Tarea",
            expand=True,
            border_color=ft.colors.BLUE_700
        )
        self.txt_desc = ft.TextField(
            label="Descripcion",
            expand=True,
            multiline=True,
            min_lines=1,
            max_lines=3,
            border_color=ft.colors.BLUE_700
        )
        self.dd_asignar = ft.Dropdown(
            label="Asignar a",
            expand=True,
            border_color=ft.colors.BLUE_700
        )

        # Tabla de seguimiento
        self.tabla_tareas = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Titulo", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Asignado a", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Estado", weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
            border=ft.border.all(1, ft.colors.BLUE_GREY_200),
            border_radius=8,
        )

        self.controls = [
            ft.AppBar(
                title=ft.Text("Panel de Administracion - Tactical Tasker"),
                bgcolor=ft.colors.BLUE_GREY_800,
                color=ft.colors.WHITE,
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
                    ft.Text("Crear Nueva Tarea", size=24, weight=ft.FontWeight.BOLD),
                    ft.Row([self.txt_titulo, self.dd_asignar], spacing=10),
                    self.txt_desc,
                    ft.ElevatedButton(
                        text="Guardar y Asignar Tarea",
                        icon=ft.icons.SAVE,
                        on_click=self.guardar_tarea,
                        bgcolor=ft.colors.BLUE_700,
                        color=ft.colors.WHITE,
                        height=50
                    ),
                    ft.Divider(height=40, thickness=2),
                    ft.Row([
                        ft.Text("Seguimiento de Tareas", size=24, weight=ft.FontWeight.BOLD),
                        ft.IconButton(
                            icon=ft.icons.REFRESH,
                            tooltip="Actualizar",
                            on_click=self.cargar_tareas
                        )
                    ]),
                    self.tabla_tareas,
                ], spacing=20),
                padding=30,
                expand=True
            )
        ]
        self.cargar_datos_iniciales()

    def cerrar_sesion(self, e):
        self.page.session.clear()
        self.page.go("/")

    def cargar_datos_iniciales(self):
        try:
            self.usuarios_sistema = obtener_usuarios()
            self.dd_asignar.options = []
            for u in self.usuarios_sistema:
                self.dd_asignar.options.append(
                    ft.dropdown.Option(key=str(u['id']), text=f"{u['nombre']} ({u['rol']})")
                )
        except Exception as e:
            print(f"Error cargando usuarios: {e}")
        self.cargar_tareas(None)

    def cargar_tareas(self, e):
        tareas = listar_todas_tareas()
        mapa_usuarios = {u['id']: u['nombre'] for u in self.usuarios_sistema}

        self.tabla_tareas.rows = []
        for t in tareas:
            nombre_asignado = mapa_usuarios.get(t['id_asignado'], f"ID {t['id_asignado']}")
            completada = t['estado'] == 'Completada'
            estado_color = ft.colors.GREEN_700 if completada else ft.colors.ORANGE_700
            self.tabla_tareas.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(t['titulo'])),
                    ft.DataCell(ft.Text(nombre_asignado)),
                    ft.DataCell(ft.Text(t['estado'], color=estado_color)),
                ])
            )
        self.page.update()

    def guardar_tarea(self, e):
        if not self.txt_titulo.value or not self.dd_asignar.value:
            self.page.snack_bar = ft.SnackBar(ft.Text("Error: El titulo y el asignado son obligatorios"))
            self.page.snack_bar.open = True
        else:
            id_admin = self.page.session.get("user_id")
            id_asignado = int(self.dd_asignar.value)
            resultado = crear_nueva_tarea(
                self.txt_titulo.value,
                self.txt_desc.value,
                id_asignado,
                id_admin
            )

            if resultado:
                # Notificar por Telegram si el supervisor tiene ID configurado
                supervisor = next((u for u in self.usuarios_sistema if u['id'] == id_asignado), None)
                if supervisor and supervisor.get('telegram_id'):
                    enviar_notificacion_tarea(
                        supervisor['telegram_id'],
                        self.txt_titulo.value,
                        self.txt_desc.value
                    )

                self.page.snack_bar = ft.SnackBar(ft.Text("Tarea asignada correctamente"))
                self.page.snack_bar.open = True
                self.txt_titulo.value = ""
                self.txt_desc.value = ""
                self.dd_asignar.value = None
                self.cargar_tareas(None)
            else:
                self.page.snack_bar = ft.SnackBar(ft.Text("Error al guardar en la base de datos"))
                self.page.snack_bar.open = True

        self.page.update()
