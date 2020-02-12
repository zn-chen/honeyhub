from time import strftime, localtime
from json import loads
from logging import getLogger

from model.record import Record
from tornado.web import RequestHandler


class RecordHandler(RequestHandler):
    """
    攻击记录相关接口
    """
    _logger = getLogger()

    async def post(self):
        """
        获取分页数据
        """
        page_info = self.request.body.decode(encoding="utf-8")
        page_info = loads(page_info)

        page_size = page_info["page_size"]
        start_page = page_info["start_page"]
        end_page = page_info["end_page"]

        rst = await Record().get_record(num=(end_page-start_page+1)*page_size, start=start_page*page_size)

        view_data = []
        for i in rst:
            payload = "登录账户:%s/%s, 执行命令" % (i["loggedin"][0], i["loggedin"][1])
            for i2 in i["commands"]:
                payload += (i2 + " ")

            view_data.append({
                "name": i["name"],
                "peer_ip": i["peer_ip"],
                "peer_port": i["peer_port"],
                "host_ip": i["host_ip"],
                "host_port": i["host_port"],
                "timestamp": strftime("%Y-%m-%d %H:%M:%S", localtime(int(i["timestamp"]))),
                "protocol": i["protocol"],
                "payload":payload})

        self.write({"result": view_data})
