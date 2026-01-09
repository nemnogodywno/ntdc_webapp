from locust import HttpUser, task, between
from locust.exception import RescheduleTask


class WebsiteUser(HttpUser):
    wait_time = between(1, 5)

    def on_start(self):
        """Логин через реальную форму /accounts/login/ с CSRF."""
        # 1. GET формы логина, чтобы получить csrftoken и куки
        login_page = self.client.get("/accounts/login/", name="/accounts/login/ [GET]")

        csrftoken = login_page.cookies.get("csrftoken")
        if not csrftoken:
            raise RescheduleTask("No csrftoken cookie on login page")

        # 2. POST как делает браузер: csrf + username + password
        response = self.client.post(
            "/accounts/login/",
            data={
                "csrfmiddlewaretoken": csrftoken,
                "username": "admin",   # Имя пользователя
                "password": "admin",   # Пароль
            },
            headers={
                "Referer": "http://localhost/accounts/login/",
            },
            name="/accounts/login/ [POST]",
            allow_redirects=False,
        )

        # Успешный логин в Django обычно даёт 302 на next / профиль / главную
        if response.status_code not in (301, 302):
            raise RescheduleTask(f"Login failed with status {response.status_code}")

    # Главная страница используется чаще всего
    @task(5)
    def index(self):
        self.client.get("/", name="/")

    # Дашборд реже, но важен по производительности
    @task(3)
    def dashboard(self):
        self.client.get("/dashboard/", name="/dashboard/")

    # Материальные части — список
    @task(4)
    def material_parts_list(self):
        self.client.get("/material-parts/", name="/material-parts/")

    # Операции — список
    @task(3)
    def operations_list(self):
        self.client.get("/operations/", name="/operations/")

    # Сценарий-цепочка: материалы список → деталь → редактирование
    @task(2)
    def material_parts_flow(self):
        # 1. Список
        self.client.get("/material-parts/", name="/material-parts/ [list]")

        part_id = 1  # пример id

        # 2. Деталь
        self.client.get(f"/material-parts/{part_id}/", name="/material-parts/[id]/ detail")

        # 3. Страница редактирования (GET форма)
        self.client.get(f"/material-parts/{part_id}/edit/", name="/material-parts/[id]/ edit")
