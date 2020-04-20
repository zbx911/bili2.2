from bili_global import API_LIVE
import utils
from json_rsp_ctrl import ZERO_ONLY_CTRL


class HeartBeatReq:
    @staticmethod
    async def pc_heartbeat(user):
        url = f'{API_LIVE}/User/userOnlineHeart'
        data = {
            "csrf_token": user.dict_bili['csrf'],
            "csrf": user.dict_bili['csrf']
            }
        json_rsp = await user.bililive_session.request_json('POST', url, data=data, headers=user.dict_bili['pcheaders'])
        return json_rsp

    @staticmethod
    async def app_heartbeat(user):
        extra_params = {
            'access_key': user.dict_bili['access_key'],
            'ts': utils.curr_time(),
        }
        params = user.sort_and_sign(extra_params)
        url = f'{API_LIVE}/mobile/userOnlineHeart'
        payload = {'roomid': 23058, 'scale': 'xhdpi'}
        json_rsp = await user.bililive_session.request_json('POST', url, data=payload, headers=user.dict_bili['appheaders'], params=params)
        return json_rsp

                
class OpenSilverBoxReq:
    @staticmethod
    async def check(user):
        url = f'{API_LIVE}/lottery/v1/SilverBox/getCurrentTask'
        # {"code":0,"msg":"","message":"","data":{"minute":3,"silver":30,"time_start":1566611611,"time_end":1566611791,"times":1,"max_times":3}}
        # {'code': -10017, 'msg': '今天所有的宝箱已经领完!', 'message': '今天所有的宝箱已经领完!', ...}
        json_rsp = await user.bililive_session.request_json('GET', url, headers=user.dict_bili['pcheaders'])
        return json_rsp
    
    @staticmethod
    async def join(user):  # 此 api 限制必须绑定手机号
        extra_params = {
            'access_key': user.dict_bili['access_key'],
            'ts': utils.curr_time(),
        }
        # {'code': 0, 'msg': 'ok', 'message': 'ok', 'data': {'silver': '894135', 'awardSilver': 30, 'isEnd': 0}}
        # {'code': -500, 'msg': '领取时间未到, 请稍后再试', 'message': '领取时间未到, 请稍后再试', 'data': {'surplus': 3}}
        # {'code': -903, 'msg': '已经领取过这个宝箱', 'message': '已经领取过这个宝箱', 'data': {'surplus': -8.0166666666667}}
        # {'code': 400, 'msg': '访问被拒绝', 'message': '访问被拒绝', 'data': []}
        # {'code': -800, 'msg': '未绑定手机', ...}
        params = user.sort_and_sign(extra_params)
        url = f'{API_LIVE}/lottery/v1/SilverBox/getAward'
        json_rsp = await user.bililive_session.request_json('GET', url, headers=user.dict_bili['appheaders'], params=params)
        return json_rsp
        

class RecvDailyBagReq:
    @staticmethod
    async def recv_dailybag(user):
        url = f'{API_LIVE}/gift/v2/live/receive_daily_bag'
        json_rsp = await user.bililive_session.request_json('GET', url, headers=user.dict_bili['pcheaders'])
        return json_rsp
        
        
class SignReq:
    @staticmethod
    async def sign(user):
        url = f'{API_LIVE}/sign/doSign'
        json_rsp = await user.bililive_session.request_json('GET', url, headers=user.dict_bili['pcheaders'])
        return json_rsp
        
        
class WatchTvReq:
    @staticmethod
    async def watch_tv(user):
        url = f'{API_LIVE}/activity/v1/task/receive_award'
        data = {'task_id': 'double_watch_task'}
        json_rsp = await user.bililive_session.request_json('POST', url, data=data, headers=user.dict_bili['appheaders'])
        return json_rsp

    @staticmethod
    async def get_info_by_user_pc(user):
        url = f'{API_LIVE}/xlive/web-room/v1/index/getInfoByUser?room_id=23058'
        # {"code": -101, "message": "账号未登录", "ttl": 1}
        json_rsp = await user.bililive_session.request_json('GET', url, headers=user.dict_bili['pcheaders'])
        return json_rsp

    @staticmethod
    async def get_info_by_user_app(user):
        url = f'{API_LIVE}/xlive/app-room/v1/index/getInfoByUser'
        # {"code": -101, "message": "账号未登录", "ttl": 1}
        extra_params = {
            'access_key': user.dict_bili['access_key'],
            'ts': utils.curr_time(),
            'room_id': '23058'
        }
        params = user.sort_and_sign(extra_params)
        json_rsp = await user.bililive_session.request_json('GET', url, params=params,
                                                            headers=user.dict_bili['appheaders'])
        return json_rsp

                
class SignFansGroupsReq:
    @staticmethod
    async def fetch_groups(user):
        url = "https://api.vc.bilibili.com/link_group/v1/member/my_groups"
        json_rsp = await user.other_session.request_json('GET', url, headers=user.dict_bili['pcheaders'])
        return json_rsp
    
    @staticmethod
    async def sign_group(user, group_id, owner_uid):
        extra_params = {
            'access_key': user.dict_bili["access_key"],
            'group_id': group_id,
            'owner_id': owner_uid,
            'ts': utils.curr_time(),
        }
        params = user.sort_and_sign(extra_params)
        url = f'https://api.vc.bilibili.com/link_setting/v1/link_setting/sign_in'
        json_rsp = await user.other_session.request_json('GET', url, headers=user.dict_bili['appheaders'], params=params)
        return json_rsp
        
        
class SendGiftReq:
    @staticmethod
    async def fetch_gift_config(user):
        url = f'{API_LIVE}/gift/v4/Live/giftConfig'
        json_rsp = await user.bililive_session.request_json('GET', url, ctrl=ZERO_ONLY_CTRL)
        return json_rsp
        
    @staticmethod
    async def fetch_wearing_medal(user):
        url = f'{API_LIVE}/live_user/v1/UserInfo/get_weared_medal'
        data = {
            'uid': user.dict_bili['uid'],
            'csrf_token': user.dict_bili['csrf']
        }
        json_rsp = await user.bililive_session.request_json('POST', url, headers=user.dict_bili['pcheaders'], data=data, ctrl=ZERO_ONLY_CTRL)
        return json_rsp
    
    
class ExchangeSilverCoinReq:
    @staticmethod
    async def silver2coin_web(user):
        url = f'{API_LIVE}/pay/v1/Exchange/silver2coin'
        data = {
            "platform": 'pc',
            "csrf_token": user.dict_bili['csrf']
        }
        json_rsp = await user.bililive_session.request_json('POST', url, headers=user.dict_bili['pcheaders'], data=data)
        return json_rsp

    @staticmethod
    async def silver2coin_app(user):
        extra_params = {
            'access_key': user.dict_bili["access_key"],
            'ts': utils.curr_time()
        }
        params = user.sort_and_sign(extra_params)
        app_url = "https://api.live.bilibili.com/AppExchange/silver2coin"
        json_rsp1 = await user.bililive_session.request_json('GET', app_url, headers=user.dict_bili['appheaders'], params=params)
        return json_rsp1
