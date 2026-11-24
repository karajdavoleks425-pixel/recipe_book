from locust import HttpUser, task

class WebsiteUser(HttpUser):
    host = "http://127.0.0.1:8000"  
    @task
    def list_page(self):
        self.client.get('/')