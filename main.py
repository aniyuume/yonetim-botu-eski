import discord
from discord.ext import commands
from discord.ui import View, Button, Modal, TextInput
import json
import time
import os

def json_yükle(dosya) -> dict:
    with open(dosya, "r", encoding="utf-8") as d:
        return json.load(d)

def json_yaz(dosya, veri) -> None:
    with open(dosya, "w", encoding="utf-8") as d:
        json.dump(veri, d, ensure_ascii=False, indent=4)

başlangıç = time.time()
config = json_yükle("config.json")
izinler = discord.Intents.all()
bot = commands.Bot(command_prefix=config["prefix"], intents=izinler, help_command=None)
bot.oto_mesaj = json_yükle("oto_mesaj.json")

def uptime() -> str:
    uptime_seconds = int(time.time() - başlangıç)
    days = uptime_seconds // (24 * 3600)
    hours = (uptime_seconds % (24 * 3600)) // 3600
    minutes = (uptime_seconds % 3600) // 60

    return f"{days} gün, {hours} saat, {minutes} dakika"

@bot.event
async def on_ready():
    await bot.tree.sync()
    print("Slash komutları yenilendi!")

    print(f"{bot.user.name} aktif!")

@bot.event
async def on_member_join(member : discord.Member):
    if member.guild.id == config["ana_sunucu"]:
        kanal = await bot.fetch_channel(config["giriş_çıkış"])
        user  = await bot.fetch_user(member.id)
        avatar = user.avatar.url if user.avatar else user.default_avatar.url
        banner = user.banner.url if user.banner else None

        await kanal.send(
            embed=discord.Embed(
                title="Yeni Üye!",
                description=f"{user.mention} aramıza katıldı! Artık sunucumuz {member.guild.member_count} üyeye sahip.",
                color=0x00ff00
            ).set_thumbnail(
                url=avatar
            ).set_image(
                url="https://cdn.discordapp.com/attachments/1421560795732381778/1494054936672079893/image-19.jpg?ex=69e13697&is=69dfe517&hm=92b7ee2673c69fedef305a04df2221e2f0eba1e06795400e55f477e9e2f53694&"
            )
        )

@bot.event
async def on_member_remove(member : discord.Member):
    if member.guild.id == config["ana_sunucu"]:
        kanal = await bot.fetch_channel(config["giriş_çıkış"])
        user  = await bot.fetch_user(member.id)
        avatar = user.avatar.url if user.avatar else user.default_avatar.url
        banner = user.banner.url if user.banner else None

        await kanal.send(
            embed=discord.Embed(
                title="Ayrılan Üye!",
                description=f"{user.name} aramızdan ayrıldı! Artık sunucumuz {member.guild.member_count} üyeye sahip.",
                color=0xff0000
            ).set_thumbnail(
                url=avatar
            ).set_image(
                url="https://cdn.discordapp.com/attachments/1421560795732381778/1494054936672079893/image-19.jpg?ex=69e13697&is=69dfe517&hm=92b7ee2673c69fedef305a04df2221e2f0eba1e06795400e55f477e9e2f53694&"
            )
        )

@bot.event
async def on_message(message : discord.Message):
    if message.guild:
        gid = str(message.guild.id)
        if gid in bot.oto_mesaj.keys():
            for mesaj in bot.oto_mesaj[gid].keys():
                if mesaj in message.content.lower().split():
                    await message.reply(bot.oto_mesaj[gid][mesaj])

    await bot.process_commands(message)

@bot.command(aliases=["info"])
async def bilgi(ctx : commands.Context):
    avatar = bot.user.avatar.url if bot.user.avatar else bot.user.default_avatar.url
    await ctx.send(
        embed=discord.Embed(
            title="Bilgi",
            description=f"""
Prefix: {config['prefix']}
Uptime: {uptime()}
"""         ,
            color=0xF6F478
        ).set_thumbnail(url=avatar
        ).set_footer(text=bot.user.name)
    )

@bot.command()
async def kanala_katıl(ctx : commands.Context, channel : discord.VoiceChannel = None):
    channel = channel or (ctx.author.voice.channel if ctx.author.voice else None)
    if channel:
        if ctx.guild:
            if channel.permissions_for(ctx.author).manage_channels:
                await channel.connect(timeout=99999999999999999)
                embed = discord.Embed(
                    title="KANALA KATILINDI",
                    description=f"Bot {channel.name} kanalına katıldı.",
                    color=0x00FF00
                ).set_footer(text=ctx.guild.name)
            else:
                embed = discord.Embed(
                    title="HATA!",
                    description=f"Bu komutu kullanmak için kanalları yönetme iznine sahip olmanız lazım!",
                    color=0xFF0000
                ).set_footer(text=f"Komut {ctx.author.mention} tarafından kullanıldı!")
        else:
            embed = discord.Embed(
                title="HATA",
                description="Bu komut DM üzerinde kullanılamaz.",
                color=0xFF0000
            )
    else:
        embed = discord.Embed(
            title="HATA",
            description="Bir ses kanalına katılmadınız veya bir ses kanalı belirtmediniz!",
            color=0xFF0000
        )

    await ctx.send(embed=embed)

@bot.tree.command(
    name="bilgi",
    description="Bot hakkında bilgi verir."
)
async def bilgi_slash(interaction : discord.Interaction):
    avatar = bot.user.avatar.url if bot.user.avatar else bot.user.default_avatar.url
    await interaction.response.send_message(
        embed=discord.Embed(
            title="Bilgi",
            description=f"""
Prefix: {config['prefix']}
Uptime: {uptime()}
Kaynak kodları: {config["github_linki"]}
"""         ,
            color=0xF6F478
        ).set_thumbnail(url=avatar
        ).set_footer(text=bot.user.name)
    )

bot.run(os.getenv("TOKEN")
