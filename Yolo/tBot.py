# -*- coding: utf-8 -*-
import telebot
import subprocess
import json
import logging
import os


bot = telebot.TeleBot("5444606088:AAEMFmC2y0rInAH_zM81ArLArM0MB8Qwzeo")

sticker = 'CAACAgIAAxkBAANcYcUH_EUkEP5rpPrIeHEMkCz5aeYAAssAA1dPFQgc-0S6Y7e36CME'
sticker = 'CAACAgIAAxkBAAOHYcUMHhqUhkgGO8A-mfcnxXAim3AAAvEAA3lc4gnjMTRnFs93vyME'
vinny = 'CAACAgEAAxkBAAORYcUMnzrRjlo6URlUxmBz5ydmt60AAjMAA-9vPQdFrmIRf9MnzSME'
filename = ''
with open('labels.txt') as f:
    labels_orig = f.readlines()
with open('untitled.txt') as f:
    signs = f.readlines()

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	print(message)
	bot.reply_to(message, "Hello!")
	bot.send_message(chat_id=message.chat.id, text= '@' + message.from_user.username+', <b>Отправьте мне фотографию где есть дорожные знаки, постараюсь их распознать.</b>', parse_mode='HTML')
	bot.send_sticker(message.chat.id, sticker)

@bot.message_handler(content_types="sticker")
def send_sticker(message):
	print(message)

@bot.message_handler(commands=['weather'])
def send_weather(message):
	temp = subprocess.check_output('curl -s http://wttr.in/{London,Moscow}?format=3', shell=True)
	bot.reply_to(message, temp)
	bot.send_message(chat_id=message.chat.id, text='@' + message.from_user.username + ', <b>не пиши сюда больше!</b>',
					 parse_mode='HTML')
	bot.send_sticker(message.chat.id, vinny)
	#print(temp)

@bot.message_handler(content_types=['photo'])
def handle_docs_photo(message):
	temp = subprocess.check_output('if [ ! -d /files ]; then rm -rf files\n fi', shell=True)
	temp = subprocess.check_output('mkdir -p "files/photos"', shell=True)
	file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
	downloaded_file = bot.download_file(file_info.file_path)
	global filename
	filename = file_info.file_path.split('/')[1]
	src = 'files/' + file_info.file_path
	with open(src, 'wb') as new_file:
		new_file.write(downloaded_file)

	#bot.send_photo(message.chat.id, photo=open(src, 'rb'))


	bot.reply_to(message, "Изображение сохранено, для детекции наберите /find")

@bot.message_handler(commands=['find'])
def find(message):
    bot.reply_to(message, 'Подождите совсем немного...')
    temp = subprocess.check_output('cd yolov5/runs/detect; if [ ! -d /yolov5m6_signs_test ]; then rm -rf yolov5m6_signs_test\n fi', shell=True)
    temp = subprocess.check_output('python3 yolov5/detect.py --source files/photos --weights yolov5/project/yolov5m66/weights/best.pt --save-txt --save-conf --name "yolov5m6_signs_test" --imgsz 1280 --conf-thres 0.25', shell=True)
    file = 'yolov5/runs/detect/yolov5m6_signs_test/' + filename
    labels = 'yolov5/runs/detect/yolov5m6_signs_test/labels/' + filename.split('.')[0] + '.txt'
    bot.send_photo(message.chat.id, photo=open(file, 'rb'))
    with open(labels) as f:
        lines = f.readlines()
    text = ''
    output = ''
    
    for line in lines:
        el = int(line.split()[0])
        el = str(' ') + labels_orig[el].replace("_", '.').replace('\n', '. ')
        text += el + '\n'
        flag = 0
        end = 0
        for sign in signs:
            start = sign.find(el)
            if (start > 0):
                flag = 1
                start = int(start)
            if (flag == 1):
                output += 'Знак ' + sign[start:]
                break
    #bot.send_message(chat_id=message.chat.id, text= '@' + message.from_user.username+', Распознаны следующие знаки:\n<b>'+text+ str(start) + '</b>', parse_mode='HTML')
    
    
        
                
        
            
    bot.send_message(chat_id=message.chat.id, text= '@' + message.from_user.username+', Распознаны следующие знаки:\n<b>'+output+'</b>', parse_mode='HTML')

    


bot.polling()
