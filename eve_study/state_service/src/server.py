'''main module for LSS server based on CherrPy WSGI (https://cherrypy.org/)

* cherrypy provides endpoint for LSS server which resides in container 'web'
* the actual application is done by Eve (http://python-eve.org/) and its entry point is module 'api'
'''

if __name__ == '__main__':
    import cherrypy
    import sys
    from api import app

    if "-d" in sys.argv:
        cherrypy.process.plugins.Daemonizer(cherrypy.engine).subscribe()

    # Mount the application
    cherrypy.tree.graft(app, "/")

    # Unsubscribe the default server
    cherrypy.server.unsubscribe()


    # Instantiate a new server object
    server = cherrypy._cpserver.Server()

    # Configure the server object
    server.socket_host = "0.0.0.0"
    server.socket_port = 8000
    server.thread_pool = 30

    # For SSL Support
    # server.ssl_module            = 'pyopenssl'
    # server.ssl_certificate       = 'ssl/certificate.crt'
    # server.ssl_private_key       = 'ssl/private.key'
    # server.ssl_certificate_chain = 'ssl/bundle.crt'

    # Subscribe this server
    server.subscribe()

    # Start the server engine (Option 1 *and* 2)

    cherrypy.engine.start()
    cherrypy.engine.block()
