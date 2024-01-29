# coding:utf-8
import time
from concurrent import futures

import grpc

import hello_bili_pb2 as pb2
import hello_bili_pb2_grpc as pb2_grpc


# 客户端与服务端相互传输与接收 headers key value
# 客户端与服务端相互传输与接收 进行压缩与解压缩

# 写一个拦截器的类
# 初始化 code detail
# 返回给客户端
# grpc_code 错误函数 abort
# intercept_service(self, continuation, headler_call_details)

def _abort(code, details):  # unary, stream
    def terminate(ignored_request, context):
        context.abort(code, details)

    return grpc.unary_unary_rpc_method_handler(terminate)


class TestInterceptor(grpc.ServerInterceptor):
    def __init__(self, key, value, code, detail):
        self.key = key
        self.value = value
        self._abort = _abort(code, detail)

    def intercept_service(self, continuation, handler_call_details):
        # continuation 函数执行器
        # hanfler_call_details header
        headers = dict(handler_call_details.invocation_metadata)
        print('headers', headers)
        print('handler_call_details.invocation_metadata', handler_call_details.invocation_metadata)
        if (self.key, self.value) not in handler_call_details.invocation_metadata:
            return self._abort
        return continuation(handler_call_details)


class Bili(pb2_grpc.BiliServicer):
    def HelloDewei(self, request, context):
        name = request.name
        age = request.age
        # lesson 7
        # sub_code = 40301
        # context.set_details(json.dumps({'code': sub_code, 'msg': '...'}))
        # context.set_details('haha bug')
        # context.set_code(grpc.StatusCode.DATA_LOSS)
        # raise context
        # lesson 8
        context.set_trailing_metadata(
            (('name', 'dewei'), ('key', 'value'))
        )
        headers = context.invocation_metadata()
        # print(headers[0].key)
        # print(headers[0].value)
        result = f'my name is {name}, i am {age} years old'
        context.set_compression(grpc.Compression.Gzip)  # 还有一种叫 Deflate
        return pb2.HelloDeweiReply(result=result)

    def TestClientRecvStream(self, request, context):
        # 客户端还活着
        index = 0
        while context.is_active():
            data = request.data
            if data == 'close':
                print('data is close, request will cancel')
                context.cancel()
            time.sleep(1)
            index += 1
            result = f'send {index} {data}'
            # print(result)
            yield pb2.TestClientRecvStreamResponse(
                result=result,
            )

    def TestClientSendStream(self, request_iterator, context):
        index = 0
        for request in request_iterator:
            # print(request.data, index)
            if index == 10:
                break
            index += 1

        return pb2.TestClientSendStreamResponse(
            result='ok',
        )

    def TestTwoWayStream(self, request_iterator, context):
        index = 0
        for request in request_iterator:
            data = request.data
            if index == 3:
                # 强制断开，此时客户端报错
                context.cancel()
            index += 1
            result = f'service send client {data}'
            yield pb2.TestTwoWayStreamResponse(result=result)


def run():
    validator = TestInterceptor('name',
                                'dewei',
                                grpc.StatusCode.UNAUTHENTICATED,
                                'Access Denied',
                                )
    grpc_server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=4),
        # 在服务端设置 compression
        compression=grpc.Compression.Gzip,
        options=[
            ('grpc.max_sned_message_length', 50 * 1024 * 1024),
            ('grpc.max_receive_message_length', 50 * 1024 * 1024),
        ],
        interceptors=(validator,),
    )
    pb2_grpc.add_BiliServicer_to_server(Bili(), grpc_server)
    port = 5001
    grpc_server.add_insecure_port(f'0.0.0.0:{port}')
    grpc_server.start()
    print(f'server will start at 0.0.0.0:{port}')
    try:
        while 1:
            time.sleep(3600)
    except KeyboardInterrupt:
        grpc_server.stop(0)


if __name__ == '__main__':
    # import requests
    # resp = requests.get('https://www.baidu.com')
    # print('resp', resp)
    run()
