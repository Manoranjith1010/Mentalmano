from flask import Flask, render_template, request, session, flash, send_file, jsonify

import mysql.connector
from chatterbot import ChatBot
from requests import get
from bs4 import BeautifulSoup

app = Flask(__name__)
app.config['SECRET_KEY'] = 'aaa'

english_bot = ChatBot('Bot',
                      storage_adapter='chatterbot.storage.SQLStorageAdapter',
                      logic_adapters=[
                          {
                              'import_path': 'chatterbot.logic.BestMatch'
                          },

                      ])


@app.route('/')
def home():
    import datetime
    date = datetime.datetime.now().strftime('%Y-%m-%d')
    conn = mysql.connector.connect(user='root', password='', host='localhost', database='3herbalchatmondb')
    cursor = conn.cursor()
    cursor.execute("SELECT * from reporttb where date='" + date + "' and Status='0' ")
    data = cursor.fetchall()
    for x1 in data:
        id = x1[0]
        UserName = x1[1]
        PlantName = x1[2]
        info = x1[4]

        conn = mysql.connector.connect(user='root', password='', host='localhost', database='3herbalchatmondb')
        cursor = conn.cursor()
        cursor.execute("SELECT * from regtb where username='" + UserName + "'")
        data = cursor.fetchone()
        if data:
            msg = "PlantName :" + PlantName + "\n" + "Info :" + info
            sendmail(data[3], msg)

        conn = mysql.connector.connect(user='root', password='', host='localhost', database='3herbalchatmondb')
        cursor = conn.cursor()
        cursor.execute(
            "update  reporttb set Status='1'  where id='" + str(id) + "'")
        conn.commit()
        conn.close()

    return render_template('index.html')

@app.route('/NewUser')
def NewUser():
    return render_template('NewUser.html')


@app.route('/Chat')
def Chat():
    return render_template('Chat.html')


@app.route("/ask", methods=['GET', 'POST'])
def ask():
    message = str(request.form['messageText'])

    print('User' + message)
    bot_response = english_bot.get_response(message)

    print(bot_response)

    print(bot_response.confidence)

    while True:

        if bot_response.confidence > 0.5:

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


@app.route('/UserLogin')
def UserLogin():
    return render_template('UserLogin.html')


@app.route('/Monitor')
def Monitor():
    uname = session['uname']
    conn = mysql.connector.connect(user='root', password='', host='localhost', database='3herbalchatmondb')
    cur = conn.cursor()
    cur.execute("SELECT * FROM reporttb where UserName='" + uname + "'  ")
    data = cur.fetchall()
    return render_template('Monitor.html', data=data)


@app.route("/newuser", methods=['GET', 'POST'])
def newuser():
    if request.method == 'POST':
        name = request.form['name']
        mobile = request.form['mobile']
        email = request.form['email']
        address = request.form['address']
        uname = request.form['uname']
        password = request.form['password']

        conn = mysql.connector.connect(user='root', password='', host='localhost', database='3herbalchatmondb')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO regtb VALUES ('','" + name + "','" + mobile + "','" + email + "','" + address + "','" + uname + "','" + password + "')")
        conn.commit()
        conn.close()
        flash('User Register successfully')
    return render_template('UserLogin.html')


@app.route("/ulogin", methods=['GET', 'POST'])
def ulogin():
    if request.method == 'POST':
        username = request.form['uname']
        password = request.form['password']
        session['uname'] = request.form['uname']

        conn = mysql.connector.connect(user='root', password='', host='localhost', database='3herbalchatmondb')
        cursor = conn.cursor()
        cursor.execute("SELECT * from regtb where username='" + username + "' and Password='" + password + "'")
        data = cursor.fetchone()
        if data is None:

            flash('Username or Password is wrong')
            return render_template('UserLogin.html')
        else:

            session['mob'] = data[2]

            conn = mysql.connector.connect(user='root', password='', host='localhost', database='3herbalchatmondb')
            cur = conn.cursor()
            cur.execute("SELECT * FROM regtb where username='" + username + "' and Password='" + password + "'")
            data = cur.fetchall()
            flash("Login successfully")
            return render_template('UserHome.html', data=data)


@app.route("/UserHome")
def UserHome():
    uname = session['uname']
    conn = mysql.connector.connect(user='root', password='', host='localhost', database='3herbalchatmondb')
    cur = conn.cursor()
    cur.execute("SELECT * FROM regtb where UserName='" + uname + "'  ")
    data = cur.fetchall()
    return render_template('UserHome.html', data=data)


@app.route("/Predict")
def Predict():
    return render_template('Predict.html')


@app.route("/pred", methods=['GET', 'POST'])
def pred():
    if request.method == 'POST':
        import os
        file = request.files['file']
        file.save('static/Out/Test.jpg')

        import warnings
        warnings.filterwarnings('ignore')

        import tensorflow as tf
        model = tf.keras.models.load_model('model.h5')

        import numpy as np
        from keras.preprocessing import image

        base_dir = 'Data/'
        catgo = os.listdir(base_dir)

        test_image = image.load_img('static/Out/Test.jpg', target_size=(200, 200))

        org = 'static/Out/Test.jpg'

        test_image = np.expand_dims(test_image, axis=0)
        result = model.predict(test_image)
        ind = np.argmax(result)

        print(catgo[ind])

        out = ''
        pre = ''
        predicted_class = catgo[ind]

        out = predicted_class

        if (predicted_class == "Alpinia Galanga (Rasna)"):
            out = predicted_class

            pre = 'Treating rheumatism and inflammatory disorders,Treating coughs and colds,Treating fever, ' \
                  'muscle spasms, intestinal gas, and swelling,Killing bacteria,Stimulating the digestive power and ' \
                  'appetite,Acting as a purgative,Relaxing smooth muscles,Loosening constricted tissues,Lowering pain, ' \
                  'soreness, and inflammation in muscles,Removing toxins from the body '

        elif (predicted_class == "Amaranthus Viridis (Arive-Dantu)"):
            out = predicted_class
            pre = 'Medicinal herb in traditional Ayurvedic medicine as antipyretic agents, also for the treatment of ' \
                  'inflammation, ulcer, diabetic, asthma and hyperlipidemia. '


        elif (predicted_class == "Artocarpus Heterophyllus (Jackfruit)"):
            out = predicted_class
            pre = 'Anticarcinogenic, antimicrobial, antifungal, anti-inflammatory, wound healing, and hypoglycemic ' \
                  'effects. '

        elif (predicted_class == "Azadirachta Indica (Neem)"):
            out = predicted_class
            pre = 'neem leaves are used to treat dental and gastrointestinal disorders, malaria fevers, ' \
                  'skin diseases, and as insects repellent, while the Balinese used neem leaves as a diuretic and for ' \
                  'diabetes, headache, heartburn, and stimulating the appetite. '
        elif (predicted_class == "Basella Alba (Basale)"):
            out = predicted_class
            pre = 'improve testosterone levels in males, thus boosting libido. Decoction of the leaves is recommended ' \
                  'as a safe laxative in pregnant women and children. Externally, the mucilaginous leaf is crushed and ' \
                  'applied in urticaria, burns and scalds. '

        elif (predicted_class == "Brassica Juncea (Indian Mustard)"):
            out = predicted_class
            pre = 'extracted from the seeds of brown Indian mustard plant (Brassica juncea), is commonly used for ' \
                  'cooking purposes and is rich in the content of special sulfur compounds called glucosinolates which ' \
                  'has been reported to exhibit medicinal properties '

        elif (predicted_class == "Carissa Carandas (Karanda)"):
            out = predicted_class
            pre = 'Medicine, Ayurvedic, to treat acidity, indigestion, fresh and infected wounds, skin diseases, urinary disorders and diabetic ulcer, as well as biliousness, stomach pain, constipation, anemia, skin conditions, anorexia and insanity.'

        elif (predicted_class == "Citrus Limon (Lemon)"):
            out = predicted_class
            pre = 'Weight loss and reduce your risk of heart disease, anemia, kidney stones, digestive issues, and cancer'

        elif (predicted_class == "Ficus Auriculata (Roxburgh fig)"):
            out = predicted_class
            pre = 'Stem bark juice is effective for diarrhea, cuts and wounds. Fruits are edible and can be made into jams and curries. Roasted figs are taken for diarrhea and dysentery. Root latex is used in mumps, cholera, diarrhea and vomiting.'


        elif (predicted_class == "Ficus Religiosa (Peepal Tree)"):
            out = predicted_class
            pre = 'Antiulcer, antibacterial, antidiabetic, in the treatment of gonorrhea and skin diseases.'

        elif (predicted_class == "Hibiscus Rosa-sinensis"):
            out = predicted_class
            pre = 'Consumed in teas made from its flowers, leaves, and roots. In addition to casual consumption, Hibiscus is also used as an herbal medicine to treat hypertension, cholesterol production, and cancer progression.'

        elif (predicted_class == "Jasminum (Jasmine)"):

            pre = 'Jasmine is used to flavor beverages, frozen dairy desserts, candy, baked goods, gelatins, and puddings.'

        elif (predicted_class == "Mangifera Indica (Mango)"):

            pre = 'Invigorating and freshening. The juice is restorative tonic and used in heat stroke. The seeds are used in asthma and as an astringent. Fumes from the burning leaves are inhaled for relief from hiccups and affections of the throat.'

        elif (predicted_class == "Mentha (Mint)"):
            pre = 'antimicrobial, carminative, stimulant, antispasmodic and for the treatment of various diseases such as headaches and digestive disorders '

        elif (predicted_class == "Moringa Oleifera (Drumstick)"):
            pre = 'Treating edema,Protecting the liver,Preventing and treating cancer,Treating stomach upset,Fighting foodborne bacterial,infections,Preventing rheumatoid arthritis,Treating digestive problems,Controlling diabetes and high blood pressure,Fortifying bones,Improving skin health,Treating erectile dysfunction,Enhancing libido'

        elif (predicted_class == "Muntingia Calabura (Jamaica Cherry-Gasagase)"):
            pre = 'Anti-inflammatory activity,Antipyretic activity,Antiulcer activity,Anti-diabetic activity,Anti-hypertensive activity,Cardioprotective activity,Anti-bacterial activity,Insecticidal activity'

        elif (predicted_class == "Murraya Koenigii (Curry)"):
            pre = 'Treating piles, inflammation, itching, fresh cuts, bruises, and edema,Treating common body aches,Treating stomachaches,Acting as a carminative and analgesic '

        elif (predicted_class == "Nerium Oleander (Oleander)"):
            pre = 'Treatment of diverse ailments such as heart failure, asthma, corns, cancer, diabetes, and epilepsy. Less well appreciated are the skin care benefits of extracts of N. oleander that include antibacterial, antiviral, immune, and even antitumor properties associated with topical use.'

        elif (predicted_class == "Nyctanthes Arbor-tristis (Parijata)"):
            pre = 'Treat a different kind of fevers, cough, arthritis, worm infestation, etc. The leaves juice is bitter and works as a tonic. The kadha or decoction is excellent for arthritis, constipation, worm infestation.'

        elif (predicted_class == "Ocimum Tenuiflorum (Tulsi)"):
            pre = 'Hand sanitizer, mouthwash and water purifier as well as in animal rearing, wound healing, the preservation of food stuffs and herbal raw materials and travelers health.'

        elif (predicted_class == "Piper Betle (Betel)"):
            pre = 'Prevents halitosis, improves vocalization, and strengthens gum, treat indigestion, constipation, congestion, coughs and asthma.'

        elif (predicted_class == "Plectranthus Amboinicus (Mexican Mint)"):
            pre = 'Treatment in folkloric medicines (syrup). It can also be used in other diseases such as flu, bronchitis, and epilepsy.'

        elif (predicted_class == "Pongamia Pinnata (Indian Beech)"):
            pre = 'Treatment of tumors, piles, skin diseases, and ulcers,The root is effective for treating gonorrhea, cleaning gums, teeth, and ulcers, and is used in vaginal and skin diseases '

        elif (predicted_class == "Psidium Guajava (Guava)"):
            pre = 'Gastrointestinal infections such as diarrhea, dysentery, stomach aches, and indigestion[4] and it is used across the world for these ailments.'

        elif (predicted_class == "Punica Granatum (Pomegranate)"):
            pre = 'Preventing and treating cancer,Cardiovascular disease,Osteoarthritis and rheumatoid arthritis,Wound healing,The reproductive system,Dysentery, diarrhea, and intestinal parasites,Throat infections,Nose bleeds,Bronchitis,Sore throats, coughs, urinary infections, digestive disorders, and arthritis'

        elif (predicted_class == "Santalum Album (Sandalwood)"):
            pre = 'Antipyretic, antiseptic, antiscabetic, and diuretic properties.It is also effective in treatment of bronchitis, cystitis, dysuria, and diseases of the urinary tract [17]. The main ingredient of sandalwood oil is α-santalol that has many therapeutic properties.'

        elif (predicted_class == "Syzygium Cumini (Jamun)"):
            pre = 'It has astringent, carminative, stomachic, diuretic, antidiabetic, anti-diarrheal, anti-inflammatory, radioprotective, gastroprotective, antioxidant, anti-allergic, anticancer, antibacterial, and cardioprotective effects, among other things.'

        elif (predicted_class == "Syzygium Jambos (Rose Apple)"):
            pre = 'Rich in vitamin C, the fruit can be eaten raw or cooked in various regional recipes. In South-East Asian countries, rose apple fruit is frequently served with spiced sugar.'

        elif (predicted_class == "Tabernaemontana Divaricata (Crape Jasmine)"):
            pre = 'The roots, leaves, and flowers are all used to treat snake and scorpion poisoning. Non-medical uses include using the wood as incense and perfume or using the pulp around the seed to make red dyes.'

        elif (predicted_class == "Tabernaemontana Divaricata (Crape Jasmine)"):
            pre = 'The roots, leaves, and flowers are all used to treat snake and scorpion poisoning. Non-medical uses include using the wood as incense and perfume or using the pulp around the seed to make red dyes.'

        elif (predicted_class == "Butterfly Pea"):
            pre = 'It is rich in antioxidants and may be linked to several health benefits, including increased weight ' \
                  'loss, better blood sugar control, and improvements in hair and skin health. It also versatile and ' \
                  'associated with very few side effects, so it a great potential addition to your diet. '

    return render_template('Result.html', org=org, out=out, pre=pre)


@app.route("/pred1", methods=['GET', 'POST'])
def pred1():
    if request.method == 'POST':
        return render_template('Predict.html')


@app.route("/newinfo", methods=['GET', 'POST'])
def newinfo():
    if request.method == 'POST':
        uname = session['uname']
        name = request.form['name']
        Date = request.form['Date']
        info = request.form['info']

        conn = mysql.connector.connect(user='root', password='', host='localhost', database='3herbalchatmondb')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO reporttb VALUES ('','" + uname + "','" + name + "','" + Date + "','" + info + "','0')")
        conn.commit()
        conn.close()
        flash('Record save successfully')

        conn = mysql.connector.connect(user='root', password='', host='localhost', database='3herbalchatmondb')
        cur = conn.cursor()
        cur.execute("SELECT * FROM reporttb where UserName='" + uname + "'  ")
        data = cur.fetchall()
        return render_template('Monitor.html', data=data)


@app.route("/APRemove")
def APRemove():
    id = request.args.get('id')
    conn = mysql.connector.connect(user='root', password='', host='localhost', database='3herbalchatmondb')
    cursor = conn.cursor()
    cursor.execute(
        "delete from reporttb where id='" + id + "'")
    conn.commit()
    conn.close()
    flash('Remove Successfully!')
    return Monitor()


def sendmsg(targetno, message):
    import requests
    requests.post(
        "http://sms.creativepoint.in/api/push.json?apikey=6555c521622c1&route=transsms&sender=FSSMSS&mobileno=" + targetno + "&text=Dear customer your msg is " + message + "  Sent By FSMSG FSSMSS")


def sendmail(Mailid, message):
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.base import MIMEBase
    from email import encoders

    fromaddr = "projectmailm@gmail.com"
    toaddr = Mailid

    # instance of MIMEMultipart
    msg = MIMEMultipart()

    # storing the senders email address
    msg['From'] = fromaddr

    # storing the receivers email address
    msg['To'] = toaddr

    # storing the subject
    msg['Subject'] = "Alert"

    # string to store the body of the mail
    body = message

    # attach the body with the msg instance
    msg.attach(MIMEText(body, 'plain'))

    # creates SMTP session
    s = smtplib.SMTP('smtp.gmail.com', 587)

    # start TLS for security
    s.starttls()

    # Authentication
    s.login(fromaddr, "qmgn xecl bkqv musr")

    # Converts the Multipart msg into a string
    text = msg.as_string()

    # sending the mail
    s.sendmail(fromaddr, toaddr, text)

    # terminating the session
    s.quit()


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
