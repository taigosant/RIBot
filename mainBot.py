import telepot
from telepot.loop import MessageLoop
from Bot import Bot



neobot = telepot.Bot("409078068:AAHJyyAOYOv7WkOqqLOxFhGHNn81nHoKxZs")

neobot = Bot(neobot)

MessageLoop(neobot.robot, {'chat': neobot.recebendoMsg,
                       'callback_query': neobot.crawlingback}).run_as_thread()

while True:
    pass