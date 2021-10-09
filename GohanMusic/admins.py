from asyncio.queues import QueueEmpty
from cache.admins import set
from pyrogram import Client, filters
from pyrogram.types import Message
from callsmusic import callsmusic
from helpers.filters import command, other_filters
from helpers.decorators import errors, authorized_users_only
from config import BOT_USERNAME, que, admins as a

@Client.on_message(command(["reload", f"reload@{BOT_USERNAME}"]) & other_filters)
@errors
@authorized_users_only
async def update_admin(client, message):
    global a
    admins = await client.get_chat_members(message.chat.id, filter="administrators")
    new_ads = []
    for u in admins:
        new_ads.append(u.user.id)
    a[message.chat.id] = new_ads
    await message.reply_text("✅ Bot **berhasil dimulai ulang**\n\n• **Daftar admin** telah **diperbarui**")


@Client.on_message(command(["pause", f"pause@{BOT_USERNAME}"]) & other_filters)
@errors
@authorized_users_only
async def pause(_, message: Message):
    if (
            message.chat.id not in callsmusic.pytgcalls.active_calls
    ) or (
            callsmusic.pytgcalls.active_calls[message.chat.id] == "paused"
    ):
        await message.reply_text("❗ **gada yang lagi nyanyi**")
    else:
        callsmusic.pytgcalls.pause_stream(message.chat.id)
        await message.reply_text("**Pause dulu cape**\n\n• Untuk melanjutkan pemutaran, gunakan perintah » /resume.")


@Client.on_message(command(["resume", f"resume@{BOT_USERNAME}"]) & other_filters)
@errors
@authorized_users_only
async def resume(_, message: Message):
    if (
            message.chat.id not in callsmusic.pytgcalls.active_calls
    ) or (
            callsmusic.pytgcalls.active_calls[message.chat.id] == "playing"
    ):
        await message.reply_text("**Gaada lagu yang dipause**")
    else:
        callsmusic.pytgcalls.resume_stream(message.chat.id)
        await message.reply_text("**Oke lanjut**\n\n• Untuk menjeda pemutaran, gunakan perintah » /pause")


@Client.on_message(command(["end", f"end@{BOT_USERNAME}"]) & other_filters)
@errors
@authorized_users_only
async def stop(_, message: Message):
    if message.chat.id not in callsmusic.pytgcalls.active_calls:
        await message.reply_text("**Gaada lagu yg lagi dinyanyiin**")
    else:
        try:
            callsmusic.queues.clear(message.chat.id)
        except QueueEmpty:
            pass

        callsmusic.pytgcalls.leave_group_call(message.chat.id)
        await message.reply_text("**Turun dulu ye bang**")


@Client.on_message(command(["skip", f"skip@{BOT_USERNAME}"]) & other_filters)
@errors
@authorized_users_only
async def skip(_, message: Message):
    global que
    if message.chat.id not in callsmusic.pytgcalls.active_calls:
        await message.reply_text("**Ngga ada lagu yg bisa di skip**")
    else:
        callsmusic.queues.task_done(message.chat.id)

        if callsmusic.queues.is_empty(message.chat.id):
            callsmusic.pytgcalls.leave_group_call(message.chat.id)
        else:
            callsmusic.pytgcalls.change_stream(
                message.chat.id,
                callsmusic.queues.get(message.chat.id)["file"]
            )
    qeue = que.get(message.chat.id)
    if qeue:
        skip = qeue.pop(0)
    if not qeue:
        return
    await message.reply_text(f"**Skip lagu** {skip[0]}\n**Lagi nyanyiin lagu:** {qeue[0][0]}")
