import ssl
import sqlite3
import json
import logging

from customlog.customlog import ColoredLogger

from twisted.web import server, resource
from twisted.internet import reactor, endpoints, ssl

logging.setLoggerClass(ColoredLogger)
logger = logging.getLogger('SERVER - MAIN')

db = "db.sqlite"


def dict_factory(cursor, row):
    """ Creates dictionaries from sqlite queries """
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class ClientHandler(resource.Resource):
    isLeaf = True

    def render_GET(self, request):
        logger.debug(request)
        if request.uri == b"/check_gateway":

            with sqlite3.connect(db) as conn:
                conn.row_factory = dict_factory
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM gateway")
                query = cursor.fetchall()

            request.setHeader(b"content-type", b"application/json")
            data = bytes(json.dumps(query), "UTF-8")
            return data

        elif request.uri == b"/check_subscriptors":
            with sqlite3.connect(db) as conn:
                conn.row_factory = dict_factory
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM subscriptors")
                query = cursor.fetchall()

            data = bytes(json.dumps(query), "UTF-8")
            return data

    def render_POST(self, request):
        logger.debug(request)
        if request.uri == b"/auth":

            json_data = request.content.read()
            rdata = json.loads(json_data.decode("UTF-8"))

            with sqlite3.connect(db) as conn:
                conn.row_factory = dict_factory
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE username = ?", (rdata['user'],))
                query = cursor.fetchone()

            message = {'auth': False}
            if query:
                if rdata['pass'] == query['password']:
                    message = {'auth': True}

            wdata = bytes(json.dumps(message), "UTF-8")
            request.setHeader(b"content-type", b"application/json")

            return wdata

        elif self.path == "/subscriptor_create":
            logger.debug(request)
            """
            if request.uri == b"/auth":

                json_data = request.content.read()
                rdata = json.loads(json_data.decode("UTF-8"))

                with sqlite3.connect(db) as conn:
                    conn.row_factory = dict_factory
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM users WHERE username = ?", (rdata['user'],))
                    query = cursor.fetchone()

                message = {'auth': False}
                if query:
                    if rdata['pass'] == query['password']:
                        message = {'auth': True}

                wdata = bytes(json.dumps(message), "UTF-8")
                request.setHeader(b"content-type", b"application/json")

                return wdata
            """

        return b"NONONONONO"


def main():

    server_port = 8080

    ssl_context = ssl.DefaultOpenSSLContextFactory(
        'privkey.pem',
        'cacert.pem',
    )

    site = server.Site(ClientHandler())
    endpoint = endpoints.SSL4ServerEndpoint(reactor, server_port, ssl_context)
    endpoint.listen(site)

    logger.info('Server start listening on {0}'.format(server_port))
    reactor.run()


if __name__ == '__main__':
    main()
