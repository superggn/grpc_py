import signal
import sys

import grpc

import eos_utils_pb2
import eos_utils_pb2_grpc

# 关于这个 channel 的 clean up, 其实可以不做
# EOS_CHANNEL = grpc.insecure_channel('my-service.my-namespace.svc.cluster.local:50051')
EOS_CHANNEL = grpc.insecure_channel('127.0.0.1:50051')


def fetch_eos_balance(address):
    stub = eos_utils_pb2_grpc.BlockInfoStub(EOS_CHANNEL)
    response = stub.FetchBlockInfo(eos_utils_pb2.FetchRequest(address=address))
    return response.balance_photons


def cleanup():
    if EOS_CHANNEL is not None:
        EOS_CHANNEL.close()
        print("Channel closed.")


def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    cleanup()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


def setup_signal_handlers():
    # signal.signal 放在外面可能会和外部使用的 signal handler 冲突， 放在函数里让调用灵活点
    signal.signal(signal.SIGINT, signal_handler)


print(fetch_eos_balance('my eos addr v0'))
