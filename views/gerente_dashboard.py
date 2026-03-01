import flet as ft
from database.db_manager import crear_usuario, obtener_usuarios, crear_nueva_tarea, listar_todas_tareas
from services.telegram_notifier import enviar_notificacion_tarea

class GerenteDashboard(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(route="/gerente")
        self.page = page
        self.usuarios_sistema = []
        self.id_gerente = page.session.get("user_id")

        # --- TAB TAREAS ---
        self.txt_titulo = ft.TextField(label="Titulo de la Tarea", expand=True, border_color=ft.colors.INDIGO_400)
        self.txt_desc = ft.TextField(
            label="Descripcion", expand=True, multiline=True,
            min_lines=1, max_lines=3, border_color=ft.colors.INDIGO_400
        )
        self.dd_asignar = ft.Dropdown(label="Asignar a", expand=True, border_color=ft.colors.INDIGO_400)
        self.tabla_mis_tareas = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Titulo", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Asignado a", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Estado", weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
            border=ft.border.all(1, ft.colors.INDIGO_200),
            border_radius=8,
        )

        # --- TAB PERSONAL ---
        self.txt_nombre = ft.TextField(label="Nombre Completo", expand=True)
        self.txt_email = ft.TextField(label="Email Corporativo", expand=True)
        self.txt_telegram = ft.TextField(label="ID Chat Telegram", expand=True)
        self.txt_funcion = ft.TextField(label="Funcion (Area/Puesto)", expand=True)
        self.dd_rol = ft.Dropdown(
            label="Rol de Sistema",
            options=[
                ft.dropdown.Option("Gerente"),
                ft.dropdown.Option("Admin"),
                ft.dropdown.Option("Supervisor")
            ],
            expand=True
        )
        self.lista_personal = ft.Column(spacing=10)

        tab_tareas = ft.Tab(
            text="Tareas",
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Asignar Nueva Tarea", size=20, weight=ft.FontWeight.BOLD),
                    ft.Row([self.txt_titulo, self.dd_asignar], spacing=10),
                    self.txt_desc,
                    ft.ElevatedButton(
                        "Guardar y Asignar Tarea",
                        icon=ft.icons.SAVE,
                        on_click=self.guardar_tarea,
                        bgcolor=ft.colors.INDIGO_700,
                        color=ft.colors.WHITE,
                        height=50
                    ),
                    ft.Divider(height=30),
                    ft.Row([
                        ft.Text("Mis Tareas Asignadas", size=20, weight=ft.FontWeight.BOLD),
                        ft.IconButton(icon=ft.icons.REFRESH, on_click=self.cargar_mis_tareas, tooltip="Actualizar")
                    ]),
                    self.tabla_mis_tareas,
                ], spacing=15, scroll=ft.ScrollMode.AUTO),
                padding=20
            )
        )

        tab_personal = ft.Tab(
            text="Personal",
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Alta de Nuevo Personal", size=20, weight=ft.FontWeight.BOLD),
                    ft.Row([self.txt_nombre, self.txt_email]),
                    ft.Row([self.txt_funcion, self.dd_rol]),
                    self.txt_telegram,
                    ft.ElevatedButton(
                        "Registrar en el Sistema",
                        icon=ft.icons.PERSON_ADD,
                        on_click=self.registrar_usuario,
                        bgcolor=ft.colors.INDIGO_700,
                        color=ft.colors.WHITE
                    ),
                    ft.Divider(height=30),
                    ft.Row([
                        ft.Text("Personal Activo", size=20, weight=ft.FontWeight.BOLD),
                        ft.IconButton(icon=ft.icons.REFRESH, on_click=self.cargar_personal, tooltip="Actualizar")
                    ]),
                    self.lista_personal,
                ], spacing=15, scroll=ft.ScrollMode.AUTO),
                padding=20
            )
        )

        self.controls = [
            ft.AppBar(
                title=ft.Text("Panel Gerente - Tactical Tasker"),
                bgcolor=ft.colors.INDIGO_900,
                actions=[
                    ft.IconButton(
                        icon=ft.icons.LOGOUT,
                        tooltip="Cerrar sesion",
                        icon_color=ft.colors.WHITE,
                        on_click=self.cerrar_sesion
                    )
                ]
            ),
            ft.Tabs(
                selected_index=0,
                tabs=[tab_tareas, tab_personal],
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
            print(f"Error cargando datos: {e}")
        self.cargar_mis_tareas(None)
        self.cargar_personal(None)

    def cargar_mis_tareas(self, e):
        todas = listar_todas_tareas()
        mis_tareas = [t for t in todas if t['id_creador'] == self.id_gerente]
        mapa_usuarios = {u['id']: u['nombre'] for u in self.usuarios_sistema}

        self.tabla_mis_tareas.rows = []
        for t in mis_tareas:
            nombre_asignado = mapa_usuarios.get(t['id_asignado'], f"ID {t['id_asignado']}")
            completada = t['estado'] == 'Completada'
            estado_color = ft.colors.GREEN_700 if completada else ft.colors.ORANGE_700
            self.tabla_mis_tareas.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(t['titulo'])),
                    ft.DataCell(ft.Text(nombre_asignado)),
                    ft.DataCell(ft.Text(t['estado'], color=estado_color)),
                ])
            )
        self.page.update()

    def guardar_tarea(self, e):
        if not self.txt_titulo.value or not self.dd_asignar.value:
            self.page.snack_bar = ft.SnackBar(ft.Text("El titulo y el asignado son obligatorios"))
            self.page.snack_bar.open = True
        else:
            id_asignado = int(self.dd_asignar.value)
            resultado = crear_nueva_tarea(
                self.txt_titulo.value,
                self.txt_desc.value,
                id_asignado,
                self.id_gerente
            )
            if resultado:
                supervisor = next((u for u in self.usuarios_sistema if u['id'] == id_asignado), None)
                if supervisor and supervisor.get('telegram_id'):
                    enviar_notificacion_tarea(supervisor['telegram_id'], self.txt_titulo.value, self.txt_desc.value)

                self.page.snack_bar = ft.SnackBar(ft.Text("Tarea asignada correctamente"))
                self.page.snack_bar.open = True
                self.txt_titulo.value = ""
                self.txt_desc.value = ""
                self.dd_asignar.value = None
                self.cargar_mis_tareas(None)
            else:
                self.page.snack_bar = ft.SnackBar(ft.Text("Error al guardar la tarea"))
                self.page.snack_bar.open = True
        self.page.update()

    def cargar_personal(self, e):
        usuarios = obtener_usuarios()
        self.lista_personal.controls.clear()
        ROL_COLOR = {
            "Gerente": ft.colors.INDIGO_700,
            "Admin": ft.colors.BLUE_700,
            "Supervisor": ft.colors.TEAL_700,
        }
        for u in usuarios:
            color = ROL_COLOR.get(u['rol'], ft.colors.GREY_700)
            self.lista_personal.controls.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.icons.PERSON, color=color),
                            ft.Column([
                                ft.Text(u['nombre'], weight=ft.FontWeight.BOLD),
                                ft.Text(u['email'], size=12, color=ft.colors.GREY_600),
                                ft.Text(u.get('funcion') or "", size=12, color=ft.colors.GREY_600),
                            ], spacing=2, expand=True),
                            ft.Container(
                                content=ft.Text(u['rol'], color=ft.colors.WHITE, size=12),
                                bgcolor=color,
                                padding=ft.padding.symmetric(horizontal=10, vertical=4),
                                border_radius=12,
                            )
                        ], alignment=ft.MainAxisAlignment.START,
                           vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=15),
                        padding=15
                    )
                )
            )
        self.page.update()

    def registrar_usuario(self, e):
        if not self.txt_nombre.value or not self.txt_email.value or not self.dd_rol.value:
            self.page.snack_bar = ft.SnackBar(ft.Text("Nombre, Email y Rol son obligatorios"))
            self.page.snack_bar.open = True
        else:
            rol_formateado = self.dd_rol.value.capitalize()
            exito = crear_usuario(
                self.txt_nombre.value,
                self.txt_email.value,
                rol_formateado,
                self.txt_funcion.value,
                self.txt_telegram.value
            )
            if exito:
                self.page.snack_bar = ft.SnackBar(ft.Text("Usuario creado correctamente"))
                self.txt_nombre.value = ""
                self.txt_email.value = ""
                self.txt_funcion.value = ""
                self.txt_telegram.value = ""
                self.dd_rol.value = None
                self.page.snack_bar.open = True
                self.cargar_personal(None)
        self.page.update()
