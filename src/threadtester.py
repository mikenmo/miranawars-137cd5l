import threading
import time


class Person:
    def __init__(self,name):
        self.name = name
    def hello(self):
        for i in range(0,10):
            print("Hello im ",self.name)
            time.sleep(1)

p = Person("kenneth")

t = threading.Thread(target = p.hello, name='pthread',args = [])
t.start()
time.sleep(2)
p.name = "not kenneth"