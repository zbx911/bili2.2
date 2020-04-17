import bili_statistics
from reqs.tv_raffle_handler import TvRaffleHandlerReq
from tasks.utils import UtilsTask
from .base_class import Forced, DontWait, Multi


class TvRaffleJoinTask(Forced, DontWait, Multi):
    TASK_NAME = 'join_tv_raffle'

    # 这是superuser做的,做完之后就broadcast
    @staticmethod
    async def check(user, real_roomid, json_rsp=None):
        if not await UtilsTask.is_normal_room(user, real_roomid):
            return None
        if json_rsp is None:
            json_rsp = await user.req_s(TvRaffleHandlerReq.check, user, real_roomid)
        next_step_settings = []
        for raffle in json_rsp['data']['gift']:
            raffle_id = raffle['raffleId']
            raffle_type = raffle['type']
            max_wait = raffle['time'] - 10
            # 处理一些重复
            if not bili_statistics.is_raffleid_duplicate(raffle_id):
                user.info(f'确认获取到小电视抽奖 {raffle_id}', with_userid=False)
                next_step_setting = (-2, (raffle['time_wait'], max_wait), real_roomid, raffle_id, raffle_type)
                next_step_settings.append(next_step_setting)
                bili_statistics.add2raffle_ids(raffle_id, 'TV')
                
        return next_step_settings
        
    @staticmethod
    async def work(user, real_roomid, raffle_id, raffle_type):
        json_rsp = await user.req_s(TvRaffleHandlerReq.join, user, real_roomid, raffle_id, raffle_type, timeout=5)
        bili_statistics.add2joined_raffles('小电视(合计)', user.id)
        code = json_rsp['code']
        if not code:
            data = json_rsp['data']
            gift_name = data['award_name']
            gift_num = data['award_num']
            user.info(f'小电视({raffle_id})的参与结果: {gift_name}X{gift_num}')
            bili_statistics.add2results(gift_name, user.id, gift_num)
        elif code == -403 and '拒绝' in json_rsp['msg']:
            user.fall_in_jail()
        else:
            user.info(f'小电视({raffle_id})的参与结果: {json_rsp}')
