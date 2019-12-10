from transitions.extensions import GraphMachine

from utils import send_text_message
import random

minnum = 1
maxnum = 100

user_minnum = {'userid': 'minnum'}
user_maxnum = {'userid': 'maxnum'}
user_ans = {'userid': 'ans'}



class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(model=self, **machine_configs)

    def user_is_going_to_home(self, event):
        text = event.message.text
        return text == "終極密碼start"

    def home_is_going_to_playing(self, event):
        global minnum
        global maxnum
        global ans
        if not user_minnum.__contains__(event.source.user_id):
            user_minnum[event.source.user_id] = 1
        minnum = user_minnum[event.source.user_id]
        if not user_maxnum.__contains__(event.source.user_id):
            user_maxnum[event.source.user_id] = 100
        maxnum = user_maxnum[event.source.user_id]
        if not user_ans.__contains__(event.source.user_id):
            user_ans[event.source.user_id] = random.randint(1,100)

        text = event.message.text
        return text == "1"

    def home_is_going_to_user(self, event):
        text = event.message.text
        if text.lower() == "exit":
            reply_token = event.reply_token
            send_text_message(reply_token, "Byebye\udbc0\udc31\n\udbc0\udc77輸入\"終極密碼start\"啟動遊戲\udbc0\udc77")
        return text.lower() == "exit"

    def playing_is_going_to_playing(self, event):
        global minnum
        global maxnum
        for key, value in user_minnum.items() :
            print (key, value)
            print ("\n")
        for key, value in user_maxnum.items() :
            print (key, value)
            print ("\n")
        for key, value in user_ans.items() :
            print (key, value)
            print ("\n")
        minnum = user_minnum[event.source.user_id]
        maxnum = user_maxnum[event.source.user_id]
        ans = user_ans[event.source.user_id]

        text = event.message.text
        if( text.isnumeric() and int(text) >= minnum and int(text) <= maxnum ): # 回答在正確範圍
            if int(text) > ans or int(text) < ans: # 大於或小於
                if int(text) > ans:
                    maxnum = int(text)
                    user_maxnum[event.source.user_id] = maxnum
                else:
                    minnum = int(text)
                    user_minnum[event.source.user_id] = minnum
                return True

    def playing_is_going_to_win(self, event):
        text = event.message.text
        return text == str(user_ans[event.source.user_id])

    


    def on_enter_home(self, event):
        print("I'm entering home")

        reply_token = event.reply_token
        send_text_message(reply_token, "\udbc0\udc2d遊戲開始\udbc0\udc2d \n\udbc0\udc41輸入\'1\'開始遊戲\n\udbc0\udc41輸入\'exit\'離開遊戲")

    def on_enter_playing(self, event):
        print("I'm entering playing")

        global minnum
        global maxnum
        reply_token = event.reply_token
        send_text_message(reply_token, "請輸入%d ~ %d數字\udbc0\udc7f" % (minnum, maxnum))

    def on_enter_win(self, event):
        print("I'm entering win")

        global minnum
        global maxnum
        minnum = 1
        maxnum = 100
        del user_minnum[event.source.user_id]
        del user_maxnum[event.source.user_id]
        del user_ans[event.source.user_id]
        # user_minnum[event.source.user_id] = 1
        # user_maxnum[event.source.user_id] = 100
        # user_ans[event.source.user_id] = random.randint(1,100)
        reply_token = event.reply_token
        send_text_message(reply_token, "\udbc0\udc73YOU GOT IT!\udbc0\udc73\n\n----------------------遊戲結束----------------------\n\udbc0\udc77輸入\"終極密碼start\"啟動遊戲\udbc0\udc77")
        self.go_back()