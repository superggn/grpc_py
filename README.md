# Python grpc workflow

##### 概述

python 写逻辑

grpc 定义接口

先写一个 proto 文件， 定义一下数据结构和函数签名

用 grpc 跑一下这个 proto 文件， 生成可以被 python 导入的包

在 server.py 和 client.py 里就可以愉快地写逻辑了

##### xxx.proto

能定义 service, rpc, message

##### 生成出来的 pb2 文件都放什么

xxx_pb2_grpc => 放 server, rpc

xxx_pb2 => 放 request, response （message）

##### server.py

servicer_class (派生自 proto 文件中的 service)

grpc.server + threadpool => server

xxx_pb2_grpc.add_xxx_servicer_to_server(servicer_class(), server)

server.add_insecure_port('localhost:50052')

server.start()

server.wait_for_termination()

##### client.py

rpc 分 unary 和 stream 的

```python3
# unary 单次调用
with grpc.insecure_channel('ip:port') as channel:
    stub = xxx_pb2_grpc.ServiceNameStub(channel)
    # 这里的 message 也可以叫 response
    message = stub.rpc_name(xxx_pb2.MessageName())
    
    
# stream 的 rpc 就是接受一个不停 yield message 的函数， 无入参
# unary 的 rpc 就是接一个 message
```

##### stub => client side proxy

在 client side 当 server 的替身 => 在 client side 调 server 的 rpc 就是 stub.xxx_rpc



##### 参考链接

https://github.com/grpc/grpc/tree/master/examples/python/auth

https://github.com/grpc/grpc/blob/master/examples/python/auth/customized_auth_server.py

https://github.com/grpc/grpc/blob/master/examples/python/auth/customized_auth_client.py

##### authentication - grpc 鉴权

###### client side

初始化 channel 的时候把 auth 打进去

写一个 metadata plugin, 和 channel credential 组合一下，丢到 channel 里

```python3
import grpc

METADATA_KEY = 'token'

class MetaPlugin(grpc.AuthMetadataPlugin):
    def __init__(self, token):
        self._token = token

    def __call__(self, context, callback):
        metadata = ((METADATA_KEY, self._token),)
        error = None
        callback(metadata, error)

MY_TOKEN = '...'
my_foo_plugin = MetaPlugin(MY_TOKEN)
# 单发
call_credentials = grpc.metadata_call_credentials(my_foo_plugin)
stub.FooRpc(request_message, credentials=call_credentials)

# stream
channel_credentials = grpc.ssl_channel_credentials()
call_credentials = grpc.metadata_call_credentials(my_foo_plugin)
composite_credentials = grpc.composite_channel_credentials(
    channel_credential,
    call_credentials)
channel = grpc.secure_channel(server_address, composite_credentials)

```



###### server side

写一个 interceptor / 拦截器, 在初始化 server 的时候传进去

(interceptor 类似 server 端的中间件)

```python3
import grpc

METADATA_KEY = 'token'
EXPECTED_TOKEN = '...'

class SignatureValidationInterceptor(grpc.ServerInterceptor):
    def __init__(self):
        def abort(ignored_request, context):
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "Invalid signature")

        self._abortion = grpc.unary_unary_rpc_method_handler(abort)

    def intercept_service(self, continuation, handler_call_details):
        # Example HandlerCallDetails object:
        #     _HandlerCallDetails(
        #       method=u'/helloworld.Greeter/SayHello',
        #       invocation_metadata=...)
        expected_metadata = (METADATA_KEY, EXPECTED_TOKEN)
        if expected_metadata in handler_call_details.invocation_metadata:
            return continuation(handler_call_details)
        else:
            return self._abortion
server = grpc.server(
    futures.ThreadPoolExecutor(),
    interceptors=(SignatureValidationInterceptor(),),
)

```







