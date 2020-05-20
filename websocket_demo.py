# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function
from datetime import datetime
import os

import tornado
from tornado.options import define, options
from tornado.web import RequestHandler
from tornado.websocket import WebSocketHandler

# 设置服务器端口
define("port", default=2222, type=int)


class IndexHandler(RequestHandler):
    def get(self):
        self.render("chat-client.html")


class ChatHandler(WebSocketHandler):
    users = set()  # 用来存放在线用户的容器

    def open(self):
        # 建立连接后添加用户到容器中
        self.users.add(self)

        # 向已在线用户发送消息
        for user in self.users:
            remote_ip, port = self.request.connection.context.address
            now = datetime.now().strftime("%H:%M:%S")
            user.write_message("[{}][{}:{}]-进入聊天室".format(now, remote_ip, port))

    def on_message(self, message):
        # 向在线用户广播消息
        now = datetime.now().strftime("%H:%M:%S")
        remote_ip, port = self.request.connection.context.address
        for user in self.users:
            user.write_message("[{}][{}:{}] {}".format(now, remote_ip, port, message))

    def on_close(self):
        # 用户关闭连接后从容器中移除用户
        now = datetime.now().strftime("%H:%M:%S")
        remote_ip, port = self.request.connection.context.address
        self.users.remove(self)
        for user in self.users:
            user.write_message("[{}][{}:{}]-离开聊天室".format(now, remote_ip, port))

    def check_origin(self, origin):
        return True  # 允许WebSocket的跨域请求


if __name__ == '__main__':
    tornado.options.parse_command_line()

    app = tornado.web.Application([
        (r"/", IndexHandler),
        (r"/chat", ChatHandler),
    ],
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        debug=True
    )

    http_server = tornado.httpserver.HTTPServer(app, xheaders=True)
    http_server.listen(options.port, "0.0.0.0")
    tornado.ioloop.IOLoop.current().start()
