import threading
import time
import argparse

parser = argparse.ArgumentParser()
group1 = parser.add_mutually_exclusive_group()
group2 = parser.add_mutually_exclusive_group()
group1.add_argument("-v","--verbose", action="store_true")
group1.add_argument("-q","--quiet", action="store_true")
group2.add_argument("-a", action="store")
group2.add_argument("-b", action="store")
args = parser.parse_args()

print(args.verbose)
print(args.quiet)
print(args.a)
print(args.b)

def test():
    time.sleep(1)
    print(threading.currentThread().getName())
    time.sleep(10)

th = []
for i in range(10):
    t = threading.Thread(target=test, args=())
    th.append(t)

#for t in th:
#    t.setDaemon(True)
#    t.start()
#for t in th:
#    t.join()

#print("main end")
