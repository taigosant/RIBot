# coding: utf-8

# ## Bot Telegram paito

# In[3]:

#
import nltk
from telepot.loop import MessageLoop
import telepot
import random
import Search as se
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove


class Bot(object):
    def __init__(self, bot):
        self._editor = {}
        self._keyboard_msg_ident = {}
        self.places = ['Walmart', 'Casas Bahia', 'Bemol', 'Salao Top', 'Salao Rainha', 'Salao Sempre Bela']
        self.__search = {}
        self.__precos = {}
        self.__users = {}
        self.robot = bot
        self.re_greetings = ["yay", "Ola!! Deseja pedir algo?", "oie, deseja alguma coisa?"]
        # self.place = se.data['loja']['nome']
        self.__categorias= {}
        # print(self.__categorias)

        with open('greeting.txt', 'r') as f:
            self.greetings = f.read()
        f.close()
        self.greetings = self.greetings.split('\n')

        # print place


        # print greetings


    # In[ ]:
    def catalogo(self,chatID, key =None):
        if key is not None:
            for item in self.__search[chatID].services:
                if item['id'] == key:
                    categoria = item['nome']
                    break

            produtos = []
            for x in self.__search[chatID].data['servicos']:
                if x['categoria'] == key:
                    if len(x['nome'].split(" ")) > 4:
                        nome = " ".join(x['nome'].split()[:4])
                    else:
                        nome = x['nome']
                    produtos.append((nome, x['preco']))
            # print(produtos)

            sent = self.robot.sendMessage(chatID, "Categoria: " + categoria, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=prod + "; Preço: " + preco, callback_data=prod)] for prod, preco in produtos]))
        else:
            sent = self.robot.sendMessage(chatID, "Este é o nosso Menu ;) ", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=category, callback_data=category)] for category in self.__categorias[chatID].keys()]))

        self._keyboard_msg_ident[chatID] = telepot.message_identifier(sent)
        self._editor[chatID] = telepot.helper.Editor(self.robot, self._keyboard_msg_ident[chatID])

    def encerraPedido(self,chatID):
        total = 0
        if self.__users[chatID]['pedido']:
            self.__users[chatID]['status'] = 3
            for i in range(0, len(self.__users[chatID]['pedido'])):
                total += float(self.__precos[self.__users[chatID]['pedido'][i]])
            pedido = ", ".join(self.__users[chatID]['pedido'])
            self.robot.sendMessage(chatID, "Pedido Atual: " + pedido)
            self.robot.sendMessage(chatID, "Valor Total: " + str(total))
            sent = self.robot.sendMessage(chatID, 'Deseja encerrar este pedido ?',
                                          reply_markup=ReplyKeyboardMarkup(keyboard=[
                                              [KeyboardButton(text="sim ( ͡~ ͜ʖ ͡°)"), KeyboardButton(text="nao")]],
                                              one_time_keyboard=True))
            self._keyboard_msg_ident[chatID] = telepot.message_identifier(sent)
        else:
            self.robot.sendMessage(chatID, "Ainda não há nenhum pedido :c ")
            self.__users[chatID]['status'] = 1

    def encerraFinal(self, chatID):
        print("nome:" + self.__users[chatID]['nome']+"\n Pedido: "+ str(self.__users[chatID]['pedido']))
        self.__users[chatID]['pedido'] = []
        self.robot.deleteMessage(self._keyboard_msg_ident[chatID])
        self.robot.sendMessage(chatID, "Muito obrigado, seu pedido foi encaminhado com sucesso :D, pode pedir o que mais desejar <3", reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
        self.__users[chatID]['status'] = 1


    def addProdConfirmation(self,chatID, prod):
        self.__users[chatID]['status'] = 2
        sent = self.robot.sendMessage(chatID, 'Deseja adicionar '+prod+' ao pedido?', reply_markup=ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="sim :)"), KeyboardButton(text="nao")]], one_time_keyboard=True))
        self.__users[chatID]['temporaryProd'] = prod
        self._keyboard_msg_ident[chatID] = telepot.message_identifier(sent)
        # self._editor[chatID] = telepot.helper.Editor(self.robot, self._keyboard_msg_ident[chatID)

    def addProdFinal(self,chatID):
        self.__users[chatID]['status'] = 1
        self.__users[chatID]['pedido'].append(self.__users[chatID]['temporaryProd'])
        self.__users[chatID]['temporaryProd'] = ''
        self.robot.deleteMessage(self._keyboard_msg_ident[chatID])
        self._editor[chatID].editMessageText(text="produto adicionado ao pedido :D, você pode usar /total para ver o pedido atual ou /remover se desejar retirar algum produto ;)")
        self.robot.sendMessage(chatID, "Muito obrigado :D, pode pedir o que mais desejar <3")
        # self.robot.sendMessage(chatID, "Serviço/Produto adicionado ao pedido :D "
        #                                "\nSe desejar mais alguma coisa, é só pedir ;)")
    def inicio(self, chatID, name):
        self.__categorias[chatID] = {}
        self.__users[chatID]['pedido'] = []
        if name != '':
            toSend = 'Ola ' + name + ". " + "Estou trabalhando com os seguintes estabelecimentos, Voce pode escolher o estabelicimento que lhe interessar ;) "
        else:
            toSend = "Hello Again. Estou trabalhando com os seguintes estabelecimentos, Voce pode escolher o estabelicimento que lhe interessar ;) "

        self.robot.sendMessage(chatID, toSend)
        sent = self.robot.sendMessage(chatID, "Escolha um",
                                      reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                          [InlineKeyboardButton(text=place, callback_data=place)]
                                          for place in self.places]))

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

                self._keyboard_msg_ident[chatID] = telepot.message_identifier(sent)
                self._editor[chatID] = telepot.helper.Editor(self.robot, self._keyboard_msg_ident[chatID])
        else:
            self.robot.sendMessage(chatID, "Não há produtos para serem removidos")

    def commands(self, chatID, msg):
        name = msg['chat']['first_name']
        sentence = msg['text']

        if sentence == '/total':
            self.total(chatID)
        elif sentence == '/remover':
            self.remover(chatID)
        elif sentence == '/catalogo':
            self.catalogo(chatID)
        elif sentence == '/confirmar':
            self.encerraPedido(chatID)
        elif sentence == '/voltar':
            self.__users[chatID]['status'] = 0
            self.inicio(chatID, '')
        else:
            self.robot.sendMessage(chatID, "Não reconheço este comando D:")


    def pedido(self, chatID, sentence):
        prods = None
        sent = None
        try:
            prods = self.__search[chatID].searchCategory(sentence)
        except:
            self.robot.sendMessage(chatID,"Desculpe, não consegui entender.")
        if prods:
            for i in range(0,len(prods)):
                if len(prods[i][0].split()) > 4:
                    nome = " ".join(prods[i][0].split()[:4])
                    prods[i] = (nome,prods[i][1])
            # print(prods)
            try:
                sent = self.robot.sendMessage(chatID, "Achei estes produtos, deseja algum?",
                                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                             [InlineKeyboardButton(text=prod + "; Preço: " + prec, callback_data=prod)]
                                             for (prod, prec) in prods]))
            except:
                sent = self.robot.sendMessage(chatID, "Temos estas categorias: ",
                                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                               [InlineKeyboardButton(text=prod, callback_data=prod)] for prod in prods]))
        else:
            self.robot.sendMessage(chatID, "Desculpe, não temos este serviço/produto D:")


        if sent:
            self._keyboard_msg_ident[chatID] = telepot.message_identifier(sent)
            self._editor[chatID] = telepot.helper.Editor(self.robot, self._keyboard_msg_ident[chatID])

    def recebendoMsg(self, msg):
        name = msg['chat']['first_name']
        sentence = str(msg['text'].lower())
        print(sentence, name)
        tipoMsg, tipoChat, chatID = telepot.glance(msg)
        if chatID not in self.__users.keys():
            self.__users[chatID] = {'nome': name, 'pedido': [], 'status': 0}

        if self.__users[chatID]['status'] == 0:
            if sentence == '/start':
                self.inicio(chatID,name)
            else:
                toSend = "Escolha um estabelecimento para começar por favor"
                self.robot.sendMessage(chatID, toSend)
                self.inicio(chatID, name)


        elif self.__users[chatID]['status'] == 1:
            if sentence in self.greetings:
                send = random.choice(self.re_greetings)
                self.robot.sendMessage(chatID,send)
            elif sentence.startswith('/'):
                self.commands(chatID, msg)
            else:
                self.pedido(chatID, sentence)
        elif self.__users[chatID]['status'] == 2:
            if sentence in ['sim :)','sim', 'si', 'yes', 'quero']:
                self.addProdFinal(chatID)
            elif sentence in ['não', 'nao', 'no']:
                self.__users[chatID]['status'] = 1
                self.robot.sendMessage(chatID, "Okay, Voce pode pedir outra coisa se quiser.", reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
            else:
                self.robot.sendMessage(chatID, "Por favor, escolha uma opção..")
        elif self.__users[chatID]['status'] == 3:
            if sentence in ['sim ( ͡~ ͜ʖ ͡°)', 'sim :)', 'sim', 'si', 'yes']:
                self.encerraFinal(chatID)
            elif sentence in ['não', 'nao', 'no']:
                self.__users[chatID]['status'] = 1
                self.robot.sendMessage(chatID, "Okay, Voce continuar fazendo seu pedido ;)", reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
            else:
                self.robot.sendMessage(chatID, "Por favor, escolha uma opção..")




    def crawlingback(self, msg):
        # tipoMsg, tipoChat, chatID = telepot.glance(msg)
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
        chatID = msg['from']['id']
        # message_id = msg['message']['message_id']
        if self.__users[chatID]['status'] == 0:
            if query_data in self.places:
                self.__users[chatID]['status'] = 1
                self.robot.answerCallbackQuery(query_id, text='entrando..')
                self.__search[chatID] = se.Search(query_data)
                self.robot.sendMessage(chatID,"Agora estou atendendo pelx " + query_data + ". Voce pode fazer um pedido, ver o /catalogo ou ver a lista de comandos digitando / ")
                for item in self.__search[chatID].services:
                    # print(self.__search.services)
                    if len(item['nome'].split()) > 4:
                        nome = " ".join(item['nome'].split()[:4])
                    else:
                        nome = item['nome']
                    self.__categorias[chatID][nome] = item['id']


                for item in self.__search[chatID].data['servicos']:
                    if len(item['nome'].split()) > 4:
                        nome = " ".join(item['nome'].split()[:4])
                    else:
                        nome = item['nome']
                    self.__precos[nome] = item['preco']
        elif self.__users[chatID]['status'] == 1:
            if query_data.startswith('remover'):
                toberemoved = query_data.replace('remover','')
                self.remover(chatID, toberemoved)
                self.robot.answerCallbackQuery(query_id, text='removendo..')
                self._editor[chatID].editMessageReplyMarkup(reply_markup=None)
                self._editor[chatID].editMessageText(text="removido com sucesso :D")
            elif query_data in self.__categorias[chatID].keys():
                self.catalogo(chatID, self.__categorias[chatID][query_data])
                # self._editor[chatID].editMessageReplyMarkup(reply_markup=None)
            else:
                self._editor[chatID].editMessageReplyMarkup(reply_markup=None)
                self.addProdConfirmation(chatID, query_data)
        else:
            self.robot.answerCallbackQuery(query_id, text='...')
