from app import app
import view

# from server.blueprint import server
# from client.blueprint import client
# from issued.blueprint import issued
from po.blueprint import po
# from ca.blueprint import ca

from ca_pyopenssl.blueprint import ca_pyopenssl
from server_pyopenssl.blueprint import server_pyopenssl
from client_pyopenssl.blueprint import client_pyopenssl
from certificate_chain.blueprint import certificate_chain
# from users.blueprint import users

app.register_blueprint(ca_pyopenssl, url_prefix='/ca_pyopenssl')
app.register_blueprint(server_pyopenssl, url_prefix='/server_pyopenssl')
app.register_blueprint(client_pyopenssl, url_prefix='/client_pyopenssl')
app.register_blueprint(certificate_chain, url_prefix='/certificate_chain')
# app.register_blueprint(users, url_prefix='/users')

# app.register_blueprint(ca, url_prefix='/ca')
app.register_blueprint(po, url_prefix='/po')
# app.register_blueprint(server, url_prefix='/server')
# app.register_blueprint(client, url_prefix='/client')
# app.register_blueprint(issued, url_prefix='/issued')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
