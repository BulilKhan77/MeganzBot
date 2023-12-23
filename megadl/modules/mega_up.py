# Copyright (c) 2023 Itz-fork
# Author: https://github.com/Itz-fork
# Project: https://github.com/Itz-fork/Mega.nz-Bot
# Description: Responsible for upload function

from os import getenv
from time import time
from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from megadl.lib.ddl import Downloader
from megadl.lib.megatools import MegaTools
from megadl.lib.pyros import track_progress

from megadl.helpers.files import cleanup


# Respond only to Documents, Photos, Videos, GIFs, Audio and to urls other than mega
@Client.on_message(
    filters.document
    | filters.photo
    | filters.video
    | filters.animation
    | filters.audio
    | filters.regex(
        r"((http|https)://)(www.)?(?!mega)[a-zA-Z0-9@:%._\+~#?&//=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%._\+~#?&//=]*)"
    )
)
async def to_up(_: Client, msg: Message):
    await msg.reply(
        "Select what you want to do 🤗",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Download 💾", callback_data=f"up_tgdl-{msg.id}")],
                [InlineKeyboardButton("Close ❌", callback_data="closeqcb")],
            ]
        ),
    )


@Client.on_callback_query(filters.regex(r"up_tgdl?.+"))
async def to_up_cb(client: Client, query: CallbackQuery):
    # Get message content
    qcid = query.message.chat.id
    qmid = query.message.id
    strtim = time()
    msg = await client.get_messages(qcid, int(query.data.split("-")[1]))
    # Status msg
    await client.edit_message_text(
        qcid, qmid, "Trying to download the file 📬", reply_markup=None
    )
    # Download files accordingly
    dl_path = None
    if msg.media:
        dl_path = await client.download_media(
            msg, progress=track_progress, progress_args=(client, [qcid, qmid], strtim)
        )
    else:
        dl = Downloader()
        dl_path = await dl.download(
            msg.text, getenv("DOWNLOAD_LOCATION"), client, (qcid, qmid)
        )
    # Upload the file
    cli = MegaTools(client)
    limk = await cli.upload(dl_path, qcid, qmid)
    await client.edit_message_text(
        qcid,
        qmid,
        "Your file has been uploaded to Mega.nz ✅",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Visit 🔗", url=limk)]]
        ),
    )
    cleanup(dl_path)