# coding:utf-8

import tornado.web
import tornado.ioloop
import tornado.httpserver
import tornado.options
import os
import datetime

from tornado.web import RequestHandler
from tornado.options import define, options
from tornado.websocket import WebSocketHandler

define("port", default=8000, type=int)

class IndexHandler(RequestHandler):
    def get(self):
        self.render("index.html")

class ChatHandler(WebSocketHandler):

    users = set()  # 用户ID
    client_id = 1
    def open(self):
        self.client_id = ChatHandler.client_id  #每个客户端独有的ID
        ChatHandler.client_id = ChatHandler.client_id + 1
        self.users.add(self)  # 每个request添加一个用户
        for u in self.users:  # 登录告知所有人
            u.write_message(u"[%s]-[%s]-进入聊天室" % ("游客" + str(self.client_id), datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            

    def on_message(self, message):
        for u in self.users:  # 向在线用户广播消息
            u.write_message(u"[%s]-[%s]-说：%s" % ("游客" + str(self.client_id), datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message))

    def on_close(self):
        self.users.remove(self) # 用户关闭连接后从容器中移除用户
        for u in self.users:
            u.write_message(u"[%s]-[%s]-离开聊天室" % ("游客" + str(self.client_id), datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    def check_origin(self, origin):
        return True  

if __name__ == '__main__':
    tornado.options.parse_command_line()
    app = tornado.web.Application([
            (r"/", IndexHandler),
            (r"/chat", ChatHandler),
        ],
        static_path = os.path.join(os.path.dirname(__file__), "static"),    #ico文件路径
        template_path = os.path.join(os.path.dirname(__file__), "templates"), #视图文件路径
        debug = True
        )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()

