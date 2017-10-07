import os
import json
import telepot
import requests
from   flask          import Flask, jsonify, request, make_response
from   flask_httpauth import HTTPBasicAuth

app      = Flask(__name__)
auth     = HTTPBasicAuth()
tgmtoken = os.environ['TGM-TOKEN']

@auth.get_password
def get_password(username):
    if username == 'ansi':
        return 'test'
    return None


@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)


def prepareanswer(r, msg):
    #print(json.dumps(r, indent=2, sort_keys=True))

    if 'action' in r['chat']['output']:

        if r['chat']['output']['action'] == "EatDrink":
            print("Bring %s to %s" % (r['chat']['context']['DrinkOrFood'], msg['from']['username']))

    return r['chat']['output']['text'][0]

def handle(msg):
    uID    = msg['from']['id']
    uName  = msg['from']['username']
    uFName = msg['from']['first_name']
    text   = msg['text']
    r      = json.loads(requests.post('http://conversation:8011/api/v1.0/conversation/process',
                                      json={'text': text, "telegramid": uID},
                                      auth=('ansi', 'test')
                                      ).content
                        )
    bot.sendMessage(uID, prepareanswer(r, msg))


bot  = telepot.Bot(tgmtoken)
bot.message_loop(handle)
bot.sendMessage(276371592, 'Start Feelflight Bot')


@app.route('/api/v1.0/chat/send', methods=['POST'])
@auth.login_required
def process_text():
    r = request.get_json(silent=True)
    if r is not None and 'text' in r:
        text = r['text']
        uID  = int(r['uid'])
        bot.sendMessage(uID, text)
        return make_response(jsonify({'done': 'done'}), 200)
    return make_response(jsonify({'error': 'Not a valid json'}), 401)


if __name__ == '__main__':
    app.run(host="::", port=8020)
