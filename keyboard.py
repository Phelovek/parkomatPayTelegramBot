from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

button_nomer = InlineKeyboardButton(text="Ввести номер авто", callback_data='nomer')
button_kod = InlineKeyboardButton(text="Ввести штрих код", callback_data='kod')
button_foto = InlineKeyboardButton(text="Отправить фото талона", callback_data='foto')

markup_pay = InlineKeyboardButton(text="Сплатити",
                                  url='https://www.liqpay.ua/api/3/checkout?data=eyJ2ZXJzaW9uIjozLCJhY3Rp'
                                      'b24iOiJwYXkiLCJhbW91bnQiOiIxMDAiLCJjdXJyZW5jeSI6IlVBSCIsImRlc2NyaX'
                                      'B0aW9uIjoi0JzRltC5INGC0L7QstCw0YAiLCJwdWJsaWNfa2V5Ijoic2FuZGJveF9'
                                      'pOTg5MTEzMDg2NjEiLCJsYW5ndWFnZSI6InJ1In0=&signature=tGMo7am8pOW4'
                                      'ApdnaULkoqLmHts=')


async def keyboard_start():
    keybord_start = InlineKeyboardMarkup(row_width=1)
    keybord_start.add(button_nomer, button_kod, button_foto)
    return keybord_start


async def keyboard_pay():
    keybord_pay = InlineKeyboardMarkup(row_width=1)
    keybord_pay.add(button_nomer, button_kod, button_foto)
    return keyboard_pay
