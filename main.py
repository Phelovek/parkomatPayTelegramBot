import asyncio
import re

from PIL import Image
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ParseMode, ContentType, ContentTypes
from aiogram.utils import executor
from pyzbar.pyzbar import decode

from conf import *
from keyboard import *


class Choises(StatesGroup):
    kod = State()
    nomer = State()
    foto = State()


@dp.message_handler(commands=['start'])
async def start(message):
    await bot.send_sticker(message.chat.id,
                           'CAACAgIAAxkBAAEDtB9h5g4uoZuncEGXMVP4YgrdCXfuugACIAADwZxgDGWWbaHi0krRIwQ')
    await message.reply(
        "👋 Ласкаво просимо,<b> {0.first_name}!</b>\n\n  ✅ Я -<b> {1.first_name}</b>\n\n\nОберіть,будь ласка, "
        "something   \n👇  Натисніть кнопку  👇".format(
            message.from_user, await bot.get_me()),
        reply_markup=await keyboard_start(), reply=False, parse_mode=ParseMode.HTML)


@dp.message_handler(commands=['pay'])
async def pay(message: types.Message):
    await bot.send_message(message.chat.id,
                           "Ця картка не працює з реальними операціями."
                           " Тестова картка вводіть при оплаті: `4242 4242 4242 4242`"
                           "\n\nТестовий платіж:", parse_mode=ParseMode.HTML)
    # reply_markup=await keyboard_pay()
    await bot.send_invoice(message.chat.id, title='Оплата за паркування',
                           description='Оплати, только сегодня и только сейчас!',
                           provider_token=PAYMENTS_PROVIDER_TOKEN,
                           currency='uah',
                           prices=prices,
                           payload='Сплата за паркування'
                           )


@dp.callback_query_handler(lambda callback_query: True)
async def callback_handler(callback_query: types.CallbackQuery):
    if callback_query.data == 'nomer':
        await callback_query.message.answer('👇Надішліть в чат👇 номер автомобіля')
        await bot.answer_callback_query(callback_query.id)
        await Choises.nomer.set()

    if callback_query.data == 'kod':
        await callback_query.message.answer('👇Надішліть в чат👇 номер штрих коду паркувального талону')
        await bot.answer_callback_query(callback_query.id)
        await Choises.kod.set()

    if callback_query.data == 'foto':
        await bot.answer_callback_query(callback_query.id, '👇Надішліть в чат👇 фото талону', show_alert=True)
        await Choises.foto.set()


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='відміна', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    # logging.info('Cancelling state %r', current_state)
    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    await bot.send_sticker(message.chat.id,
                           'CAACAgIAAxkBAAEDtBlh5eZJ4xhbHs_q2kGgiWsQ7Xhg5AACKQADwZxgDPBLqR6_2N98IwQ',
                           reply_markup=types.ReplyKeyboardRemove()
                           )
    await message.reply('Відмінено', reply_markup=await keyboard_start())


@dp.message_handler(state=Choises.nomer)
async def nomer(message: types.Message, state: FSMContext):
    try:
        nomer_avto = message.text

        if re.match(r'[А-Яа-я]{2}[0-9]{4}[А-Яа-я]{2}', nomer_avto):
            await message.reply(
                f'<b>Номер автомобіля:</b>\n {message.text}\n\n<b>Сплатити</b> за паркування тисніть <b>/pay</b>',
                parse_mode=ParseMode.HTML)
            print(nomer_avto)
            await state.finish()
        else:
            await message.reply(
                f'Перевірте правильність вводу',
                parse_mode=ParseMode.HTML)
    except Exception as ex:
        print(ex)
        await state.finish()


@dp.message_handler(state=Choises.kod)
async def kod(message: types.Message, state: FSMContext):
    try:
        kod = message.text
        await message.reply(f'<b>Номер талона:</b>\n {message.text}\n<b>Сплатити</b> за паркування тисніть <b>/pay</b>',
                            parse_mode=ParseMode.HTML)

        print(kod)
        await state.finish()
    except Exception as ex:
        print(ex)
        await state.finish()


prices = [
    types.LabeledPrice(label='Оплата за паркування', amount=10000),  # в копейках

]


@dp.message_handler(commands=['terms'])
async def cmd_terms(message: types.Message):
    await bot.send_message(message.chat.id,
                           'Дякуємо за користування ботом.  Гарного дня')


@dp.pre_checkout_query_handler(lambda query: True)
async def checkout(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True,
                                        error_message="Инопланетяне пытались украсть CVV вашей карты, но мы успешно защитили ваши учетные данные, попробуйте оплатить еще раз через минуту, нам нужен небольшой отдых.")


@dp.message_handler(content_types=ContentTypes.SUCCESSFUL_PAYMENT)
async def got_payment(message: types.Message):
    await bot.send_message(message.chat.id,
                           'Урааа! Дякуємо! Ваш платіж на `{} {}`'
                           ' успішно здійснений! На все добре. Гарного вам настрою'.format(
                               message.successful_payment.total_amount / 100, message.successful_payment.currency),
                           parse_mode='Markdown')


@dp.message_handler(content_types=['text'])
async def msg(message):
    await message.reply('<b>Оберіть, будь ласка, спосіб надання інформації</b>',
                        reply_markup=await keyboard_start(), reply=False,
                        parse_mode=ParseMode.HTML)


@dp.message_handler(content_types=[types.ContentType.ANIMATION])
async def animation_handle(message: types.Message):
    await message.reply_animation(message.animation.file_id, reply_markup=await keyboard_start())


def BarcodeReader(image_path):
    # read the image in numpy array using cv2
    # img = cv2.imread(image_path)
    img = Image.open(image_path)
    # Decode the barcode image
    detectedBarcodes = decode(img)

    # If not detected then print the message
    if not detectedBarcodes:
        print("Barcode Not Detected or your barcode is blank/corrupted!")

    else:

        #  detect barcodes in image
        for barcode in detectedBarcodes:

            # Locate the barcode position in image
            # (x, y, w, h) = barcode.rect

            # Put the rectangle in image using
            # cv2 to heighlight the barcode
            # cv2.rectangle(img, (x - 10, y - 10),
            #               (x + w + 10, y + h + 10),
            #               (255, 0, 0), 2)

            if barcode.data != "":
                # Print the barcode data
                print(barcode.type)
                return barcode.data


@dp.message_handler(state=Choises.foto, content_types=ContentType.ANY)
async def foto(message: types.Message, state: FSMContext):
    try:
        foto_info = await bot.get_file(message.photo[len(message.photo) - 1].file_id)
        print(foto_info)
        downloaded_file = await bot.download_file(foto_info.file_path)
        print(message.photo[len(message.photo) - 1].as_json())
        src = foto_info.file_path
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file.getvalue())

        # stroka = img_reader(src)
        stroka = BarcodeReader(src)

        if stroka:
            bc = str(stroka).split("'")[1]
        else:
            bc = str(stroka)

        if stroka is None:
            await message.reply(
                '<b>Вибачте,</b> але <b>штрих код</b> не дуже чітко видно.',
                reply=False, parse_mode=ParseMode.HTML)
        else:
            await message.reply(
                'Номер талона: ' + bc + '\nЯкщо номер вірний, то ви можете сплатити за паркування натиснувши <b>/pay</b>',
                reply=False, parse_mode=ParseMode.HTML)

        await state.finish()
    except Exception as ex:
        print(ex)
        await state.finish()


if __name__ == '__main__':
    while True:
        try:
            executor.start_polling(dp, skip_updates=True)
        except Exception as ex:
            asyncio.sleep(2)
            print(ex)
