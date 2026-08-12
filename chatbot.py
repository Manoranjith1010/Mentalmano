from chatterbot import ChatBot
from requests import get
from bs4 import BeautifulSoup
import os
from flask import Flask, render_template, request, jsonify


app = Flask(__name__)
app.config['DEBUG']
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'

english_bot = ChatBot('Bot',
                      storage_adapter='chatterbot.storage.SQLStorageAdapter',
                      logic_adapters=[
                          {
                              'import_path': 'chatterbot.logic.BestMatch'
                          },

                      ])


@app.route("/")
def hello():
    return render_template('chat.html')


@app.route("/ask", methods=['GET', 'POST'])
def ask():
    message = str(request.form['messageText'])

    print('User' + message)
    bot_response = english_bot.get_response(message)

    print(bot_response)

    print(bot_response.confidence)

    while True:

        bert = SentimentIntensityAnalyzer()

        # polarity_scores method of SentimentIntensityAnalyzer
        # object gives a sentiment dictionary.
        # which contains pos, neg, neu, and compound scores.
        sentiment_dict = bert.polarity_scores(message)

        string = str(sentiment_dict['neg'] * 100) + "% Negative"
        # negativeField.insert(10, string)

        string = str(sentiment_dict['neu'] * 100) + "% Neutral"
        # neutralField.insert(10, string)

        string = str(sentiment_dict['pos'] * 100) + "% Positive"
        # positiveField.insert(10, string)

        # decide sentiment as positive, negative and neutral
        if sentiment_dict['compound'] >= 0.05:
            string = "Positive"
            i = 0;

        elif sentiment_dict['compound'] <= - 0.05:
            string = "sad"

            i = 1;


        else:
            string = "Neutral"
            i = 0;

        print(string)

        if string == "Negative":
            mes = "Prediction Result Negative Recommend Solution <br>"
            ss1 = '<a href="https://www.youtube.com/watch?v=2RTZNLL0wss" target="_blank" >Yoga</a> <br>'

            ss2 = '<a href="https://www.youtube.com/watch?v=I5-_HnwnLTE" target="_blank">ViewSong</a> <br>'

            out = mes + ss1 + ss2

            return jsonify({'status': 'OK', 'answer': out})

        if bot_response.confidence > 0.3:

            bot_response = str(bot_response)
            print(bot_response)
            return jsonify({'status': 'OK', 'answer': bot_response})

        elif message == ("bye") or message == ("exit"):

            bot_response = 'Hope to see you soon' + '<a href="http://127.0.0.1:5000">Exit</a>'

            print(bot_response)
            return jsonify({'status': 'OK', 'answer': bot_response})

            break



        else:

            try:
                url = "https://en.wikipedia.org/wiki/" + message
                page = get(url).text
                soup = BeautifulSoup(page, "html.parser")
                p = soup.find_all("p")
                return jsonify({'status': 'OK', 'answer': p[1].text})



            except IndexError as error:

                bot_response = 'Sorry i have no idea about that.'

                print(bot_response)
                return jsonify({'status': 'OK', 'answer': bot_response})

    # return render_template("index.html")




if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)
