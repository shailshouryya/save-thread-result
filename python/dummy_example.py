import random
import threading
import time

from save_thread_result import ThreadWithResult


def function_to_thread(n):
    count = 0
    while count < 3:
        print('Still running ' + threading.current_thread().name + '...')
        count += 1
        time.sleep(3)
    result = random.random()
    print('Return value of ' + threading.current_thread().name + ' should be: ' + str(result))
    return result

def main():
    thread1 = ThreadWithResult(target=function_to_thread, args=(1,))
    thread2 = ThreadWithResult(target=function_to_thread, args=(2,))
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()
    print('The `result` attribute of ' + thread1.name +  ' is: ' + str(thread1.result))
    print('The `result` attribute of ' + thread2.name +  ' is: ' + str(thread2.result))


if __name__ == '__main__':
    main()
