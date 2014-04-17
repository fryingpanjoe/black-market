from os import fork
from time import sleep


SHARED_STATE = 0


def set_shared_state(st):
    global SHARED_STATE
    SHARED_STATE = st


def main():
    print('before fork')
    pid = fork()
    print('after fork pid=%d' % pid)
    if pid != 0:
        print('setting shared state to %d' % pid)
        set_shared_state(pid)
    else:
        sleep(1)
    global SHARED_STATE
    print('pid %d says shared state is %d' % (pid, SHARED_STATE))


if __name__ == '__main__':
    main()
