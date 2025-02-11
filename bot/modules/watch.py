from telegram.ext import CommandHandler
from telegram import Bot, Update
from bot import DOWNLOAD_DIR, dispatcher, LOGGER, Interval, DOWNLOAD_STATUS_UPDATE_INTERVAL, dispatcher, LOGGER
from bot.helper.telegram_helper.message_utils import sendMessage, sendStatusMessage, update_all_messages, sendtextlog
from .mirror import MirrorListener
from bot.helper.mirror_utils.download_utils.youtube_dl_download_helper import YoutubeDLHelper
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.ext_utils.bot_utils import setInterval
import threading
import time


def _watch(bot: Bot, update, isTar=False):
    mssg = update.message.text
    message_args = mssg.split(' ')
    name_args = mssg.split('|')

    try:
        link = message_args[1]
    except IndexError:
        msg = f"/{BotCommands.WatchCommand} [youtube-dl supported link] [quality] |[CustomName] to mirror with youtube-dl.\n\n"
        msg += "<b>Note: Quality and custom name are optional</b>\n\nExample of quality: audio, 144, 240, 360, 480, 720, 1080, 2160."
        msg += "\n\nIf you want to use custom filename, enter it after |"
        msg += f"\n\nExample:\n<code>/{BotCommands.WatchCommand} https://youtu.be/Pk_TthHfLeE 720 |Newname.extension</code>\n\n"
        msg += "This file will be downloaded in 720p quality and it's name will be <b>Newname.extension</b>"
        sendMessage(msg, bot, update)
        return

    try:
      if "|" in mssg:
        mssg = mssg.split("|")
        qual = mssg[0].split(" ")[2]
        if qual == "":
          raise IndexError
      else:
        qual = message_args[2]
      if qual != "audio":
        qual = f'bestvideo[height<={qual}]+bestaudio/best[height<={qual}]'
    except IndexError:
      qual = "bestvideo+bestaudio/best"

    try:
      name = name_args[1]
    except IndexError:
      name = ""
    reply_to = update.message.reply_to_message
    tag = reply_to.from_user.username if reply_to is not None else None
    pswd = ""
    listener = MirrorListener(bot, update, pswd, isTar, tag)
    ydl = YoutubeDLHelper(listener)
    threading.Thread(target=ydl.add_download,args=(link, f'{DOWNLOAD_DIR}{listener.uid}', qual, name)).start()
    uname = f'<a href="tg://user?id={update.message.from_user.id}">{update.message.from_user.first_name}</a>'
    uid = f"<a>{update.message.from_user.id}</a>"
    msg = f"{uname} has sent - \n\n<code>{link}</code>\n\nUser ID : {uid}"
    sendtextlog(msg, bot, update)
    sendStatusMessage(update, bot)
    time.sleep(1)
    if len(Interval) == 0:
        Interval.append(setInterval(DOWNLOAD_STATUS_UPDATE_INTERVAL, update_all_messages))



def watchTar(update, context):
    _watch(context.bot, update, True)


def watch(update, context):
    _watch(context.bot, update)


mirror_handler = CommandHandler(BotCommands.WatchCommand, watch,
                                filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
tar_mirror_handler = CommandHandler(BotCommands.TarWatchCommand, watchTar,
                                    filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
dispatcher.add_handler(mirror_handler)
dispatcher.add_handler(tar_mirror_handler)
