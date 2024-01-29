from concurrent import futures

import grpc

import eos_utils_pb2
import eos_utils_pb2_grpc


class BlockInfoServicer(eos_utils_pb2_grpc.BlockInfoServicer):
    def FetchBlockInfo(self, request, context):
        print('request', request)
        balance_amount = 1234
        address = request.address
        return eos_utils_pb2.FetchReply(balance_photons=balance_amount, address=address)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    eos_utils_pb2_grpc.add_BlockInfoServicer_to_server(BlockInfoServicer(), server)
    server.add_insecure_port('127.0.0.1:50051')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
