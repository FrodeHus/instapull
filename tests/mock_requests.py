import json

class MockResponse:
    def __init__(self, text, status_code):
        self.text = text
        self.status_code = status_code
        self.content = text
    
    def text(self):
        return self.text
    def content(self):
        return self.content
    def json(self):
        return json.loads(self.text)