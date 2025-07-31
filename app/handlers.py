import os
from aiogram import Router, F, Bot
from aiogram.types import Message, InputMediaPhoto
from aiogram.enums import ChatAction
from time import sleep
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from dotenv import load_dotenv
from random import randint

from app.db import requests as rq
from app import keyboards as kb
from app.call_handlers import Register
from app.call_handlers import ALL

router = Router()

load_dotenv()
bot = Bot(token=os.getenv("TOKEN"))


@router.message(CommandStart())
async def cmd(message: Message, state: FSMContext):
    await bot.send_chat_action(message.from_user.id, action=ChatAction.TYPING)
    sleep(0.8)
    file = 'https://56cbf095-b352-4813-87c5-21e64c2cd347.selstorage.ru/start/photo_2024-05-13_21-59-50.jpg'
    await message.answer_photo(photo=file, caption='Здравствуйте, дорогие любители тортов, десертов и выпечки!'
                                                   f' Меня зовут Елена, и я кондитер 👩🏼‍🍳. Я создаю для вас самые '
                                                   f'вкусные и красивые торты 🍰, пирожные 🥮, капкейки 🥧 и другие'
                                                   f' сладости.\n'
                                                   f'Теперь вы можете заказать мои десерты прямо здесь,'
                                                   f' в этом боте!'
                                                   f'Выбирайте любимые вкусы, а я позабочусь о том,'
                                                   f' чтобы ваш праздник стал незабываемым.\n'
                                                   f'С наилучшими пожеланиями, Елена.')
    await bot.send_chat_action(message.from_user.id, action=ChatAction.TYPING)
    sleep(0.8)
    await message.answer(text='Подтвердите начало регистрации', reply_markup=kb.reg)


@router.message(Command('finish_admin'))
async def finish_admin(message: Message, state: FSMContext):
    await message.answer(text='Вы вышли из Админ-режима', reply_markup=kb.main_menu)
    await state.update_data(mode='public')


@router.message(Register.name)
async def reg_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Register.phone)
    await bot.send_chat_action(message.from_user.id, action=ChatAction.TYPING)
    sleep(0.8)
    await message.answer(text='Отправьте свой телефон 📲\nЧерез кнопку над клавиатурой ️❗❗️',
                         reply_markup=kb.register_number_button)


@router.message(Register.phone)
async def reg_phone(message: Message, state: FSMContext):
    if not message.text:
        await state.update_data(phone=message.contact.phone_number)
        data = await state.get_data()
        await rq.register_user(message.from_user.id, data['name'], data['phone'],
                               message.from_user.username)
        await state.clear()
        await bot.send_chat_action(message.from_user.id, action=ChatAction.TYPING)
        sleep(0.8)
        await message.answer(text=f'🎉 Регистрация успешно пройдена 🎉\n\n'
                                  f'Теперь вам доступен 🍰 Каталог', reply_markup=kb.main_menu)
    else:
        await bot.send_chat_action(message.from_user.id, action=ChatAction.TYPING)
        sleep(0.8)
        await message.answer(text='Ошибка 🔄', reply_markup=kb.register_number_button)


@router.message(F.text == '🍰 Каталог')
async def catalog(message: Message, state: FSMContext):
    catalog_photo = set()
    all_images = await rq.get_catalog_image()
    photo = []
    for image in all_images:
        photo.append(f'{image.url}')
    while len(catalog_photo) < 4:
        file = photo[randint(0, len(photo) - 1)]
        catalog_photo.add(InputMediaPhoto(type='photo', media=str(file)))
    await bot.send_chat_action(message.from_user.id, action=ChatAction.UPLOAD_PHOTO)
    sleep(0.7)
    await message.answer_media_group(media=catalog_photo)
    await bot.send_chat_action(message.from_user.id, action=ChatAction.TYPING)
    sleep(0.7)
    await message.answer(text=f'Торты, десерты и рулеты от кондитера Елены: искусство вкуса в каждом кусочке.',
                         reply_markup=await kb.set_category())
    await state.update_data(name_call='choose_category')


async def complete_my_bin(message: Message):
    my_items = await rq.get_my_bin(message.from_user.id)
    items_data = {}
    for myitem in my_items:
        item = await rq.get_item(myitem.item)
        if len(item.price.split()) == 6:
            if item.name in items_data:
                items_data[item.name] += int(item.price.split()[4])
            else:
                items_data[item.name] = int(item.price.split()[4])
        else:
            if item.name in items_data:
                items_data[item.name] += int(item.price)
            else:
                items_data[item.name] = int(item.price)
    itemss = []
    for name, price in items_data.items():
        itemss.append(f"{name}: {f'{price} рублей'}")

    itemss.append(f"\nОбщая сумма: {sum(items_data.values())} рублей")
    return itemss


@router.message(F.text == '🗑 Корзина')
async def my_bin_(message: Message):
    itemss = await complete_my_bin(message)
    if int(itemss[-1].split()[2]) > 0:
        await bot.send_chat_action(message.from_user.id, action=ChatAction.TYPING)
        sleep(0.9)
        await message.answer(text='🗑 Твоя корзина содержит')
        await message.answer('\n'.join(itemss),
                             reply_markup=kb.delete_bin)
    else:
        await message.answer(text='🗑 Твоя корзина пуста')


class SOS(StatesGroup):
    text_msg = State()


@router.message(F.text == '🆘 Помощь')
async def my_bin_(message: Message, state: FSMContext):
    await message.answer(text='Введите ваш запрос')
    await state.set_state(SOS.text_msg)


@router.message(SOS.text_msg)
async def my_bin_(message: Message, state: FSMContext):
    await state.update_data(text_msg=message.text)
    await message.answer(text='Ожидайте ⏳ Ваш запрос отправлен.')
    data = await state.get_data()
    await bot.send_message('1474718642', text=f'Запрос от пользователя @{message.from_user.username}\n\n'
                                              f'{data["text_msg"]}')  # '5380691019'
    await state.clear()


# Начало Админ части
@router.message(Command('admin_panel'))
async def cmd(message: Message, state: FSMContext):
    if message.from_user.id == int(os.getenv('ADMIN_ID')) or message.from_user.id == int(os.getenv('ADMIN_ID2')):
        await state.update_data(mode='admin')
        await message.answer(text='Вы вошли в админ панель', reply_markup=kb.admin_panel)
    else:
        await message.answer(text='Извините, вы не админ')


@router.message(F.text == 'Добавить')
async def add_cmd(message: Message):
    await message.answer(text='Панель добавления', reply_markup=kb.add_panel)


@router.message(F.text == 'Удалить')
async def add_cmd(message: Message):
    await message.answer(text='Панель удаления', reply_markup=kb.delete_panel)


@router.message(F.text == 'Редактировать')
async def add_cmd(message: Message):
    await message.answer(text='Панель редактирования', reply_markup=kb.edit_panel)


@router.message(ALL.category_name)
async def add_categ(message: Message, state: FSMContext):
    data = await state.get_data()
    if data['name_call'] == 'add_category':
        await state.update_data(category_name=message.text)
        data = await state.get_data()
        category_name = data['category_name']
        await rq.add_category(category_name)
        await message.answer(text='Категория успешно добавлена')
    elif data['name_call'] == 'edit_category':
        await state.update_data(category_name=message.text)
        data = await state.get_data()
        category_name = data['category_name']
        await rq.edit_category(category_name, data['category_id'])
        await message.answer(text='Категория успешно изменена')


@router.message(ALL.name_item)
async def add_item_description(message: Message, state: FSMContext):
    data = await state.get_data()
    if data['name_call'] == 'add_item':
        await state.update_data(name_item=message.text)
        await message.answer(text='Введите описание товара')
        await state.set_state(ALL.description_item)
    if data['name_call'] == 'edit_item_name':
        await state.update_data(name_item=message.text)
        data = await state.get_data()
        await rq.edit_item_name(data['name_item'], data['item_id'])
        await message.answer(text='Название успешно изменено',
                             reply_markup=kb.edit_item_panel)


@router.message(ALL.description_item)
async def add_item_price(message: Message, state: FSMContext):
    data = await state.get_data()
    if data['name_call'] == 'add_item':
        await state.update_data(description_item=message.text)
        await message.answer(text='Введите цену товара')
        await state.set_state(ALL.price_item)
    if data['name_call'] == 'edit_item_description':
        await state.update_data(description_item=message.text)
        data = await state.get_data()
        await rq.edit_item_description(data['description_item'], data['item_id'])
        await message.answer(text='Описание успешно изменено',
                             reply_markup=kb.edit_item_panel)


@router.message(ALL.price_item)
async def add_item_complete(message: Message, state: FSMContext):
    data = await state.get_data()
    if data['name_call'] == 'add_item':
        await state.update_data(price_item=message.text)
        data = await state.get_data()
        await rq.add_item(data['name_item'], data['description_item'], data['price_item'], data['category_item'])
        await message.answer(text='Товар успешно добавлен')
    if data['name_call'] == 'edit_item_price':
        await state.update_data(price_item=message.text)
        data = await state.get_data()
        await rq.edit_item_price(data['price_item'], data['item_id'])
        await message.answer(text='Цена успешно изменена',
                             reply_markup=kb.edit_item_panel)


@router.message(ALL.url_image)
async def add_url_complete(message: Message, state: FSMContext):
    await state.update_data(url_image=message.text)
    data = await state.get_data()
    await rq.add_image(data['url_image'], data['item_id'])
    await message.answer(text='Фото добавлено', reply_markup=kb.image)
