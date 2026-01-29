from locust import HttpUser, task, between, SequentialTaskSet

class UserBehavior(SequentialTaskSet):
    def on_start(self):

        response = self.client.post(
            "/login",
            data={
                "username": "moghtade",
                "password": "123456"
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


class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 3)
