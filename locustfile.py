from locust import HttpUser, task, between, SequentialTaskSet
from io import BytesIO

class UserBehavior(SequentialTaskSet):
    def on_start(self):

        response = self.client.post(
            "/login",
            data={
                "username": "testuser",
                "password": "1234"
            }
        )
        self.auth_headers = {"Cookie": f"session={response.cookies.get('session')}"}

    @task
    def edit_task(self):
        self.client.post(
            "/action/task/1/edit",
            data={"title": "Updated Task", "description": "Updated via Locust"},
            headers=self.auth_headers
        )

    @task
    def complete_task(self):
        self.client.get("/action/task/1/complete", headers=self.auth_headers)

    @task
    def delete_task(self):
        self.client.get("/action/task/2/delete", headers=self.auth_headers)

    @task
    def update_profile(self):
        f = BytesIO(b"fake image content")
        f.name = "test.png"
        self.client.post(
            "/profile/profile",
            files={"profile_image": f},
            data={"username": "testuser"},
            headers=self.auth_headers,
            name="/profile/profile"
        )

    @task
    def request_otp(self):
        self.client.post("/profile/request-otp", headers=self.auth_headers)

    @task
    def delete_image(self):
        self.client.post("/profile/delete-image", headers=self.auth_headers)

    @task
    def change_password(self):
        self.client.post(
            "/profile/change-password",
            data={"otp_code": "123456", "new_password": "newpass123"},
            headers=self.auth_headers
        )



class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 3)
