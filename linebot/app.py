import os
import sys

from flask import Flask, jsonify, request, abort, send_file
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FollowEvent, UnfollowEvent

from fsm import TocMachine
from utils import send_text_message

load_dotenv()  #可以用os.getevn去取.env裡的東西

machine = TocMachine(
    states=["user", "home", "playing", "win"],
    transitions=[
        {
            "trigger": "start",
            "source": "user",
            "dest": "home",
            "conditions": "user_is_going_to_home",
        },
        {
            "trigger": "selectmode",
            "source": "home",
            "dest": "playing",
            "conditions": "home_is_going_to_playing",
        },
        {
            "trigger": "selectmode",
            "source": "home",
            "dest": "user",
            "conditions": "home_is_going_to_user",
        },
        {
            "trigger": "guess",
            "source": "playing",
            "dest": "playing",
            "conditions": "playing_is_going_to_playing",
        },
        {
            "trigger": "guess",
            "source": "playing",
            "dest": "win",
            "conditions": "playing_is_going_to_win",
        },
        {
            "trigger": "go_back",
            "source": ["win"],
            "dest": "user",
        },
    ],
    initial="user",
    auto_transitions=False,
    show_conditions=True,
)

app = Flask(__name__, static_url_path="")


# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv("LINE_CHANNEL_SECRET", None)
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)
if channel_secret is None:
    print("Specify LINE_CHANNEL_SECRET as environment variable.")
    sys.exit(1)
if channel_access_token is None:
    print("Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.")
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)

userstate = {'userid': 'state'}

@app.route("/")
def hello():
    return "hello world"

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue

        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=event.message.text)
        )

    return "OK"


@app.route("/webhook", methods=["POST"])
def webhook_handler():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info(f"Request body: {body}")

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    line_bot_api = LineBotApi(channel_access_token)
    profile = line_bot_api.get_profile(events[0].source.user_id)


    # if event is FollowEvent
    for event in events:
        if not isinstance(event, FollowEvent):
            continue
        line_bot_api.push_message(profile.user_id, TextSendMessage(text=f"嗨~ {profile.display_name} \udbc0\udc0b\n感謝您將本帳號加入好友\udbc0\udc04\n\udbc0\udc77輸入\"終極密碼start\"啟動遊戲\udbc0\udc77"))
        if userstate.__contains__(profile.user_id): # 清空之前state
            del userstate[profile.user_id]

    if not userstate.__contains__(events[0].source.user_id): # 新用戶
        userstate[events[0].source.user_id] = "user"
    nowstate = userstate[events[0].source.user_id]
    for key, value in userstate.items() :
        print (key, value)
        print ("\n")
    machine.state = nowstate

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        if not isinstance(event.message.text, str):
            continue
        print(f"\nFSM STATE: {machine.state}")
        print(f"REQUEST BODY: \n{body}")
        # line_bot_api.push_message(event.source.user_id, TextSendMessage(text='\uDBC0\uDC84Hello World!'))

        if machine.state == "user":
            response = machine.start(event)
            if response == False:
                send_text_message(event.reply_token, "...")

        elif machine.state == "home":
            response = machine.selectmode(event)
            if response == False:
                send_text_message(event.reply_token, "\udbc0\udc2d遊戲開始\udbc0\udc2d \n\udbc0\udc41輸入\'1\'開始遊戲\n\udbc0\udc41輸入\'exit\'離開遊戲")

        elif machine.state == "playing":
            response = machine.guess(event)
            if response == False:
                send_text_message(event.reply_token, "請重新輸入")
        
        userstate[event.source.user_id] = machine.state
        

    return "OK"


@app.route("/show-fsm", methods=["GET"])
def show_fsm():
    machine.get_graph().draw("fsm.png", prog="dot", format="png")
    return send_file("fsm.png", mimetype="image/png")


if __name__ == "__main__":
    port = os.environ.get("PORT", 8000)
    app.run(host="0.0.0.0", port=port, debug=True)
