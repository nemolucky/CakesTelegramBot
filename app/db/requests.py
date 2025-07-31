from app.db.models import User, Category, Item, Bin, Image, async_session
from sqlalchemy import select


async def is_user(td_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == td_id))
        if not user:
            return True
        else:
            return False


async def register_user(tg_id, name, phone_number, username):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            user = User(tg_id=tg_id, name=name, phone=phone_number, username=username)
            session.add(user)
            await session.commit()


async def get_categories():
    async with async_session() as session:
        return await session.scalars(select(Category))


async def get_items(ct_id):
    async with async_session() as session:
        return await session.scalars(select(Item).where(Item.category == ct_id))


async def get_item(it_id):
    async with async_session() as session:
        return await session.scalar(select(Item).where(Item.id == it_id))


async def get_item_image(it_id):
    async with async_session() as session:
        return await session.scalars(select(Image).where(Image.item == it_id))


async def get_catalog_image():
    async with async_session() as session:
        return await session.scalars(select(Image))


async def get_bins(tg_id, item_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        session.add(Bin(user=user.id, item=item_id))
        await session.commit()


async def get_my_bin(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        bin_items = await session.scalars(select(Bin).where(Bin.user == user.id))
    return bin_items


async def delete_my_bin(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        bin_items = await session.scalars(select(Bin).where(Bin.user == user.id))
        for bin_item in bin_items:
            await session.delete(bin_item)
            await session.commit()


async def get_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        return user


# Начало Админ части
async def add_category(category_name):
    async with async_session() as session:
        category = Category(name=category_name)
        session.add(category)
        await session.commit()


async def add_item(item_name, item_description, item_price, category_id):
    async with async_session() as session:
        item = Item(name=item_name, description=item_description, price=item_price, category=category_id)
        session.add(item)
        await session.commit()


async def add_image(url, item_id):
    async with async_session() as session:
        image = Image(url=url, item=item_id)
        session.add(image)
        await session.commit()


async def is_items(category_id):
    async with async_session() as session:
        items = await session.scalars(select(Item).where(Item.category == category_id))
        result = []
        for item in items:
            result.append(item.name)
        if len(result) > 0:
            return True
        else:
            return False


async def delete_item(item_id):
    async with async_session() as session:
        item = await session.scalar(select(Item).where(Item.id == item_id))
        images = await session.scalars(select(Image).where(Image.item == item_id))
        for image in images:
            await session.delete(image)
        await session.delete(item)
        await session.commit()


async def delete_category(category_id):
    async with async_session() as session:
        category = await session.scalar(select(Category).where(Category.id == category_id))
        await session.delete(category)
        await session.commit()


async def edit_category(new_name, category_id):
    async with async_session() as session:
        category = await session.scalar(select(Category).where(Category.id == category_id))
        category.name = new_name
        await session.commit()


async def edit_item_name(new_name, item_id):
    async with async_session() as session:
        item = await session.scalar(select(Item).where(Item.id == item_id))
        item.name = new_name
        await session.commit()


async def edit_item_description(new_description, item_id):
    async with async_session() as session:
        item = await session.scalar(select(Item).where(Item.id == item_id))
        item.description = new_description
        await session.commit()


async def edit_item_price(new_price, item_id):
    async with async_session() as session:
        item = await session.scalar(select(Item).where(Item.id == item_id))
        item.price = new_price
        await session.commit()


async def get_image_url(item_id):
    async with async_session() as session:
        images_url = await session.scalars(select(Image.url).where(Image.item == item_id))
        return images_url


async def is_images(item_id):
    async with async_session() as session:
        image_url = await session.scalar(select(Image.url).where(Image.item == item_id))
        if len(image_url) != 0:
            return True
        else:
            return False


async def is_image(url):
    async with async_session() as session:
        image = await session.scalar(select(Image).where(Image.url == url))
        if image is not None:
            return True
        else:
            return False


async def del_image(url):
    async with async_session() as session:
        image = await session.scalar(select(Image).where(Image.url == url))
        await session.delete(image)
        await session.commit()


async def is_bin(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        bins = await session.scalar(select(Bin).where(Bin.user == user.id))
        if bins is None:
            return False
        else:
            return True





