from typing import NamedTuple, Callable
import time
import types
import functools
import threading

ns_to_microsecond = 1 / 1000
ns_to_millisecond = 1 / 1000000
ns_to_second = 1 / 1000000000


class TaskDataType:
    def __init__(self,
                 unique_id: int,
                 fnc_name: str,
                 fnc: Callable,
                 args: any,
                 kwargs: any,
                 interval: int,
                 lpt: int):
        self.unique_id = unique_id
        self.fnc_name = fnc_name
        self.fnc = fnc
        self.args = args
        self.kwargs = kwargs
        self.interval = interval  # millisecond
        self.last_performed_time = lpt
        self.last_duration = 0


class CustomTimer:
    def __init__(self):
        self.__taskList = list()
        self.__function_address_list = list()
        self.__id_counter = 0
        pass

    def __initTimer__(self):
        for func in self.__function_address_list:
            func()

    def run(self, block=True):
        self.__initTimer__()
        wait_times = list()
        # if there is no registered task, return immediately with warning message
        if len(self.__function_address_list) == 0:
            print("[WARNING] There is no registered task so CustomTimer, run nothing")
            return

        def operation():
            while True:
                #  main driver
                for task in self.__taskList:
                    elapsed_time = (time.perf_counter_ns() * ns_to_millisecond) - task.last_performed_time
                    if elapsed_time >= task.interval:
                        # perform  function
                        start_time = (time.perf_counter_ns() * ns_to_millisecond)
                        task.fnc(*task.args, **task.kwargs)
                        task.last_performed_time = (time.perf_counter_ns() * ns_to_millisecond)

                        duration = task.last_performed_time - start_time
                        task.last_duration = duration
                        wait_time = task.interval - duration
                        # print("function name:", task.fnc_name, "duration:", duration, "wait_time:", wait_time)
                        if wait_time > 0.0:
                            wait_times.append(wait_time)
                    else:
                        remaining_time = task.interval - elapsed_time
                        if remaining_time > 0.0:
                            wait_times.append(remaining_time)

                if len(wait_times) > 0:
                    min_wait_time = min(wait_times)
                    if min_wait_time > 1:
                        time.sleep(min_wait_time / 1000)  # sleep for better cpu performance
                    wait_times.clear()

        if block:
            operation()
        else:
            thread = threading.Thread(target=operation, name="Custom Timer non-blocking thread")
            thread.start()

    def register(self, func):
        self.__function_address_list.append(func)

    def periodic_task(self, interval=1000):
        def decorator(func):
            def inner_task(*args, **kwargs):
                last_elapsed_time_millisecond = time.perf_counter_ns() * ns_to_millisecond
                periodic_data_type = TaskDataType(self.__id_counter,
                                                  func.__name__,
                                                  func,
                                                  args,
                                                  kwargs,
                                                  interval,
                                                  last_elapsed_time_millisecond)
                self.__taskList.append(periodic_data_type)
                self.__id_counter += 1

            return inner_task
        return decorator

    def get_time_stamp_ns(self):
        return time.perf_counter_ns()

    def get_time_stamp_us(self):
        return time.perf_counter_ns() * ns_to_microsecond

    def get_time_stamp_ms(self):
        return time.perf_counter_ns() * ns_to_millisecond

    def get_time_stamp_s(self):
        return time.perf_counter_ns() * ns_to_second

    def getTaskCount(self):
        return self.__id_counter


#      ######################################################################
#      ######################################################################
# TEST ######################################################################
#      ######################################################################
#      ######################################################################

customTimer = CustomTimer()


@customTimer.register
@customTimer.periodic_task(interval=1000)
def print_hi1():
    print(f'Hi print_hi - 1', time.perf_counter_ns() * ns_to_second)


@customTimer.register
@customTimer.periodic_task(interval=2000)
def print_hi2():
    print(f'Hi2 print_hi - 2', time.perf_counter_ns() * ns_to_second)


@customTimer.register
@customTimer.periodic_task(interval=1000)
def print_hi3():
    print(f'Hi3 print_hi - 3', time.perf_counter_ns() * ns_to_second)


@customTimer.register
@customTimer.periodic_task(interval=2000)
def print_hi4():
    print(f'Hi4 print_hi - 4', time.perf_counter_ns() * ns_to_second)

# If test is needed then uncommented below section
# customTimer.run(block=False)
