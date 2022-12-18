from app import app
import view

from server.blueprint import server
from client.blueprint import client
from issued.blueprint import issued
from po.blueprint import po
from ca.blueprint import ca

app.register_blueprint(ca, url_prefix='/ca')
app.register_blueprint(po, url_prefix='/po')
app.register_blueprint(server, url_prefix='/server')
app.register_blueprint(client, url_prefix='/client')
app.register_blueprint(issued, url_prefix='/issued')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
