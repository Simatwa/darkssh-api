import telebot
import os
import json
import random
import string
from telebot.custom_filters import SimpleCustomFilter
from telebot.types import (
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
)
from telebot.util import extract_arguments
from darkssh.main import SSH, country_codes_map
from darkssh.errors import ServerCreationError
from dotenv import load_dotenv

load_dotenv()

bot_token = os.getenv("telegram-token")
admin_id = int(os.getenv("admin-id", 0))
request_timeout = int(os.getenv("timeout", 20))
cache = {
    admin_id: {
        "location": "United Kingdom",
        "username": "smarytwahajaka",
        "password": "12441244",
        "previous_username": "",
    }
}

bot = telebot.TeleBot(token=bot_token)

bot.remove_webhook()

help_info = (
    "Generate ssh servers.\n"
    "Available commands :\n"
    "/start - Show this message.\n"
    "/username - Set username\n"
    "/password - Set password\n"
    "/location - Set server location\n"
    "/captcha - Get captcha image\n"
    "/generate - Generate ssh server.\n"
    "/cached - View recently created server\n"
    "/check - View current configuration\n\n"
    "Made with ❤️ by @AlphaBei from Kenya 🇰🇪"
)

get_exc = lambda e: e.args[1] if e.args and len(e.args) > 1 else str(e)


def random_string(k=16, alphanumeric=False) -> str:
    """Generate random string

    Args:
        k (int, optional): Population. Defaults to 16.
        alphanumeric (bool, optional): Include digits. Defaults to False.

    Returns:
        str: generated string
    """
    return "".join(
        random.sample(
            (
                string.ascii_letters + string.digits
                if alphanumeric
                else string.ascii_letters
            ),
            k,
        )
    )


def next_step_handler(func):
    """Decorator to pass argument to next_step_handler"""

    def decorator(message: Message):
        if len(message.text) > 1:
            return func(message, extract_arguments(message.text))

    return decorator


def inline_delete_markup(message: Message) -> InlineKeyboardMarkup:
    """Make delete markup

    Args:
        message (types.Message): Message obj

    Returns:
        InlineKeyboardMarkup: Delete button markup.
    """
    markup = InlineKeyboardMarkup(row_width=1)
    button = InlineKeyboardButton(
        text="🗑️", callback_data=f"del:{message.chat.id}:{message.id}"
    )
    markup.add(button)
    return markup


@bot.message_handler(commands=["start"], is_admin=True)
def usage_info(message: Message):
    """Help info"""
    markup = inline_delete_markup(message)
    markup.add(InlineKeyboardButton("Contact Developer", "https://t.me/AlphaBei"))
    return bot.reply_to(message, help_info, reply_markup=markup)


@bot.message_handler(commands=["username"], is_admin=True)
@next_step_handler
def accept_username(message: Message, username: str):
    """Accept username"""
    cache[message.from_user.id]["username"] = (
        random_string(12) if username == "random" else username
    )
    bot.reply_to(
        message,
        "New username set successfully.",
        reply_markup=inline_delete_markup(message),
    )


@bot.message_handler(commands=["password"], is_admin=True)
@next_step_handler
def accept_password(message: Message, password: str):
    """Accept password"""
    cache[message.from_user.id]["password"] = (
        random_string(12, True) if password == "random" else password
    )
    bot.reply_to(
        message,
        "New password set successfully.",
        reply_markup=inline_delete_markup(message),
    )


@bot.message_handler(commands=["location"], is_admin=True)
@next_step_handler
def set_server_location(message: Message, location: str):
    """Take passphrase"""
    if location in country_codes_map:
        cache[message.from_user.id]["location"] = location
        return bot.reply_to(
            message,
            "Location set successfully!",
            reply_markup=inline_delete_markup(message),
        )

    markup = InlineKeyboardMarkup(row_width=2)
    location_buttons = map(
        lambda location: InlineKeyboardButton(
            location, callback_data=f"loc:{message.from_user.id}:{location}"
        ),
        country_codes_map.keys(),
    )
    markup.add(*location_buttons)
    markup.add(
        InlineKeyboardButton(
            text="🗑️", callback_data=f"del:{message.chat.id}:{message.id}"
        ),
        row_width=1,
    )

    bot.reply_to(message, "Select Server location", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("loc:"))
def callback_query(call: CallbackQuery):
    _, user, location = call.data.split(":")
    cache[int(user)]["location"] = location
    bot.reply_to(
        call.message,
        "Location updated successfully!",
        reply_markup=inline_delete_markup(call.message),
    )


@bot.message_handler(commands=["captcha"], is_admin=True)
def message_handler(message: Message):
    """Verify capatcha & Generate SSH server"""
    try:
        user = cache[message.from_user.id]
        ssh_instance = SSH(user["location"])
        ssh_instance.timeout = request_timeout
        cache[message.from_user.id]["ssh_instance"] = ssh_instance
        bot.send_chat_action(message.chat.id, "upload_photo")
        path_to_captcha_image = ssh_instance.download_captcha_image()
        markup = inline_delete_markup(message)
        markup.add(
            telebot.types.InlineKeyboardButton(
                text="Generate",
                switch_inline_query_current_chat="/generate ",
            )
        )
        msg = bot.send_photo(
            message.chat.id,
            open(path_to_captcha_image, "rb"),
            "Enter captcha value shown here in /generate.",
            reply_markup=markup,
        )
        bot.register_next_step_handler(msg, create_server)
    except Exception as e:
        bot.reply_to(message, get_exc(e), reply_markup=inline_delete_markup(message))
    finally:
        try:
            os.remove(path_to_captcha_image)
        except:
            pass


@bot.message_handler(func=lambda msg: "/generate" in msg.text.split(' '), is_admin=True)
# @next_step_handler
def create_server(message: Message):
    splitted_text = message.text.split(" ")
    if len(splitted_text) > 1:
        captcha = splitted_text[len(splitted_text) - 1]
    else:
        markup = telebot.types.ForceReply(selective=True)
        return bot.reply_to(
            message, "Captcha value is required! - /captcha", reply_markup=markup
        )

    user_inputs = cache[message.from_user.id]
    if user_inputs["username"] == user_inputs["previous_username"]:
        user_inputs["username"] = random_string()

    user_ssh_instance: SSH = user_inputs["ssh_instance"]
    try:
        server_info = user_ssh_instance.generate(
            username=user_inputs["username"],
            password=user_inputs["password"],
            captcha=captcha,
        )
        cache[message.from_user.id]["server_cache"] = server_info
        bot.send_message(
            message.chat.id,
            (
                f"Username : {server_info.data.username}\n"
                f"Password : {server_info.data.password}\n"
                f"Host : {server_info.data.ip}\n"
                f"SSH Port : {server_info.data.op}\n"
                f"HTTP Payload : {server_info.data.data.payload_http}\n"
                f"Expiry : {server_info.data.exp}\n"
                f"Location : {user_inputs['location']}\n"
            ),
            reply_markup=inline_delete_markup(message),
        )
    except ServerCreationError:
        bot.reply_to(
            message,
            "Failed to create server!",
            reply_markup=inline_delete_markup(message),
        )
    except Exception as e:
        bot.reply_to(
            message, f"{get_exc(e)}", reply_markup=inline_delete_markup(message)
        )


@bot.message_handler(commands=["check"], is_admin=True)
def check_configuration(message: Message):
    current_config = cache.get(message.from_user.id, {}).copy()
    for key, value in current_config.items():
        current_config[key] = str(value)

    bot.send_message(
        message.chat.id,
        f"```json\n{json.dumps(current_config, indent=4)}\n```",
        parse_mode="Markdown",
        reply_markup=inline_delete_markup(message),
    )


@bot.message_handler(commands=["cached"], is_admin=True)
def view_cache(message: Message):
    """Last server generated info"""
    cached_server_info = cache[message.from_user.id].get(
        "server_cache",
    )
    if cached_server_info:
        bot.send_message(
            message.chat.id,
            f"```json\n{cached_server_info.model_dump_json(indent=4)}\n```",
            parse_mode="Markdown",
            reply_markup=inline_delete_markup(message),
        )
    else:
        bot.reply_to(message, "{}", reply_markup=inline_delete_markup(message))


@bot.message_handler(commands=["myid"])
def echo_user_id(message: Message):
    """Show user his Telegram ID"""
    return bot.reply_to(
        message,
        message.from_user.id.__str__(),
        reply_markup=inline_delete_markup(message),
    )


@bot.message_handler(func=lambda msg: True, is_admin=True)
def unknown_action(message: Message):
    return bot.reply_to(message, help_info, reply_markup=inline_delete_markup(message))


@bot.callback_query_handler(func=lambda call: call.data.startswith("del:"))
def delete_button_callback_handler(call: CallbackQuery):
    """Deletes a sent message"""
    _, chat_id, msg_id = call.data.split(":")
    try:
        bot.delete_message(chat_id, msg_id)
        bot.delete_message(call.message.chat.id, call.message.id)
    except Exception as e:
        try:
            bot.delete_message(call.message.chat.id, call.message.id)
        except:
            pass
        pass


class IsAdminFilter(SimpleCustomFilter):

    key = "is_admin"

    @staticmethod
    def check(message: Message):
        return message.from_user.id == admin_id


bot.add_custom_filter(IsAdminFilter())

if __name__ == "__main__":
    cache[admin_id]["username"] = random_string()
    print("Infinity polling ...")
    bot.infinity_polling()
