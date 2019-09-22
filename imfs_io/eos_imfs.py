import os
import json
import time
from eospy.cleos import Cleos
import eospy.cleos
import eospy.keys
import pytz
import requests
import base64

eos_endpoint = 'https://eosbp.atticlab.net'
eos_endpoint = 'https://eos.greymass.com:443'
# eos_endpoint = 'https://eosapi.blockmatrix.network:443'
# eos_endpoint = 'https://eu1.eosdac.io:443'

#depth = 333


# imfs_provider_account = 'wealthysnake'
# active_privat_key = os.environ['IMFS_PROVIDER_PRIVAT_KEY']

class EosDir:
    account = ''
    path = ''
    sender_account = ''
    sender_privat_key = ''

    def __init__(self, account: str, path: str, sender_account: str, sender_privat_key: str):
        self.account = account
        self.path = path
        self.sender_account = sender_account
        self.sender_privat_key = sender_privat_key

    def get_dir(self) -> int:
        # return {}
        memos = self.__get_last_actions(333)
        # memos.reverse()
        f_count = 0
        for m in memos:
            memo = m['memo']
            if self.__is_json(memo):
                memo_d = json.loads(memo)
                if ('imfs' in memo_d.keys()):
                    print(memo_d)
                    for fn in memo_d:
                        if fn != 'imfs' and fn != 'next_dir':
                            f_count += 1
                            print('file_name is: ', fn, ' end_block is: ', memo_d[fn])
                            eos_file = EosFile(self.account, self.path, fn, self.sender_account, self.sender_privat_key)
                            eos_file.get_file()
                    return f_count
        return 0

    def __get_last_actions(self, depth: int):
        out = {}
        ce = Cleos(url=eos_endpoint)
        actions = ce.get_actions(self.account, pos=-1, offset=-depth)
        if 'actions' in actions.keys():
            out = actions['actions']
        memos = []
        for s in out:
            receiver = s['action_trace']['receipt']['receiver']
            data = s['action_trace']['act']['data']
            if s['action_trace']['act']['name'] == 'transfer' \
                    and receiver == self.account \
                    and 'to' in data.keys() \
                    and data['to'] == self.account \
                    and 'from' in data.keys() \
                    and 'quantity' in data.keys() \
                    and (data['quantity'].find('EOS') != -1 or data['quantity'].find('KNYGA') != -1):
                data['recv_sequence'] = s['action_trace']['receipt']['recv_sequence']
                data['account'] = s['action_trace']['act']['account']
                block_n = s['account_action_seq']
                data['block_num'] = block_n
                data['glob_num'] = s['block_num']
                memos.append(data)
        memos.reverse()
        return memos

    def __is_json(self, myjson):
        try:
            json_object = json.loads(myjson)
        except ValueError:
            return False
        return True


class EosFile:
    account = ''
    path = ''
    file_name = ''
    sender_account = ''
    sender_privat_key = ''

    def __init__(self, account: str, path: str, file_name: str, sender_account: str, sender_privat_key: str):
        self.account = account
        self.path = path
        self.file_name = file_name
        self.sender_account = sender_account
        self.sender_privat_key = sender_privat_key

    def ping(self):
        print("I'm here")

    def put_file(self) -> int:
        '''
        :return: block number of file header block
        '''
        fc = ''
        block_size = 200
        fb = open(f'{self.path}/{self.file_name}', 'rb')
        fc = fb.read()
        #print('file content = ', fc)
        fb.close()
        fc_encoded = self.__encode_str(fc)
        block_num = 0
        while fc_encoded != '':
            if len(fc_encoded) >= block_size:
                data_block = fc_encoded[:block_size]
                fc_encoded = fc_encoded[block_size:]
            else:
                data_block = fc_encoded[:len(fc_encoded)]
                fc_encoded = fc_encoded[len(fc_encoded):]
            data_json = f'{{"file":"{self.file_name}","next_block":{block_num},"data":"{data_block}"}}'
            ret = self.__send_block(data_json)
            if ('transaction_id' in ret):
                #print(ret)
                glob_block = ret['processed']['block_num']
                # block_num = 0
                l1 = 0
                while l1 == 0:
                    # time.sleep(1)
                    memos = self.__get_last_actions(15)
                    for m in memos:
                        if ('memo' in m):
                            memo_in = m['memo']
                            if self.__is_json(memo_in):
                                memo_d = json.loads(memo_in)
                                #print('memo_d =', memo_d)
                                if 'data' in memo_d:
                                    if memo_d['data'].find(data_block) != -1:
                                        # print('glob_block = ', glob_block, ' m[glob_num] = ', m['glob_num'])
                                        # if glob_block == m['glob_num'] or glob_block == m['glob_num'] + 1:
                                        if block_num == memo_d['next_block']:
                                            block_num = m['block_num']
                                            l1 = block_num
                print('block_num = ', block_num)
            else:
                return 0
            time.sleep(1)
        self.update_dir(block_num)
        return block_num

    def get_file(self) -> str:
        ce = Cleos(url=eos_endpoint)
        dir_l = self.get_dir()
        if dir_l == {}:
            return ''
        if self.file_name in dir_l.keys():
            head_block = dir_l[self.file_name]
            print(head_block)
            out = {}
            n_block = head_block
            r_data = ''
            while n_block != 0:
                actions = ce.get_actions(self.account, pos=n_block, offset=0)
                if 'actions' in actions.keys():
                    out = actions['actions']
                for s in out:
                    memo_l = (s['action_trace']['act']['data']['memo'])
                    memo_d = json.loads(memo_l)
                    r_data = memo_d['data'] + r_data
                    n_block = memo_d['next_block']
                    print('next_block is: ', n_block)
                    #print(r_data)
            dec_data = self.__decode_str(r_data)
            #print(dec_data)
            fb = open(f'{self.path}/{self.file_name}', 'wb')
            fb.write(dec_data)
            fb.close()
        else:
            return ''

    def get_dir(self):
        #return {}
        memos = self.__get_last_actions(333)
        # memos.reverse()
        for m in memos:
            memo = m['memo']
            if self.__is_json(memo):
                memo_d = json.loads(memo)
                if ('imfs' in memo_d.keys()):
                    return memo_d
        return {}

    def update_dir(self, head_block: int):
        cur_dir = self.get_dir()
        upd_dir = cur_dir
        print('update_dir -> cur_dir: ', upd_dir)
        if cur_dir == {}:
            upd_dir = {
                "imfs": "v_0.1",
                "next_dir": 0
            }
        upd_dir[self.file_name] = head_block
        upd_dir = json.dumps(upd_dir)
        print(str(upd_dir))
        return self.__send_block(str(upd_dir))

    def get_all_files(self, account: str, path: str) -> int:
        '''
        :returns quantity of saved files
        '''
        pass

    def __is_json(self, myjson):
        try:
            json_object = json.loads(myjson)
        except ValueError:
            return False
        return True

    def __encode_str(self, bytes_to_encode) -> str:
        b1 = base64.b64encode(bytes_to_encode)
        s1 = b1.decode('utf-8')
        print(s1)
        return s1

    def __decode_str(self, encoded_data: str):
        b1 = base64.b64decode(encoded_data)
        # s2 = base64.b64decode(encoded_data).decode("utf-8", "ignore")
        return b1

    def __send_block(self, memo: str):
        ce = Cleos(url=eos_endpoint)
        arguments = {
            "from": self.sender_account,  # sender
            "to": self.account,  # receiver
            "quantity": '0.0001 EOS',  # In Token
            "memo": memo,
        }
        payload = {
            "account": 'eosio.token',
            "name": 'transfer',
            "authorization": [{
                "actor": self.sender_account,
                "permission": 'active',
            }],
        }
        # Converting payload to binary
        data = ce.abi_json_to_bin(payload['account'], payload['name'], arguments)
        # Inserting payload binary form as "data" field in original payload
        payload['data'] = data['binargs']
        # final transaction formed
        trx = {"actions": [payload]}
        import datetime as dt
        trx['expiration'] = str((dt.datetime.utcnow() + dt.timedelta(seconds=60)).replace(tzinfo=pytz.UTC))
        key = eospy.keys.EOSKey(self.sender_privat_key)
        resp = ce.push_transaction(trx, key, broadcast=True)
        if ('transaction_id' in resp.keys()):
            return resp
        else:
            return ''

    def __get_last_actions(self, depth: int):
        out = {}
        ce = Cleos(url=eos_endpoint)
        actions = ce.get_actions(self.account, pos=-1, offset=-depth)
        if 'actions' in actions.keys():
            out = actions['actions']
        memos = []
        for s in out:
            receiver = s['action_trace']['receipt']['receiver']
            data = s['action_trace']['act']['data']
            if s['action_trace']['act']['name'] == 'transfer' \
                    and receiver == self.account \
                    and 'to' in data.keys() \
                    and data['to'] == self.account \
                    and 'from' in data.keys() \
                    and 'quantity' in data.keys() \
                    and (data['quantity'].find('EOS') != -1 or data['quantity'].find('KNYGA') != -1):
                data['recv_sequence'] = s['action_trace']['receipt']['recv_sequence']
                data['account'] = s['action_trace']['act']['account']
                block_n = s['account_action_seq']
                data['block_num'] = block_n
                data['glob_num'] = s['block_num']
                memos.append(data)
        memos.reverse()
        return memos

    def test_send(self):
        ce = eospy.cleos.Cleos(url=eos_endpoint)

        arguments = {
            "from": self.sender_account,  # sender
            "to": self.account,  # receiver
            "quantity": '0.0001 EOS',  # In EOS
            "memo": "memo 1213",
        }
        payload = {
            "account": "eosio.token",
            "name": "transfer",
            "authorization": [{
                "actor": self.sender_account,
                "permission": 'active',
            }],
        }
        # Converting payload to binary
        data = ce.abi_json_to_bin(payload['account'], payload['name'], arguments)
        # Inserting payload binary form as "data" field in original payload
        payload['data'] = data['binargs']
        # final transaction formed
        trx = {"actions": [payload]}
        import datetime as dt
        trx['expiration'] = str(
            (dt.datetime.utcnow() + dt.timedelta(seconds=60)).replace(tzinfo=pytz.UTC))
        # use a string or EOSKey for push_transaction
        key1 = self.sender_privat_key
        # use EOSKey:
        key = eospy.keys.EOSKey(self.sender_privat_key)
        resp = ce.push_transaction(trx, key, broadcast=True)
        print('------------------------------------------------')
        print(resp)
        print('------------------------------------------------')

    def get_last(self):
        out = {}
        ce = Cleos(url=eos_endpoint)
        # actions = ce.get_actions(self.account, pos=-1, offset=-depth)
        actions = ce.get_actions(self.account, pos=6940, offset=1)
        print(actions)
        if 'actions' in actions.keys():
            out = actions['actions']
