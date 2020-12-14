from flask import Flask, render_template, send_file, request
import seaborn as sns
import pandas as pd
import numpy as np
import time
import telegram



app = Flask(__name__)

TOKEN="1401512910:AAGBK1rpry44b3S6Xt-FePKWO7QE-Wm0PNI"
bot = telegram.Bot(token=TOKEN)
URL = "https://dsba-201-1-pilot.herokuapp.com/"

links = {"Pairplot" : "pairplot",
         "Download" : "download",
         "Fair vs pclass" : "fair_vs_pclass",
         "Pclass vs Sex" : "pclass_vs_sex"}

def render_index (image = None):
    return render_template("index.html", links=links, image = image, code=time.time())

@app.route('/', methods=['GET'])
def main_route():
    return render_index ()


@app.route('/download', methods=['GET'])
def download_data():
    return send_file("data/titanic_train.csv", as_attachment=True)

@app.route('/pairplot', methods=['GET'])
def get_pairplot():
    data = pd.read_csv ("data/titanic_train.csv")
    sns_plot =  sns.pairplot(data[["Survived", "Fare", "Pclass"]], hue="Survived")
    sns_plot.savefig("static/tmp/pairplot.png")
    return render_index (image="pairplot.png")

@app.route('/fair_vs_pclass', methods=['GET'])
def fair_vs_pclass():
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    data = pd.read_csv ("data/titanic_train.csv")
    filtered_data = data.query('Fare < 200')
    sns.boxplot(x='Pclass', y='Fare', data=filtered_data, ax=ax)
    plt.savefig('static/tmp/fair_vs_pclass.png')

    return render_index ("fair_vs_pclass.png")


@app.route('/pclass_vs_sex', methods=['GET'])
def pclass_vs_sex():
    import matplotlib.pyplot as plt
    data = pd.read_csv ("data/titanic_train.csv")
    result = {}
    for (cl, sex), sub_df in data.groupby(['Pclass', 'Sex']):
        result[f"{cl} {sex}"] = sub_df['Age'].mean()

    plt.bar (result.keys(), result.values())
    plt.savefig('static/tmp/pclass_vs_sex.png')
    return render_index ("pclass_vs_sex.png")

# use prints average age -> return average age
def get_response (text):
    if text.lower () == "average age":
        data = pd.read_csv("data/titanic_train.csv")
        return data["Age"].mean ()

    return text

@app.route('/{}'.format(TOKEN), methods=['POST'])
def respond():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    chat_id = update.message.chat.id
    msg_id = update.message.message_id
    text = update.message.text.encode('utf-8').decode()
    response = get_response(text)
    bot.sendMessage(chat_id=chat_id, text=response, reply_to_message_id=msg_id)
    return 'ok'


@app.route('/setwebhook', methods=['GET', 'POST'])
def set_webhook():
    # we use the bot object to link the bot to our app which live
    # in the link provided by URL
    s = bot.setWebhook('{URL}{HOOK}'.format(URL=URL, HOOK=TOKEN))
    # something to let us know things work
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"

if __name__ == '__main__':
    # port -> http port 80 / https port 443
    app.run(host="localhost", port=8888)
    # print (get_response("average age"))