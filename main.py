# main.py
import flet as ft
from views.login_view import LoginView
from views.mobile_tasker import MobileTasker
from views.admin_dashboard import AdminDashboard
from views.gerente_dashboard import GerenteDashboard

def main(page: ft.Page):
    page.title = "Tactical Tasker"

    def route_change(route):
        page.views.clear()
        if page.route == "/":
            page.views.append(LoginView(page))
        elif page.route == "/gerente":
            page.views.append(GerenteDashboard(page))
        elif page.route == "/admin":
            page.views.append(AdminDashboard(page))
        elif page.route == "/supervisor":
            page.views.append(MobileTasker(page))
        page.update()

    page.on_route_change = route_change
    page.go("/")

if __name__ == "__main__":
    ft.app(target=main)