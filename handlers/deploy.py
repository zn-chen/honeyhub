import aiofiles
from uuid import uuid4
from re import sub
from json import loads
from os.path import join

from util import ROOT_DIR
from config import Config
from tornado.web import RequestHandler


template = r"""#!/bin/bash

docker run -it --rm -p 2222:2222\
        -e IDENT=#IDENT# \
        -e NAME=#NAME# \
        -e DESCRIBE=#DESCRIBE# \
        -e HONEYPOT_HOST=#HONEYPOT_HOST# \
        -e HONEYPOT_PORT=#HONEYPOT_PORT# \
        -e RABBIT_HOST=#RABBIT_HOST# \
        -e RABBIT_PORT=#RABBIT_PORT# \
        -e RABBIT_USERNAME=#RABBIT_USERNAME# \
        -e RABBIT_PASSWORD=#RABBIT_PASSWORD# \
        -e SERVER_HOST=#SERVER_HOST# \
        -e SERVER_PORT=#SERVER_PORT# \
        cowriex:2.0.0"""


class DeployHandler(RequestHandler):
    async def post(self):
        """
        节点部署脚本获取接口
        """
        info = loads(self.request.body.decode(encoding="utf-8"))

        name = info.get("name")
        honeypot_type = info.get("type")
        des = info.get("des")
        honeypot_host = info.get("addr")

        conf = Config()
        server_host = conf.Base.addr
        server_port = str(conf.Base.port)

        script_name = await create_deploy_script(
            name=name,
            describe=des,
            honeypot_host=honeypot_host,
            honeypot_port="2222",
            rabbit_host=conf.RabbitMQ.addr,
            rabbit_port=str(conf.RabbitMQ.port),
            rabbit_username=conf.RabbitMQ.username,
            rabbit_password=conf.RabbitMQ.password,
            server_host=server_host,
            server_port=server_port
        )

        self.write({"result": "curl http://%s:%s/script/%s >> %s; chmod +x %s; ./%s"
                    % (server_host, server_port, script_name, script_name, script_name, script_name)})


async def create_deploy_script(**kwarge):
    ident = str(uuid4()).replace('-', "")

    rst = sub("#IDENT#", ident, template)
    rst = sub("#NAME#", kwarge.get("name"), rst)
    rst = sub("#DESCRIBE#", kwarge.get("describe"), rst)
    rst = sub("#HONEYPOT_HOST#", kwarge.get("honeypot_host"), rst)
    rst = sub("#HONEYPOT_PORT#", kwarge.get("honeypot_port"), rst)
    rst = sub("#RABBIT_HOST#", kwarge.get("rabbit_host"), rst)
    rst = sub("#RABBIT_PORT#", kwarge.get("rabbit_port"), rst)
    rst = sub("#RABBIT_USERNAME#", kwarge.get("rabbit_username"), rst)
    rst = sub("#RABBIT_PASSWORD#", kwarge.get("rabbit_password"), rst)
    rst = sub("#SERVER_HOST#", kwarge.get("server_host"), rst)
    rst = sub("#SERVER_PORT#", kwarge.get("server_port"), rst)

    async with aiofiles.open(join(ROOT_DIR, "tmp", ident), "w+") as f:
        await f.write(rst)

    return ident
