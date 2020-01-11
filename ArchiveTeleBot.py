import telebot
import time
import requests
import os
from archivenow import archivenow
from bs4 import BeautifulSoup

bot = telebot.TeleBot("TOKEN", threaded=False)

@bot.message_handler(
    regexp="(?:(?:https?|ftp|file):\/\/|www\.|ftp\.)(?:\([-A-Z0-9+&@#\/%=~_|$?!:,.]*\)|[-A-Z0-9+&@#\/%=~_|$?!:,.])*(?:\([-A-Z0-9+&@#\/%=~_|$?!:,.]*\)|[A-Z0-9+&@#\/%=~_|$])")
def echo_all(message):

    if 'weibo.com' in message.text or 'weibo.cn' in message.text:
        try:
            bot.reply_to(message, "archive doesn't support weibo")
        except Exception as e:
            bot.reply_to(message, 'oooops, please send the url again.')
    else:
        if message.text.startswith('https://mp.weixin.qq.com/') and '__biz=' in message.text:
            url = '&'.join(message.text.split('&', 5)[:5])
        else:
            url = message.text

        try:
            reply_ia = archivenow.push(url, 'ia')[0]
            bot.reply_to(message, reply_ia)
        except Exception as e:
            bot.reply_to(message, 'oooops, please send the url again.')

        html = requests.get(url)
        soup = BeautifulSoup(html.text, "html.parser")
        if message.text.startswith('https://mp.weixin.qq.com/s'):
            Title = soup.h2.text.strip()
            Title = Title.replace(',',' ')
            Title = Title.replace(' ','_')
        else:
            Title = soup.title.text.strip()
            Title = Title.replace('\n','')
            Title = Title.replace(',',' ')
            Title = Title.replace(' ','_')

        cmd = 'monolith ' + url + ' -o /srv/web/mono/' + Title + '.html'
        print(cmd)
        os.system(cmd)
        reply_url = 'http://206.189.252.32:8083/'  + Title + '.html'
        bot.reply_to(message, reply_url)
        with open('archive.csv', 'a') as f1:
            print(reply_ia)
            f1.write(time.ctime() + ',' + message.text + ',' + reply_ia + ',')
            f1.write(Title)
            f1.write('\n')

while True:
    try:
        bot.polling(none_stop=True, timeout=123)
    except Exception as e:
        logger = telebot.logger
        logger.error(e)
        time.sleep(15)
