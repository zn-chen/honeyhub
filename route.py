from tornado.web import StaticFileHandler

from handlers.beat import BeatHandler
from handlers.front import FrontHandler
from handlers.record import RecordHandler
from handlers.deploy import DeployHandler
from handlers.node import NodesHandler, NodeHandler

url = [
    # 节点操作相关路由
    (r"/api/v1.0/nodes", NodesHandler),
    (r"/api/v1.0/nodes/(?P<ident>[a-zA-Z0-9]+)", NodeHandler),

    # 部署脚本获取接口
    (r"/api/v1.0/deploy", DeployHandler),

    # 攻击记录查询接口
    (r"/api/v1.0/record", RecordHandler),

    # 心跳接口路由
    (r"/api/v1.0/beat/(?P<ident>[a-zA-Z0-9]+)", BeatHandler),

    # 临时文件目录
    (r'/script/(.*)', StaticFileHandler, {'path': 'tmp'}),
    
    # 前端路由
    (r'/', FrontHandler),
    (r'/(.*)', StaticFileHandler, {'path': 'static/html/dist'}),
]
