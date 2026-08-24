import html
import logging

from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InputMediaPhoto,
)


# =========================================================
# بيانات البوت
# =========================================================

API_ID = 26022471
API_HASH = "c677f19844c6ceb21e6e0ece33561ddd"
BOT_TOKEN = "8666418252:AAH1jstO2XfO6XCkGhIwvmC9Y9vzXZEhPUQ"

SESSION_NAME = "ID_Premium_Session"
MAX_PHOTOS = 10


# =========================================================
# Logging
# =========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


# =========================================================
# التحقق من البيانات
# =========================================================

if not API_ID:
    raise ValueError("❌ API_ID غير موجود.")

if not API_HASH or API_HASH == "ضع_API_HASH_هنا":
    raise ValueError("❌ ضع API_HASH الصحيح مكان النص الموجود.")

if not BOT_TOKEN or BOT_TOKEN == "ضع_BOT_TOKEN_هنا":
    raise ValueError("❌ ضع BOT_TOKEN الصحيح مكان النص الموجود.")


# =========================================================
# Pyrogram Client
# =========================================================

app = Client(
    SESSION_NAME,
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)


# =========================================================
# أدوات مساعدة
# =========================================================

def safe_text(text):
    """حماية النص عند استخدام HTML."""
    return html.escape(str(text or ""))


def premium_text(user):
    """عرض حالة Premium."""
    if getattr(user, "is_premium", False):
        return "بريميوم 👑"

    return "عادي"


def username_text(user):
    """عرض اليوزر."""
    if getattr(user, "username", None):
        return "@" + safe_text(user.username)

    return "لا يوجد"


def profile_link(user):
    """رابط فتح بروفايل المستخدم."""
    return f"tg://user?id={user.id}"


def build_caption(user, index, total):
    """إنشاء وصف الصورة."""

    return (
        "👤 <b>بطاقة الهوية المميزة</b>\n\n"
        f"🆔 <b>الأيدي:</b> <code>{user.id}</code>\n"
        f"✨ <b>الاسم:</b> {safe_text(user.first_name or 'غير معروف')}\n"
        f"👤 <b>اليوزر:</b> {username_text(user)}\n"
        f"💎 <b>الحساب:</b> {premium_text(user)}\n"
        f"📸 <b>الصورة:</b> {index + 1} من {total}"
    )


# =========================================================
# Keyboard
# =========================================================

def build_keyboard(user, index, total):

    navigation = []

    # زر الصورة السابقة
    if index > 0:
        navigation.append(
            InlineKeyboardButton(
                "◀️",
                callback_data=f"photo:{user.id}:{index - 1}"
            )
        )

    # المؤشر
    dots = "".join(
        "🔘" if i == index else "⚪"
        for i in range(total)
    )

    navigation.append(
        InlineKeyboardButton(
            dots,
            callback_data="nothing"
        )
    )

    # زر الصورة التالية
    if index < total - 1:
        navigation.append(
            InlineKeyboardButton(
                "▶️",
                callback_data=f"photo:{user.id}:{index + 1}"
            )
        )

    return InlineKeyboardMarkup(
        [
            navigation,
            [
                InlineKeyboardButton(
                    "👤 فتح البروفايل",
                    url=profile_link(user)
                )
            ],
            [
                InlineKeyboardButton(
                    "🔄 تحديث",
                    callback_data=f"refresh:{user.id}:{index}"
                )
            ]
        ]
    )


# =========================================================
# START
# =========================================================

@app.on_message(filters.command("start"))
async def start_command(client, message):

    user = message.from_user

    if not user:
        return

    name = safe_text(user.first_name or "صديقي")

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🆔 عرض الـ ID",
                    callback_data="my_id"
                )
            ],
            [
                InlineKeyboardButton(
                    "ℹ️ المساعدة",
                    callback_data="help"
                )
            ]
        ]
    )

    text = (
        f"👋 أهلاً {name}\n\n"
        "💎 <b>ID Premium</b>\n\n"
        "بوت لعرض معلومات المستخدم وصور البروفايل.\n\n"
        "🆔 <code>/id</code> — عرض البيانات\n"
        "🆔 <code>/ايدي</code> — عرض البيانات\n"
        "ℹ️ <code>/help</code> — المساعدة\n\n"
        "💡 يمكنك عمل Reply على رسالة أي شخص "
        "ثم إرسال <code>/id</code>."
    )

    await message.reply_text(
        text,
        parse_mode="html",
        reply_markup=keyboard
    )


# =========================================================
# HELP
# =========================================================

@app.on_message(filters.command("help"))
async def help_command(client, message):

    text = (
        "ℹ️ <b>مساعدة ID Premium</b>\n\n"
        "🆔 <code>/id</code> — عرض بياناتك.\n"
        "🆔 <code>/ايدي</code> — عرض بياناتك.\n\n"
        "👤 لعرض بيانات شخص آخر:\n"
        "اعمل Reply على رسالته ثم اكتب <code>/id</code>.\n\n"
        "📸 يمكنك التنقل بين صور البروفايل."
    )

    await message.reply_text(
        text,
        parse_mode="html"
    )


# =========================================================
# ID COMMAND
# =========================================================

@app.on_message(
    filters.command(["id", "ايدي"])
    & (filters.private | filters.group)
)
async def id_command(client, message):

    try:

        # تحديد المستخدم
        if (
            message.reply_to_message
            and message.reply_to_message.from_user
        ):
            user = message.reply_to_message.from_user
        else:
            user = message.from_user

        if not user:
            await message.reply_text(
                "❌ لم أستطع تحديد المستخدم."
            )
            return

        # جلب صور البروفايل
        photos = [
            photo
            async for photo in client.get_chat_photos(
                user.id,
                limit=MAX_PHOTOS
            )
        ]

        total = len(photos)

        # =================================================
        # لا توجد صور
        # =================================================

        if total == 0:

            text = (
                "👤 <b>بطاقة الهوية المميزة</b>\n\n"
                f"🆔 <b>الأيدي:</b> <code>{user.id}</code>\n"
                f"✨ <b>الاسم:</b> "
                f"{safe_text(user.first_name or 'غير معروف')}\n"
                f"👤 <b>اليوزر:</b> {username_text(user)}\n"
                f"💎 <b>الحساب:</b> {premium_text(user)}\n\n"
                "📸 <i>لا توجد صورة بروفايل.</i>"
            )

            await message.reply_text(
                text,
                parse_mode="html"
            )

            return

        # =================================================
        # توجد صور
        # =================================================

        await message.reply_photo(
            photo=photos[0].file_id,
            caption=build_caption(user, 0, total),
            parse_mode="html",
            reply_markup=build_keyboard(user, 0, total)
        )

    except Exception as error:

        logger.exception(
            "ID command error: %s",
            error
        )

        await message.reply_text(
            "❌ حصل خطأ أثناء جلب بيانات المستخدم."
        )


# =========================================================
# PHOTO NAVIGATION
# =========================================================

@app.on_callback_query(
    filters.regex(r"^photo:(\d+):(\d+)$")
)
async def photo_callback(client, callback_query):

    try:

        parts = callback_query.data.split(":")

        user_id = int(parts[1])
        index = int(parts[2])

        # جلب المستخدم
        user = await client.get_users(user_id)

        # جلب الصور من جديد
        photos = [
            photo
            async for photo in client.get_chat_photos(
                user_id,
                limit=MAX_PHOTOS
            )
        ]

        total = len(photos)

        # لا توجد صور
        if total == 0:

            await callback_query.answer(
                "❌ لا توجد صور.",
                show_alert=True
            )

            return

        # التحقق من رقم الصورة
        if index < 0 or index >= total:

            await callback_query.answer(
                "❌ الصورة غير موجودة.",
                show_alert=True
            )

            return

        # تجهيز الصورة
        media = InputMediaPhoto(
            media=photos[index].file_id,
            caption=build_caption(
                user,
                index,
                total
            ),
            parse_mode="html"
        )

        # تغيير الصورة
        await callback_query.edit_message_media(
            media=media,
            reply_markup=build_keyboard(
                user,
                index,
                total
            )
        )

        await callback_query.answer()

    except Exception as error:

        logger.exception(
            "Photo callback error: %s",
            error
        )

        await callback_query.answer(
            "❌ حصل خطأ أثناء تغيير الصورة.",
            show_alert=True
        )


# =========================================================
# REFRESH
# =========================================================

@app.on_callback_query(
    filters.regex(r"^refresh:(\d+):(\d+)$")
)
async def refresh_callback(client, callback_query):

    try:

        parts = callback_query.data.split(":")

        user_id = int(parts[1])
        index = int(parts[2])

        # جلب المستخدم
        user = await client.get_users(user_id)

        # جلب الصور
        photos = [
            photo
            async for photo in client.get_chat_photos(
                user_id,
                limit=MAX_PHOTOS
            )
        ]

        total = len(photos)

        # لا توجد صور
        if total == 0:

            await callback_query.answer(
                "📸 لا توجد صور.",
                show_alert=True
            )

            return

        # لو عدد الصور قل
        if index >= total:
            index = total - 1

        # تجهيز الصورة
        media = InputMediaPhoto(
            media=photos[index].file_id,
            caption=build_caption(
                user,
                index,
                total
            ),
            parse_mode="html"
        )

        # تحديث الرسالة
        await callback_query.edit_message_media(
            media=media,
            reply_markup=build_keyboard(
                user,
                index,
                total
            )
        )

        await callback_query.answer(
            "🔄 تم التحديث."
        )

    except Exception as error:

        logger.exception(
            "Refresh error: %s",
            error
        )

        await callback_query.answer(
            "❌ فشل التحديث.",
            show_alert=True
        )


# =========================================================
# MY ID BUTTON
# =========================================================

@app.on_callback_query(
    filters.regex(r"^my_id$")
)
async def my_id_callback(client, callback_query):

    try:

        user = callback_query.from_user

        if not user:
            await callback_query.answer(
                "❌ لم أستطع تحديد حسابك.",
                show_alert=True
            )
            return

        # جلب الصور
        photos = [
            photo
            async for photo in client.get_chat_photos(
                user.id,
                limit=MAX_PHOTOS
            )
        ]

        total = len(photos)

        # بدون صورة
        if total == 0:

            await callback_query.answer(
                f"🆔 ID الخاص بك: {user.id}",
                show_alert=True
            )

            return

        # إرسال بطاقة المستخدم
        await callback_query.message.reply_photo(
            photo=photos[0].file_id,
            caption=build_caption(
                user,
                0,
                total
            ),
            parse_mode="html",
            reply_markup=build_keyboard(
                user,
                0,
                total
            )
        )

        await callback_query.answer()

    except Exception as error:

        logger.exception(
            "My ID error: %s",
            error
        )

        await callback_query.answer(
            "❌ حصل خطأ.",
            show_alert=True
        )


# =========================================================
# HELP BUTTON
# =========================================================

@app.on_callback_query(
    filters.regex(r"^help$")
)
async def help_callback(client, callback_query):

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🔙 رجوع",
                    callback_data="back_start"
                )
            ]
        ]
    )

    await callback_query.message.edit_text(
        "ℹ️ <b>ID Premium</b>\n\n"
        "🆔 /id — بيانات المستخدم\n"
        "🆔 /ايدي — بيانات المستخدم\n\n"
        "👤 اعمل Reply على رسالة شخص ثم اكتب /id.\n\n"
        "📸 تنقل بين الصور من الأسهم.\n"
        "🔄 استخدم زر التحديث.",
        parse_mode="html",
        reply_markup=keyboard
    )

    await callback_query.answer()


# =========================================================
# BACK BUTTON
# =========================================================

@app.on_callback_query(
    filters.regex(r"^back_start$")
)
async def back_callback(client, callback_query):

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🆔 عرض الـ ID",
                    callback_data="my_id"
                )
            ],
            [
                InlineKeyboardButton(
                    "ℹ️ المساعدة",
                    callback_data="help"
                )
            ]
        ]
    )

    await callback_query.message.edit_text(
        "💎 <b>ID Premium</b>\n\n"
        "اختار من القائمة:",
        parse_mode="html",
        reply_markup=keyboard
    )

    await callback_query.answer()


# =========================================================
# NOTHING BUTTON
# =========================================================

@app.on_callback_query(
    filters.regex(r"^nothing$")
)
async def nothing_callback(client, callback_query):

    await callback_query.answer()


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    print("===================================")
    print("⚡ ID Premium Bot")
    print("⚡ البوت يعمل الآن...")
    print("===================================")

    app.run()
