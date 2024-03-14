## Task A

1. http 

### cookie or session
1. cookie数据始终在同源的http请求中携带（即使不需要）


if __name__ == '__main__':
    default_product_url = "media/default_product.jpeg"
    default_logo_url = "media/default_logo.png"
    base_url = os.path.dirname(os.path.abspath(__file__))
    # mysql db
    db = connect_mysql(db_host="127.0.0.1", user="brad", port=3333, passwd="5863417aasAAS!", db="TaskA", charset="utf8")
    # start server
    server_addr = '127.0.0.1'
    server_port = 8005
    server_address = (server_addr, server_port)
    httpd = HTTPServer(server_address, MyHandler)
    print('Server running on {}:{}...'.format(server_addr, server_port))
    httpd.serve_forever()


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'TaskB',
        'USER': 'brad',
        'PASSWORD': '5863417aasAAS!',
        'HOST': '127.0.0.1',
        'PORT': 3333,
        'OPTIONS': {'charset': 'utf8mb4'},
}
}


var apiUrlBase = 'http://pythoner.me/2cloud/TaskA/'