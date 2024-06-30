import telebot
import os
import json
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
request_timeout = int(os.getenv('timeout', 20))
cache = {
    admin_id: {
        "location": "United Kingdom",
        "username": "smarytwahajaka",
        "password": "12441244",
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
    "/check - View current configuration"
)

get_exc = lambda e: e.args[1] if e.args and len(e.args) > 1 else str(e)


def next_step_handler(func):
    """Decorator to pass argument to next_step_handler"""

    def decorator(message: Message):
        return func(message, extract_arguments(message.text))

    return decorator


@bot.message_handler(commands=["start"], is_admin=True)
def usage_info(message: Message):
    """Help info"""
    return bot.reply_to(message, help_info)


@bot.message_handler(commands=["username"], is_admin=True)
@next_step_handler
def accept_username(message: Message, username: str):
    """Accept username"""
    cache[message.from_user.id]["username"] = username
    bot.reply_to(message, "New username set successfully.")


@bot.message_handler(commands=["password"], is_admin=True)
@next_step_handler
def accept_password(message: Message, password: str):
    """Accept password"""
    cache[message.from_user.id]["password"] = password
    bot.reply_to(message, "New password set successfully.")


@bot.message_handler(commands=["location"], is_admin=True)
@next_step_handler
def set_server_location(message: Message, location: str):
    """Take passphrase"""
    if location in country_codes_map:
        cache[message.from_user.id]["location"] = location
        return bot.reply_to(message, "Location set successfully!")

    markup = InlineKeyboardMarkup(row_width=2)
    for location in country_codes_map.keys():
        markup.add(
            InlineKeyboardButton(
                location, callback_data=f"{message.from_user.id}:{location}"
            )
        )
    bot.reply_to(message, "Select Server location", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call: CallbackQuery):
    user, location = call.data.split(":")
    cache[int(user)]["location"] = location
    bot.reply_to(call.message, "Location updated successfully!")


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
        msg = bot.send_photo(
            message.chat.id,
            open(path_to_captcha_image, "rb"),
            "Enter captcha value shown here in /generate.",
        )
        bot.register_next_step_handler(msg, create_server)
    except Exception as e:
        bot.reply_to(message, get_exc(e))
    finally:
        try:
            os.remove(path_to_captcha_image)
        except:
            pass


@bot.message_handler(commands=["generate"], is_admin=True)
@next_step_handler
def create_server(message: Message, captcha: str):
    if not captcha:
        return bot.reply_to(message, "Captcha value is required! - /captcha")
    user_inputs = cache[message.from_user.id]
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
                f"Host : {server_info.data.ip}"
                f"SSH Port : {server_info.data.op}\n"
                f"HTTP Payload : {server_info.data.data.payload_http}\n"
                f"Expiry : {server_info.data.exp}\n"
                f"Location : {user_inputs['location']}\n"
            ),
        )
    except ServerCreationError:
        bot.reply_to(
            message,
            "Failed to create server!"
        )
    except Exception as e:
        bot.reply_to(message, f"{get_exc(e)}")


@bot.message_handler(commands=["check"], is_admin=True)
def check_configuration(message: Message):
    current_config = cache.get(message.from_user.id, {})
    if current_config.get('ssh_instance'):
        current_config.pop('ssh_instance')
    bot.send_message(
        message.chat.id,
        f"```json\n{json.dumps(current_config, indent=4)}\n```",
        parse_mode="Markdown",
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
        )
    else:
        bot.reply_to(message, "{}")


@bot.message_handler(commands=["myid"])
def echo_user_id(message: Message):
    """Show user his Telegram ID"""
    return bot.reply_to(message, message.from_user.id.__str__())


class IsAdminFilter(SimpleCustomFilter):

    key = "is_admin"

    @staticmethod
    def check(message: Message):
        return message.from_user.id == admin_id


bot.add_custom_filter(IsAdminFilter())

if __name__ == "__main__":
    print("Infinity polling ...")
    bot.infinity_polling()
