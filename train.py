from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
import os

MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
CHATBOT_MONGO_DB_NAME = os.getenv('CHATBOT_MONGO_DB_NAME', 'chatbotdb')

english_bot = ChatBot(
        'Bot',
        storage_adapter='chatterbot.storage.MongoDatabaseAdapter',
        database_uri=MONGO_URI,
        database=CHATBOT_MONGO_DB_NAME,
)
trainer = ListTrainer(english_bot)
for file in os.listdir('cdata'):
        print('Training using '+file)
        convData = open('cdata/' + file).readlines()
        trainer.train(convData)
        print("Training completed for "+file)
    

