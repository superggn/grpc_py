# coding:utf-8
import random
import time

import grpc

import hello_bili_pb2 as pb2
import hello_bili_pb2_grpc as pb2_grpc


# GRPC_VERBOSITY = 'debug'

# if os.environ.get('https_proxy'):
#     del os.environ['https_proxy']
# if os.environ.get('http_proxy'):
#     del os.environ['http_proxy']


def test():
    index = 0
    while 1:
        time.sleep(1)
        data = str(random.random())
        if index == 5:
            break
        print(index)
        index += 1
        yield pb2.TestClientSendStreamRequest(data=data)


def run():
    options = [
        ('grpc.max_send_message_length', 50 * 1024 * 1024),
        ('grpc.max_receive_message_length', 50 * 1024 * 1024),
    ]
    conn = grpc.insecure_channel('0.0.0.0:5001', options=options)
    # conn = grpc.insecure_channel('0.0.0.0:5001', options=(('grpc.enable_http_proxy', 0),))
    client = pb2_grpc.BiliStub(channel=conn)
    # lesson 3
    try:
        response, call = client.HelloDewei.with_call(
            pb2.HelloDeweiReq(
                name='superggn',
                age=26,
            ),
            compression=grpc.Compression.Gzip,
            metadata=(
                ('client_key', 'client_value'),
                ('client_k', 'client_v'),
                ('name', 'dewei'),
            ),
            wait_for_ready=True,
        )
        # print('response.result', response.result)
        headers = call.trailing_metadata()
        print('headers', headers[0].key)
        print('result', response.result)
        # print('nihao', response.get('nihao'))
        print('dir(response)', dir(response))
        print()
        print('response.ListFields()', response.ListFields())
        # help(client.HelloDewei.with_call)
    except Exception as e:
        # print(dir(e))
        print('e.code()', e.code())
        print('e.code().name', e.code().name)
        print(type(e.code().name))
        print('e.code().value', e.code().value)
        print('e.details()', e.details())
    # lesson 4 请求非流，返回流
    # response = client.TestClientRecvStream(pb2.TestClientRecvStreamRequest(
    #     data='close',
    # ))
    # for item in response:
    #     print(item.result)
    # lesson 5 请求流，返回非流
    # response = client.TestClientSendStream(test())
    # print(response.result)
    # lesson 6 双向流
    # response = client.TestTwoWayStream(test(), timeout=10)
    # for res in response:
    #     print(res.result)


if __name__ == '__main__':
    # import requests
    #
    # resp = requests.get('https://www.baidu.com')
    # print('resp', resp)
    run()
