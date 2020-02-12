from tornado.web import RequestHandler


class FrontHandler(RequestHandler):
    def get(self):
        self.render("../static/html/dist/index.html")
        