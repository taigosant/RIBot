import telepot
from telepot.loop import MessageLoop
from Bot import Bot



neobot = telepot.Bot("485412513:AAGm7pe6DVEO-btyDcRwzjMNQBI-7zdo-SU")

neobot = Bot(neobot)

MessageLoop(neobot.robot, {'chat': neobot.recebendoMsg,
                       'callback_query': neobot.crawlingback}).run_as_thread()

while True:
    pass