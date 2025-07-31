import os
from aiogram import F, Router, Bot
from aiogram.types import CallbackQuery, InputMediaPhoto
from aiogram.enums import ChatAction
from time import sleep
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from dotenv import load_dotenv

from app.db import requests as rq
from app import keyboards as kb

call_router = Router()
load_dotenv()
bot = Bot(token=os.getenv("TOKEN"))


class Register(StatesGroup):
    name = State()
    phone = State()


class ALL(StatesGroup):
    mode = State()

    name_call = State()

    name_item = State()
    description_item = State()
    price_item = State()
    category_item = State()

    url_image = State()
    item_id = State()

    category_id = State()
    category_name = State()


@call_router.callback_query(F.data == 'start_reg')
async def register(callback: CallbackQuery, state: FSMContext):
    if await rq.is_user(callback.from_user.id):
        await callback.answer('Регистрация')
        await bot.send_chat_action(callback.message.from_user.id, action=ChatAction.TYPING)
        sleep(0.9)
        await callback.message.answer('Введите свое имя 👤')
        await state.set_state(Register.name)
    else:
        await callback.answer()
        await callback.message.answer(text='Вы уже были зарегистрированы ранее',
                                      reply_markup=kb.main_menu)


@call_router.callback_query(F.data.startswith('first_bin_'))
async def set_items(callback: CallbackQuery):
    await rq.get_bins(callback.from_user.id, int(callback.data.split('_')[2]))
    await callback.answer('Товар добавлен в корзину', show_alert=True)
    await callback.message.edit_reply_markup(reply_markup=await kb.item_buttons_2(int(callback.data.split('_')[2])))


@call_router.callback_query(F.data.startswith('second_bin_'))
async def add_plus_item(callback: CallbackQuery):
    await callback.answer('Товар добавлен в корзину', show_alert=True)
    await rq.get_bins(callback.from_user.id, int(callback.data.split('_')[2]))


async def complete_my_bin(callback: CallbackQuery):
    my_items = await rq.get_my_bin(callback.from_user.id)
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


@call_router.callback_query(F.data == 'my_bin')
async def my_bin_call(callback: CallbackQuery):
    itemss = await complete_my_bin(callback)
    if int(itemss[-1].split()[2]) > 0:
        await callback.answer()
        await bot.send_chat_action(callback.message.from_user.id, action=ChatAction.TYPING)
        sleep(0.8)
        await callback.message.answer(text='🗑 Твоя корзина содержит')
        await callback.message.answer('\n'.join(itemss),
                                      reply_markup=kb.delete_bin)
    else:
        await callback.message.answer(text='🗑 Твоя корзина пуста')


@call_router.callback_query(F.data == 'delete_my_bin')
async def my_bin_call(callback: CallbackQuery):
    await callback.answer('Корзина очищена')
    await rq.delete_my_bin(callback.from_user.id)


@call_router.callback_query(F.data == 'complete_bin')
async def complete_of(callback: CallbackQuery, state: FSMContext):
    if await rq.is_bin(callback.from_user.id):
        await callback.answer()
        await bot.send_chat_action(callback.message.from_user.id, action=ChatAction.TYPING)
        sleep(1)
        await callback.message.answer(text=f'Отлично, пришло время оформлять заказ.\n'
                                           f'Полетели 🚀')
        await bot.send_chat_action(callback.message.from_user.id, action=ChatAction.TYPING)
        sleep(1)
        await callback.message.answer(text=f'Давай выберем способ доставки.\n❗ Его можно будет изменить\n'
                                           f'❗ Адрес самовывоза будет передан вам позже',
                                      reply_markup=kb.delivery)
    else:
        await callback.answer()
        await callback.message.answer(text='❌ Невозможно оформить заказ ❌\n🗑 Твоя корзина пуста')


async def delivery(delivery_way, callback):
    items = await complete_my_bin(callback)
    user = await rq.get_user(callback.from_user.id)
    await callback.answer()
    await callback.message.answer(text=f'Отлично заказ обработан 👍\n'
                                       f'❗️ В течении 15 минут вам напишут для уточнения деталей ❗️')
    await bot.send_message('5380691019', text=f'Пришел новый заказ от пользователя @{user.username}\n\n'
                                              f'Имя: {user.name}\n'
                                              f'Телефон: {user.phone}\nСпособ'
                                              f' доставки: {delivery_way}')
    await bot.send_message('5380691019', text='\n'.join(items))


@call_router.callback_query(F.data == 'car')
async def car_call(callback: CallbackQuery):
    await callback.answer()
    delivery_way = 'Доставка'
    if await rq.is_bin(callback.from_user.id):
        await delivery(delivery_way, callback)
    else:
        await callback.message.answer(text='❌ Невозможно оформить заказ ❌\n🗑 Твоя корзина пуста')


@call_router.callback_query(F.data == 'myself')
async def car_call(callback: CallbackQuery):
    delivery_way = 'Самовывоз'
    if await rq.is_bin(callback.from_user.id):
        await delivery(delivery_way, callback)
    else:
        await callback.message.answer(text='❌ Невозможно оформить заказ ❌\n🗑 Твоя корзина пуста')


# Начало Админ части
@call_router.callback_query(F.data == 'add_category')
async def add_cat(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer(text='Введите название категории')
    await state.set_state(ALL.category_name)
    await state.update_data(name_call='add_category')


@call_router.callback_query(F.data.startswith('category_'))
async def add_item_name(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if data['name_call'] == 'add_item':
        await callback.answer()
        await state.update_data(name_call='add_item')
        await state.update_data(category_item=int(callback.data.split('_')[1]))
        await callback.message.answer(text='Введите название товара')
        await state.set_state(ALL.name_item)
    elif data['name_call'] == 'add_image':
        await callback.answer()
        await callback.message.answer(text='Выберите товар для которого нужно добавить изображения',
                                      reply_markup=await kb.set_items(int(callback.data.split('_')[1])))
        await state.update_data(name_call='add_image')
        await state.update_data(mode='admin')
    elif data['name_call'] == 'delete_item':
        if await rq.is_items(int(callback.data.split('_')[1])):
            await callback.answer()
            await callback.message.answer(text='Выберите который нужно удалить',
                                          reply_markup=await kb.set_items(int(callback.data.split('_')[1])))
            await state.update_data(name_call='delete_item')
            await state.update_data(mode='admin')
        else:
            await callback.answer('В этой категории нет товаров', show_alert=True)
    elif data['name_call'] == 'delete_category':
        if await rq.is_items(int(callback.data.split('_')[1])):
            await callback.answer('В этой категории есть товары, ее нельзя удалить', show_alert=True)
        else:
            await callback.answer()
            await callback.message.answer(text='Эту категорию можно удалить',
                                          reply_markup=await kb.complete_category(int(callback.data.split('_')[1])))
    elif data['name_call'] == 'edit_category':
        await callback.answer()
        await callback.message.answer(text='Введите новое название категории')
        await state.update_data(category_id=int(callback.data.split('_')[1]))
        await state.update_data(name_call='edit_category')
        await state.set_state(ALL.category_name)
    elif data['name_call'] == 'edit_item':
        await callback.answer()
        if await rq.is_items(int(callback.data.split('_')[1])):
            await callback.answer()
            await callback.message.answer(text='Выберите товар который нужно отредактировать',
                                          reply_markup=await kb.set_items(int(callback.data.split('_')[1])))
            await state.update_data(name_call='edit_item')
            await state.update_data(mode='admin')
        else:
            await callback.answer('В этой категории нет товаров', show_alert=True)
    elif data['name_call'] == 'delete_image':
        if await rq.is_items(int(callback.data.split('_')[1])):
            await callback.answer()
            await callback.message.answer(text='Выберите товар',
                                          reply_markup=await kb.set_items(int(callback.data.split('_')[1])))
            await state.update_data(name_call='delete_image')
            await state.update_data(mode='admin')
    elif data['name_call'] == 'choose_category':
        await bot.send_chat_action(callback.message.from_user.id, action=ChatAction.TYPING)
        sleep(0.6)
        await callback.answer()
        if int(callback.data.split('_')[1]) == 1:
            await callback.message.answer(text='Выберите торт 🎂',
                                          reply_markup=await kb.set_items(int(callback.data.split('_')[1])))
            await state.update_data(mode='public')
        elif int(callback.data.split('_')[1]) == 2:
            await callback.message.answer(text='Выберите десерт 🍩',
                                          reply_markup=await kb.set_items(int(callback.data.split('_')[1])))
            await state.update_data(mode='public')
        elif int(callback.data.split('_')[1]) == 3:
            await callback.message.answer(text='Выберите рулет 🥐',
                                          reply_markup=await kb.set_items(int(callback.data.split('_')[1])))
            await state.update_data(mode='public')
        else:
            await callback.message.answer(text='Выберите товар 🥮',
                                          reply_markup=await kb.set_items(int(callback.data.split('_')[1])))
            await state.update_data(mode='public')


@call_router.callback_query(F.data == 'add_item')
async def add_item(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(name_call=callback.data)
    await callback.message.answer(text='Выберите в какую категорию добавить товар',
                                  reply_markup=await kb.set_category())


@call_router.callback_query(F.data == 'add_image')
async def add_im(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(name_call=callback.data)
    await callback.message.answer(text='Выберите категорию товара', reply_markup=await kb.set_category())


@call_router.callback_query(F.data.startswith('item_'))
async def add_images(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if data['mode'] == 'admin':
        if data['name_call'] == 'add_image':
            await callback.answer()
            await state.update_data(item_id=int(callback.data.split('_')[1]))
            await callback.message.answer(text='Для начала нажмите на кнопку', reply_markup=kb.image)
        if data['name_call'] == 'delete_item':
            await callback.answer()
            await rq.delete_item(int(callback.data.split('_')[1]))
            await callback.message.answer(text='Товар удален')
        if data['name_call'] == 'edit_item':
            await callback.answer()
            await state.update_data(item_id=int(callback.data.split('_')[1]))
            await callback.message.answer(text='Выберите что нужно изменить',
                                          reply_markup=kb.edit_item_panel)
        if data['name_call'] == 'delete_image':
            if await rq.is_images(int(callback.data.split('_')[1])):
                await callback.answer()
                images = await rq.get_image_url(int(callback.data.split('_')[1]))
                for image in images:
                    await callback.message.answer_photo(photo=image)
                    await callback.message.answer(text='Удалить фотографию',
                                                  reply_markup=await kb.delete_image())
                    await state.update_data(url_image=image)
                    await state.update_data(item_id=int(callback.data.split('_')[1]))
            else:
                await callback.answer('У этого товара нет изображений', show_alert=True)
    else:
        await callback.answer()
        images = await rq.get_item_image(int(callback.data.split('_')[1]))
        item_photos = []
        photos = []
        for image in images:
            photos.append(f'{image.url}')
        for photo in photos:
            item_photos.append(InputMediaPhoto(type='photo', media=photo))
        item = await rq.get_item(int(callback.data.split('_')[1]))
        await bot.send_chat_action(callback.message.from_user.id, action=ChatAction.UPLOAD_PHOTO)
        sleep(0.8)
        await callback.message.answer_media_group(media=item_photos)
        await bot.send_chat_action(callback.message.from_user.id, action=ChatAction.TYPING)
        sleep(0.8)
        await callback.message.answer(text=f'{item.name}\n\n'
                                           f'Описание: \n{item.description}\n\n'
                                           f'Цена {item.price}',
                                      reply_markup=await kb.item_buttons(int(callback.data.split('_')[1])))


@call_router.callback_query(F.data == 'add_url')
async def add_ur(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer(text='Введите Url')
    await state.set_state(ALL.url_image)


@call_router.callback_query(F.data == 'close')
async def close(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(text='Админ панель',
                                  reply_markup=kb.admin_panel)


@call_router.callback_query(F.data == 'delete_item')
async def delete_item(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(name_call=callback.data)
    await callback.message.answer(text='Выберите категорию товара',
                                  reply_markup=await kb.set_category())


@call_router.callback_query(F.data == 'delete_category')
async def delete_category(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(name_call=callback.data)
    await callback.message.answer(text='Выберите категорию',
                                  reply_markup=await kb.set_category())


@call_router.callback_query(F.data.startswith('complete_category'))
async def delete_category(callback: CallbackQuery):
    await callback.answer()
    print(int(callback.data.split('_')[2]))
    await rq.delete_category(int(callback.data.split('_')[2]))
    await callback.message.answer(text='Категория удалена')


@call_router.callback_query(F.data == 'edit_category')
async def edit_category(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(name_call=callback.data)
    await callback.message.answer(text='Выберите категорию, которую хотите отредактировать',
                                  reply_markup=await kb.set_category())


@call_router.callback_query(F.data == 'edit_item')
async def edit_item(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(name_call=callback.data)
    await callback.message.answer(text='Выберите категорию товара',
                                  reply_markup=await kb.set_category())


@call_router.callback_query(F.data == 'edit_item_name')
async def edit_item_name(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    item = await rq.get_item(data['item_id'])
    await callback.message.answer(text=f'Прошлое название: {item.name}')
    await callback.message.answer(text='Введите новое название')
    await state.set_state(ALL.name_item)
    await state.update_data(name_call=callback.data)


@call_router.callback_query(F.data == 'edit_item_description')
async def edit_item_name(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    item = await rq.get_item(data['item_id'])
    await callback.message.answer(text=f'Прошлое описание: {item.description}')
    await callback.message.answer(text='Введите новое описание')
    await state.set_state(ALL.description_item)
    await state.update_data(name_call=callback.data)


@call_router.callback_query(F.data == 'edit_item_price')
async def edit_item_name(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    item = await rq.get_item(data['item_id'])
    await callback.message.answer(text=f'Прошлая цена: {item.price}')
    await callback.message.answer(text='Введите новую цену')
    await state.set_state(ALL.price_item)
    await state.update_data(name_call=callback.data)


@call_router.callback_query(F.data == 'delete_image')
async def delete_image(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(name_call=callback.data)
    await callback.message.answer(text='Выберите категорию товара',
                                  reply_markup=await kb.set_category())


@call_router.callback_query(F.data.startswith('delete_image_'))
async def delete_image(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if await rq.is_image(data['url_image']):
        await rq.del_image(data['url_image'])
        await callback.answer('Фотография удалена', show_alert=True)
        await callback.message.edit_reply_markup(reply_markup=await kb.again_add_image())
        await state.update_data(url_image=data['url_image'])
        await state.update_data(item_id=data['item_id'])
    else:
        await callback.answer('Фотография уже была удалена', show_alert=True)


@call_router.callback_query(F.data == 'again_add_image')
async def again_add_image(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await rq.add_image(data['url_image'], data['item_id'])
    await callback.answer('Фотография добавлена', show_alert=True)
    await callback.message.edit_reply_markup(reply_markup=await kb.delete_image())
