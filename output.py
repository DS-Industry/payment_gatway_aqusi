import os
from multiprocessing import shared_memory, resource_tracker


def file_read():
    if os.path.exists("/home/root/CODESYS_WRK/py/output.txt"):
        f = open('/home/root/CODESYS_WRK/py/output.txt')
        status = f.read()
        f.close()
        os.remove("/home/root/CODESYS_WRK/py/output.txt")
        return status
    else:
        return '50'

def create_sm_output(status):
    SHM_NAME = 'cds_output'
    shm = shared_memory.SharedMemory(name=SHM_NAME, create=True, size=16)
    shm.buf[0] = int(status)
    resource_tracker.unregister(shm._name, 'shared_memory')
    print("Save data output")

def main():
    status = file_read()
    create_sm_output(status)


if __name__ == '__main__':
    print(f'Started')
    main()