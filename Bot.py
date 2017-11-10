# coding: utf-8

# ## Bot Telegram paito

# In[3]:

#
import nltk
from telepot.loop import MessageLoop
import telepot
import random
import Search as se
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


class Bot(object):
    def __init__(self, bot):
        self.__status = None
        self.__precos = se.precos
        self.__users = {}
        self.robot = bot
        self.re_greetings = ["yay", "Ola!! Deseja pedir algo?", "oie, deseja alguma coisa?"]
        self.place = se.data['loja']['nome']
        self.__categorias= {}
        # print(self.__categorias)

        for item in se.services:
            self.__categorias[item['nome']] = item['id']
        print(self.__categorias['cabelo'])
        with open('greeting.txt', 'r') as f:
            self.greetings = f.read()
        f.close()
        self.greetings = self.greetings.split('\n')

        # print place


        # print greetings


    # In[ ]:
    def catalogo(self,chatID, key =None):
        if key is not None:
            for item in se.services:
                if item['id'] == key:
                    categoria = item['nome']
                    break

            produtos = []
            for x in se.data['servicos']:
                if x['categoria'] == key:
                    produtos.append((x['nome'], x['preco']))

            sent = self.robot.sendMessage(chatID, "Categoria: " + categoria, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=prod + "; Preço: " + preco, callback_data=prod)] for prod, preco in
                produtos]))
        else:
            sent = self.robot.sendMessage(chatID, "Este é o nosso Menu ;) ", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=category, callback_data=category)] for category in self.__categorias.keys()]))

        self._keyboard_msg_ident = telepot.message_identifier(sent)
        self._editor = telepot.helper.Editor(self.robot, self._keyboard_msg_ident)

    def encerraPedido(self,chatID):
        total = 0
        if self.__users[chatID]['pedido']:
            for i in range(0, len(self.__users[chatID]['pedido'])):
                total += float(self.__precos[self.__users[chatID]['pedido'][i]])
            pedido = ", ".join(self.__users[chatID]['pedido'])
            self.robot.sendMessage(chatID, "Pedido Atual: " + pedido)
            self.robot.sendMessage(chatID, "Valor Total: " + str(total))
            sent = self.robot.sendMessage(chatID, 'Deseja encerrar este pedido ?',
                                          reply_markup=ReplyKeyboardMarkup(keyboard=[
                                              [KeyboardButton(text="sim ( ͡~ ͜ʖ ͡°)"), KeyboardButton(text="nao")]],
                                              one_time_keyboard=True))
            self._keyboard_msg_ident = telepot.message_identifier(sent)
        else:
            self.robot.sendMessage(chatID, "Ainda não há nenhum pedido :c ")

    def encerraFinal(self, chatID):
        print("nome:" + self.__users[chatID]['nome']+"\n Pedido: "+ str(self.__users[chatID]['pedido']))
        self.__users[chatID]['pedido'] = []
        self.robot.deleteMessage(self._keyboard_msg_ident)
        self.robot.sendMessage(chatID, "Muito obrigado, seu pedido foi encaminhado com sucesso :D, pode pedir o que mais desejar <3")


    def addProdConfirmation(self,chatID, prod):
        sent = self.robot.sendMessage(chatID, 'Deseja adicionar '+prod+' ao pedido?', reply_markup=ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="sim :)"), KeyboardButton(text="nao")]], one_time_keyboard=True))
        self.__users[chatID]['temporaryProd'] = prod
        self._keyboard_msg_ident = telepot.message_identifier(sent)
        # self._editor = telepot.helper.Editor(self.robot, self._keyboard_msg_ident)

    def addProdFinal(self,chatID):
        self.__users[chatID]['pedido'].append(self.__users[chatID]['temporaryProd'])
        self.__users[chatID]['temporaryProd'] = ''
        self.robot.deleteMessage(self._keyboard_msg_ident)
        self._editor.editMessageText(text="produto adicionado ao pedido :D, você pode usar /total para ver o pedido atual ou /remover se desejar retirar algum produto ;)")
        self.robot.sendMessage(chatID, "Muito obrigado :D, pode pedir o que mais desejar <3")
        # self.robot.sendMessage(chatID, "Serviço/Produto adicionado ao pedido :D "
        #                                "\nSe desejar mais alguma coisa, é só pedir ;)")

    def total(self, chatID):
        total = 0
        if self.__users[chatID]['pedido']:
            for i in range(0, len(self.__users[chatID]['pedido'])):
                total += float(self.__precos[self.__users[chatID]['pedido'][i]])
            pedido = ", ".join(self.__users[chatID]['pedido'])
            self.robot.sendMessage(chatID, "Pedido Atual: " + pedido)
            self.robot.sendMessage(chatID, "Valor Total: " + str(total))
        else:
            self.robot.sendMessage(chatID, "Ainda não há nenhum pedido :c ")

    def remover(self, chatID, item=''):
        if self.__users[chatID]['pedido']:
            if item != '':
                for prod in self.__users[chatID]['pedido']:
                    if item == prod:
                        self.__users[chatID]['pedido'].remove(item)
            else:
                sent = self.robot.sendMessage(chatID, "Qual produto deseja remover? ",
                                            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                                [InlineKeyboardButton(text=prod, callback_data="remover" + prod)] for
                                                prod in self.__users[chatID]['pedido']]))

                self._keyboard_msg_ident = telepot.message_identifier(sent)
                self._editor = telepot.helper.Editor(self.robot, self._keyboard_msg_ident)
        else:
            self.robot.sendMessage(chatID, "Não há produtos para serem removidos")

    def commands(self, chatID, msg):
        name = msg['chat']['first_name']
        sentence = msg['text']
        if sentence == '/start':
            # self.robot.sendMessage(chatID, "oi")
            toSend = 'Ola ' + name + ". " + "Estou atendendo pelx " + self.place + ". Voce pode fazer um pedido, ver o /catalogo ou ver a lista de comandos digitando / "
            self.robot.sendMessage(chatID, toSend)

        elif sentence == '/total':
            self.total(chatID)
        elif sentence == '/remover':
            self.remover(chatID)
        elif sentence == '/catalogo':
            self.catalogo(chatID)
        elif sentence == '/confirmar':
            self.encerraPedido(chatID)
        else:
            self.robot.sendMessage(chatID, "Não reconheço este comando D:")


    def pedido(self, chatID, sentence):
        prods = None
        sent = None
        try:
            prods = se.searchCategory(sentence)
        except:
            self.robot.sendMessage(chatID,"Desculpe, não consegui entender.")
        if prods:
            try:
                sent = self.robot.sendMessage(chatID, "Achei estes produtos, deseja algum?",
                                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                             [InlineKeyboardButton(text=prod + "; Preço: " + prec, callback_data=prod)]
                                             for (prod, prec) in prods]))
            except:
                sent = self.robot.sendMessage(chatID, "Temos estas categorias: ",
                                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                               [InlineKeyboardButton(text=prod, callback_data=prod)] for prod in prods]))


        if sent:
            self._keyboard_msg_ident = telepot.message_identifier(sent)
            self._editor = telepot.helper.Editor(self.robot, self._keyboard_msg_ident)

    def recebendoMsg(self, msg):
        name = msg['chat']['first_name']
        sentence = str(msg['text'].lower())
        print(sentence,name)
        tipoMsg, tipoChat, chatID = telepot.glance(msg)
        if chatID not in self.__users.keys():
            self.__users[chatID] = {'nome': name, 'pedido': []}

        if sentence in self.greetings:
            send = random.choice(self.re_greetings)
            self.robot.sendMessage(chatID,send)
        elif sentence == 'sim :)':
            self.addProdFinal(chatID)
        elif sentence == "sim ( ͡~ ͜ʖ ͡°)":
            self.encerraFinal(chatID)
        elif sentence == 'nao':
            self.robot.sendMessage(chatID, "Okay, Voce pode pedir outra coisa se quiser.")
        elif sentence.startswith('/'):
            self.commands(chatID, msg)
        else:
            self.pedido(chatID, sentence)


    def crawlingback(self, msg):
        # tipoMsg, tipoChat, chatID = telepot.glance(msg)
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
        chatID = msg['from']['id']
        # message_id = msg['message']['message_id']
        if query_data.startswith('remover'):
            toberemoved = query_data.replace('remover','')
            self.remover(chatID, toberemoved)
            self.robot.answerCallbackQuery(query_id, text='removendo..')
            self._editor.editMessageReplyMarkup(reply_markup=None)
            self._editor.editMessageText(text="removido com sucesso :D")
        elif query_data in self.__categorias.keys():
            self.catalogo(chatID, self.__categorias[query_data])
            # self._editor.editMessageReplyMarkup(reply_markup=None)
        else:
            self._editor.editMessageReplyMarkup(reply_markup=None)
            self.addProdConfirmation(chatID, query_data)

        # __users[chatID].append(query_data)
        # print(__users[chatID])
        # self.robot.answerCallbackQuery(query_id, text='adicionado ao pedido')
        # self._editor.editMessageReplyMarkup(reply_markup=None)
        # self._editor.editMessageText(text="produto adicionado ao pedido :D, você pode usar /total para ver o pedido atual ou /remover se desejar retirar algum produto ;)")
        # self.robot.sendMessage(chatID, "Muito obrigado :D, pode pedir o que mais desejar <3")
        # confirmarpedido(chatID)

