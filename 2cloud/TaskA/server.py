import hashlib
import json
import os
import re
import time
from cgi import parse_header, parse_multipart
from urllib.parse import quote, unquote
from http.server import BaseHTTPRequestHandler, HTTPServer

import MySQLdb
import cv2
import numpy as np


def connect_mysql(db_host="localhost", user="root", port=3306, passwd="", db="Mysql", charset="utf8"):
    conn = MySQLdb.connect(host=db_host, user=user, port=port, passwd=passwd, db=db, charset=charset)
    conn.autocommit(True)
    return conn.cursor()


def synthesise_image(bg_img, logo_img):
    bg = cv2.imread(bg_img).astype(np.float32)
    logo = cv2.imread(logo_img).astype(np.float32)
    logo = cv2.resize(logo, (50, 50))
    a = 0.5
    bg[30:80, 20:70] = bg[30:80, 20:70] * a + logo * (1 - a)
    out = bg.astype(np.uint8)
    png_img = cv2.imencode('.png', out)[1].tobytes()
    return png_img


# this can be modified to store in any file systems.
def write_image(img, img_path):
    os.makedirs(os.path.dirname(img_path), exist_ok=True)
    with open(img_path, 'wb') as f:
        f.write(img)


class MyHandler(BaseHTTPRequestHandler):
    def _set_response(self, status_code=200, content_type='application/json'):
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        # CORS
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    def _get_user(self):
        session_id = self.headers.get('Authorization')
        res = db.execute("select id, username, product_url,synthesis_url from user where session_id = %s",
                         (session_id,))
        if res == 0:
            return {}
        data = db.fetchone()
        user_logo = self._get_user_logo(data[0], latest=True)
        dict_data = {
            "id": data[0],
            "username": data[1],
            "product_url": data[2],
            "synthesis_url": data[3],
            "session_id": session_id,
            "logo_url": user_logo["logo_url"]
        }
        return dict_data

    def _get_user_logo(self, user_id, latest=True):
        db.execute("select id, logo_url from logo where user_id={} order by updated_at desc".format(user_id))
        if latest:
            data = db.fetchone()
            return {"id": data[0], "logo_url": quote(data[1])}
        else:
            data_list = db.fetchall()
            return [{"id": data[0], "logo_url": quote(data[1])} for data in data_list]

    def _load_json_data(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        data = json.loads(post_data)
        return data

    def _load_multipart_data(self):
        ctype, pdict = parse_header(self.headers.get('Content-Type'))
        pdict['CONTENT-LENGTH'] = int(self.headers.get('Content-length'))
        pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
        if ctype == 'multipart/form-data':
            post_data = parse_multipart(self.rfile, pdict)
            return post_data
        else:
            return None

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        # CORS
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()

    def do_GET(self):
        if self.path == '/':
            self._set_response()
            self.wfile.write("Hello World !".encode('utf-8'))

        elif self.path == '/user':
            session_id = self.headers.get('Authorization')
            if not session_id:
                self._set_response(404)
                self.wfile.write(json.dumps({"msg": "User not found"}).encode('utf-8'))
            user_data = self._get_user()
            if not user_data:
                self._set_response(404)
                self.wfile.write(json.dumps({"msg": "User not found"}).encode('utf-8'))
            else:
                self._set_response()
                self.wfile.write(json.dumps(user_data).encode('utf-8'))

        # match pictures
        elif re.search(r'\.(jpg|jpeg|png)$', self.path, re.IGNORECASE):
            # unquote to decode url and get the absolute path
            product_pic_path = os.path.join(base_url, unquote(self.path[1:]))
            if os.path.exists(product_pic_path) and os.path.isfile(product_pic_path):
                with open(product_pic_path, 'rb') as image_file:
                    self.send_response(200)
                    self.send_header('Content-type', 'image/jpeg')
                    self.end_headers()
                    self.wfile.write(image_file.read())
            else:
                self._set_response(404)
                self.wfile.write(json.dumps({"msg": "Image not found"}).encode('utf-8'))


        elif self.path == '/logo':
            user_data = self._get_user()
            if not user_data:
                self._set_response(404)
                self.wfile.write(json.dumps({"msg": "This User is Not Found"}).encode('utf-8'))
            else:
                logo_data = self._get_user_logo(user_data["id"], latest=False)
                self._set_response()
                self.wfile.write(json.dumps(logo_data).encode('utf-8'))

        else:
            self._set_response(404)
            self.wfile.write(json.dumps({"msg": "Url Not Found"}).encode('utf-8'))

    def do_POST(self):
        if self.path == '/signup':
            data = self._load_json_data()
            # encrpted password
            data['password'] = hashlib.md5(data['password'].encode('utf-8')).hexdigest()
            # check if the username has been registered
            if db.execute("select * from user where username = %s", (data['username'],)):
                self._set_response(409)
                self.wfile.write(json.dumps({"msg": "The username has been registered!"}).encode('utf-8'))
            else:
                # save user data to database
                db.execute("insert into user (username, password, product_url) values (%s, %s, %s)",
                           (data['username'], data['password'], default_product_url))
                # save default logo url to database
                db.execute("insert into logo (user_id, logo_url) values (%s, %s)", (db.lastrowid, default_logo_url))
                self._set_response(201)
                self.wfile.write(json.dumps({"status": "success"}).encode('utf-8'))

        elif self.path == '/login':
            data = self._load_json_data()
            # encrpted password
            data['password'] = hashlib.md5(data['password'].encode('utf-8')).hexdigest()
            # retrive user data from database
            res = db.execute("select * from user where username = %s ", (data['username'],))
            if res == 0:
                self._set_response(404)
                self.wfile.write(json.dumps({"msg": "This User is Not Found"}).encode('utf-8'))
                return

            res = db.execute("select * from user where username = %s and password = %s",
                             (data['username'], data['password']))
            if res == 0:
                self._set_response(404)
                self.wfile.write(json.dumps({"msg": "Password is incorrect!"}).encode('utf-8'))
            else:
                # generate session id
                session_id = hashlib.md5(str(time.time()).encode('utf-8')).hexdigest()
                # save session id to database
                db.execute("update user set session_id=%s where username=%s and password=%s",
                           (session_id, data['username'], data['password']))
                self._set_response(200, 'application/json')
                data = db.fetchone()
                self.wfile.write(json.dumps({"session_id": session_id}).encode('utf-8'))

        elif self.path == '/upload-logo':
            user_data = self._get_user()
            form_data = self._load_multipart_data()
            logo_name = form_data["logo_name"][0]
            if isinstance(logo_name, bytes):
                logo_name = logo_name.decode('utf-8')
            # unquote
            print(logo_name)
            logo_name = unquote(logo_name)
            print(logo_name)
            # use timestamp to generate the img name
            img_path = "/".join(
                ["media", str(user_data["id"]), "logo", str(int(time.time())) + "_" + logo_name])
            # save file to file system
            write_image(form_data["logo"][0], img_path)
            # save logo url to db
            db.execute("insert into logo (user_id, logo_url) values (%s, %s)", (user_data["id"], img_path))
            # synthesise images
            print(img_path)
            syn_img = synthesise_image(user_data["product_url"], img_path)
            syn_img_path = "/".join(["media", str(user_data["id"]), "synthesise",
                                     str(int(time.time())) + "_" + user_data["product_url"].split("/")[-1]])
            # save file to file system
            write_image(syn_img, syn_img_path)
            # update sysnthesise url to db
            db.execute("update user set synthesis_url=%s where id=%s", (syn_img_path, user_data["id"]))
            self._set_response(201, "application/json")
            self.wfile.write(json.dumps({"synthesis_url": quote(syn_img_path)}).encode('utf-8'))

        elif self.path == '/update-logo':
            user_data = self._get_user()
            data = self._load_json_data()
            logo_url = unquote(data["logo_url"])
            # update logo update time
            db.execute("update logo set updated_at=now() where logo_url=%s", (logo_url,))
            # synthesise images
            syn_img = synthesise_image(user_data["product_url"], logo_url)
            syn_img_path = "/".join(["media", str(user_data["id"]), "synthesise",
                                     str(int(time.time())) + "_" + user_data["product_url"].split("/")[-1]])
            # save file to file system
            write_image(syn_img, syn_img_path)
            # update sysnthesise url to db
            db.execute("update user set synthesis_url=%s where id=%s", (syn_img_path, user_data["id"]))
            self._set_response(201, "application/json")
            self.wfile.write(json.dumps({"synthesis_url": quote(syn_img_path)}).encode('utf-8'))

        else:
            self._set_response(404)
            self.wfile.write(json.dumps({"mes": "Not Found"}).encode('utf-8'))


if __name__ == '__main__':
    default_product_url = "media/default_product.jpeg"
    default_logo_url = "media/default_logo.png"
    base_url = os.path.dirname(os.path.abspath(__file__))
    # mysql db
    db = connect_mysql(db_host="localhost", user="root", port=3306, passwd="", db="TaskA", charset="utf8")
    # start server
    server_addr = 'localhost'
    server_port = 8000
    server_address = (server_addr, server_port)
    httpd = HTTPServer(server_address, MyHandler)
    print('Server running on {}:{}...'.format(server_addr, server_port))
    httpd.serve_forever()
