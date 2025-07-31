from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.db.requests import get_categories, get_items

main_menu = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [KeyboardButton(text='🍰 Каталог')],
    [KeyboardButton(text='🗑 Корзина'),
     KeyboardButton(text='🆘 Помощь')]
])

delete_bin = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Подтвердить заказ ✅', callback_data='complete_bin')],
    [InlineKeyboardButton(text='Очистить корзину 🗑', callback_data='delete_my_bin')]
])

check = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Подтвердить заказ ✅', callback_data='complete_bin')]
])

delivery = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Доставка 🚚', callback_data='car')],
    [InlineKeyboardButton(text='Самовывоз 🧍', callback_data='myself')]
])

reg = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Подтвердить ✅', callback_data='start_reg')]
])

register_number_button = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, keyboard=[
    [KeyboardButton(text='Отправить свой номер 📱', request_contact=True)]
])


async def item_buttons(it_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Добавить в корзину 🗑', callback_data=f'first_bin_{it_id}')],
    ])
    return keyboard


async def item_buttons_2(it_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Добавить +1', callback_data=f'second_bin_{it_id}')],
        [InlineKeyboardButton(text='Моя корзина 🗑', callback_data=f'my_bin')]
    ])
    return keyboard


async def set_category():
    all_categories = await get_categories()
    keyboard = InlineKeyboardBuilder()
    for category in all_categories:
        keyboard.add(InlineKeyboardButton(text=category.name, callback_data=f'category_{category.id}'))
    return keyboard.adjust(2).as_markup()


async def set_items(ct_id):
    all_items = await get_items(ct_id)
    keyboard = InlineKeyboardBuilder()
    for item in all_items:
        keyboard.add(InlineKeyboardButton(text=item.name, callback_data=f'item_{item.id}'))
    return keyboard.adjust(2).as_markup()


# Начало Админ части
admin_panel = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [KeyboardButton(text='Добавить')],
    [KeyboardButton(text='Удалить'),
     KeyboardButton(text='Редактировать')]
])

add_panel = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Добавить категорию', callback_data='add_category')],
    [InlineKeyboardButton(text='Добавить товар', callback_data='add_item')],
    [InlineKeyboardButton(text='Добавить изображение к товару', callback_data='add_image')]
])

delete_panel = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Удалить категорию', callback_data='delete_category')],
    [InlineKeyboardButton(text='Удалить товар из категории', callback_data='delete_item')],
    [InlineKeyboardButton(text='Удалить фотографию товара', callback_data='delete_image')]
])

edit_panel = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Редактировать категорию', callback_data='edit_category')],
    [InlineKeyboardButton(text='Редактировать товар', callback_data='edit_item')]
])


async def complete_category(category_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Подтвердить', callback_data=f'complete_category_{category_id}')]
    ])
    return keyboard


image = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Добавить url', callback_data='add_url')],
    [InlineKeyboardButton(text='Закончить', callback_data='close')]
])

edit_item_panel = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Название', callback_data='edit_item_name')],
    [InlineKeyboardButton(text='Описание', callback_data='edit_item_description')],
    [InlineKeyboardButton(text='Цена', callback_data='edit_item_price')]
])


async def delete_image():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Удалить', callback_data=f'delete_image_')]
    ])
    return keyboard


async def again_add_image():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Вернуть фотографию', callback_data='again_add_image')]
    ])
    return keyboard
