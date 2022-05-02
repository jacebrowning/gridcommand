from livereload import Server

from app.views import app

import log

log.reset()
log.init()
log.silence("datafiles", allow_warning=True)

app.debug = True
server = Server(app.wsgi_app)
server.watch("*.py")
server.watch("templates")
server.watch("data", ignore=lambda _: True)
server.serve(port=5000)
