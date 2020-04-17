import asyncio
import re

from printer import print_danmu
from printer import info as print
import notifier
import bili_statistics
from danmu.bili_abc import bili_danmu
from tasks.tv_raffle_handler import TvRaffleJoinTask
from tasks.guard_raffle_handler import GuardRafflJoinTask
from tasks.storm_raffle_handler import StormRaffleJoinTask
from tasks.utils import UtilsTask
from danmu import raffle_handler
from utils import clear_whitespace


class DanmuPrinter(bili_danmu.WsDanmuClient):
    __slots__ = ()

    def handle_danmu(self, data: dict) -> bool:
        if 'cmd' in data:
            cmd = data['cmd']
        elif 'msg' in data:
            data = data['msg']
            cmd = data['cmd']
        else:
            return True  # 预防未来sbb站

        if cmd == 'DANMU_MSG':
            print_danmu(data)
        return True


class DanmuRaffleMonitor(bili_danmu.WsDanmuClient):
    __slots__ = ()

    # clear_whitespace之后
    # 全区广播:<%生而为人要温柔%>送给<%岛岛子%>1个应援喵，点击前往TA的房间去抽奖吧
    # 全区广播:主播<%咩咩想喝甜奶盖%>的直播间得到了偶像恋人的回应，快去前往抽奖吧！
    # 娱乐区广播:<%阿a飘piao大草莓pizza%>送给<%雫るる_Official%>1个摩天大楼，点击前往TA的房间去抽奖吧
    # .+X>(?!.*X) 是匹配最后一个 X
    NOTICE_MSG_TV_PATTERN = r = re.compile(r'.+%>(?!.*%>)'  # 匹配最后一个 %>
                                           # X个、XXX了、直播间XX了、暴力保留，
                                           # ⚠还有匹配的优先级（因为第二个和第三个可能混合"开启了XX直播间抽奖"（我自己造的））
                                           r'(?:(\d+)个|[^，,了]+了|[^，,]+?(?:直播间|房间)[^，,了]{2}了?)?'
                                           # 前面的动作之后，第一个逗号之前
                                           r'([^，,]+)', re.DOTALL)

    # clear_whitespace之后
    # <%阿奎祝君某生日快乐%>在本房间开通了舰长
    NOTICE_MSG_GUARD_PATTERN = re.compile(r'.+%>(?!.*%>)'  # 匹配最后一个 %>
                                          r'[^，,了]+了(.{2})', re.DOTALL)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._funcs_task.append(self._check_area)  # 比正常的监控多了一个分区定时查看

    async def _check_area(self):
        try:
            await asyncio.sleep(300)
            while await asyncio.shield(
                    notifier.exec_func(UtilsTask.is_ok_as_monitor, self._room_id, self._area_id)):
                await asyncio.sleep(300)
            print(f'{self._room_id} 不再适合作为监控房间，即将切换')
        except asyncio.CancelledError:
            return

    async def _prepare_client(self) -> bool:
        # 1566786363: 把room_id删了，否则导致下播后又选择几率过高（b站api有延迟）
        self._room_id = await notifier.exec_func(
            UtilsTask.get_room_by_area,
            self._area_id)
        print(f'{self._area_id} 号数据连接选择房间（{self._room_id}）')
        if self._room_id is None:
            print(f'{self._area_id} 号数据连接准备部分发生致命错误')
            self._closed = True  # 内部关闭，不再重连
            return False
        return True

    def handle_danmu(self, data: dict) -> bool:
        if 'cmd' in data:
            cmd = data['cmd']
        elif 'msg' in data:
            data = data['msg']
            cmd = data['cmd']
        else:
            return True  # 预防未来sbb站

        if cmd == 'PREPARING':
            print(f'{self._area_id} 号数据连接房间下播({self._room_id})')
            return False

        elif cmd == 'NOTICE_MSG':
            # 1 《第五人格》哔哩哔哩直播预选赛六强诞生！
            # 2 全区广播：<%user_name%>送给<%user_name%>1个嗨翻全城，快来抽奖吧
            # 3 <%user_name%> 在 <%user_name%> 的房间开通了总督并触发了抽奖，点击前往TA的房间去抽奖吧
            # 4 欢迎 <%总督 user_name%> 登船
            # 5 恭喜 <%user_name%> 获得大奖 <%23333x银瓜子%>, 感谢 <%user_name%> 的赠送
            # 6 <%user_name%> 在直播间 <%529%> 使用了 <%20%> 倍节奏风暴，大家快去跟风领取奖励吧！(只报20的)
            msg_type = data['msg_type']
            real_roomid = data['real_roomid']
            msg_common = clear_whitespace(data['msg_common'], '“”')
            if msg_type == 2 or msg_type == 8:
                if data['msg_common']:
                    # description0, raffle_name = self.NOTICE_MSG_TV_PATTERN.match(msg_common).group(1, 2)
                    broadcast = 'nmb'
                    raffle_num = 1
                    raffle_name = '小电视'
                    print(f'{self._area_id} 号数据连接检测到{real_roomid:^9}的{raffle_name}')
                    raffle_handler.push2queue(TvRaffleJoinTask, real_roomid)
                    broadcast_type = 0 if broadcast == '全区' else 1
                    bili_statistics.add2pushed_raffles(raffle_name, broadcast_type, raffle_num)
            elif msg_type == 3:
                raffle_name = self.NOTICE_MSG_GUARD_PATTERN.match(msg_common).group(1)
                print(f'{self._area_id} 号数据连接检测到{real_roomid:^9}的{raffle_name}')
                raffle_handler.push2queue(GuardRafflJoinTask, real_roomid)
                broadcast_type = 0 if raffle_name == '总督' else 2
                bili_statistics.add2pushed_raffles(raffle_name, broadcast_type)
            elif msg_type == 6:
                raffle_name = '二十倍节奏风暴'
                print(f'{self._area_id} 号数据连接检测到{real_roomid:^9}的{raffle_name}')
                raffle_handler.push2queue(StormRaffleJoinTask, real_roomid)
                bili_statistics.add2pushed_raffles(raffle_name)
        return True
