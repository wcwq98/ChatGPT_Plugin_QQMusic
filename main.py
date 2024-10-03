from pkg.plugin.context import register, handler, BasePlugin, APIHost, EventContext
from pkg.plugin.events import *  # 导入事件类
from mirai import Voice, Plain
import os
import requests
import httpx
import logging
import re
import shutil
from pathlib import Path
from pydub import AudioSegment
from graiax import silkcoder

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 注册插件
@register(name="QQMusic", description="QQ音乐插件", version="0.1", author="wcwq98")
class QQMusic(BasePlugin):
    def __init__(self, host: APIHost):
        self.uin = "YOUR_UIN"  # 请将这里的'YOUR_UIN'替换为你实际获取的uin
        self.skey = "YOUR_SKEY"  # 请将这里的'YOUR_SKEY'替换为你实际获取的skey
        self.logger = logger

    @handler(PersonNormalMessageReceived)
    async def person_normal_message_received(self, ctx: EventContext):
        await self.handle_message(ctx)

    @handler(GroupNormalMessageReceived)
    async def group_Normal_message_received(self, ctx: EventContext):
        await self.handle_message(ctx)

    async def handle_message(self, ctx: EventContext):
        receive_text = ctx.event.text_message
        self.logger.info(f"收到消息: {receive_text}")
        # 修改正则表达式以支持中文和英文冒号
        MUSIC_PATTERN = re.compile(r"播放音乐[:：](.+)")
        match = MUSIC_PATTERN.search(receive_text)
        if match:
            music_name = match.group(1)
            self.logger.info(f"匹配到音乐名称: {music_name}")
            src = await self.get_music_src(music_name)
            if src:
                self.logger.info(f"获取到音乐直链: {src}")
                mp3_path = os.path.join(os.path.dirname(__file__), "temp", "temp.mp3")
                wav_path = os.path.join(os.path.dirname(__file__), "temp", "temp.wav")
                flac_path = os.path.join(os.path.dirname(__file__), "temp", "temp.flac")
                if re.search("flac", src):
                    file_type = "flac"
                    save_path = flac_path
                elif re.search("mp3", src):
                    file_type = "mp3"
                    save_path = mp3_path
                else:
                    file_type = "wav"
                    save_path = wav_path
                if await self.download_audio(src, save_path):
                    silk_file = self.convert_to_silk(save_path)
                    ctx.add_return("reply", [Voice(path=str(silk_file))])
                    self.logger.info(f"播放音乐：{music_name}")
                    ctx.prevent_default()
            else:
                ctx.add_return("reply", [Plain("未能找到该音乐，请检查名称是否正确。")])
                ctx.prevent_default()
        else:
            self.logger.info("未匹配到音乐请求")

    async def download_audio(self, audio_url, save_path):
        try:
            response = requests.get(audio_url)
            if response.status_code == 200:
                with open(save_path, "wb") as file:
                    file.write(response.content)
                self.logger.info(f"音频文件已成功保存为 '{save_path}'")
                return True
            else:
                self.logger.error(f"下载音频文件失败，状态码: {response.status_code}")
                return False
        except Exception as e:
            self.logger.error(f"下载音频文件发生异常: {str(e)}")
            return False

    def convert_to_silk(self, save_path: str) -> str:
        temp_folder = os.path.join(os.path.dirname(__file__), "temp")
        silk_path = os.path.join(temp_folder, Path(save_path).stem + ".silk")
        wav_path = save_path

        if save_path.endswith(".mp3"):
            self.logger.info(f"正在将 MP3 文件 {save_path} 转换为 WAV")
            wav_path = os.path.join(temp_folder, Path(save_path).stem + ".wav")
            # 将 mp3 转换为 wav
            audio = AudioSegment.from_mp3(save_path)
            audio.export(wav_path, format="wav")
            self.logger.info(f"MP3 文件已成功转换为 WAV 文件 {wav_path}")

        elif save_path.endswith(".flac"):
            self.logger.info(f"正在将 flac 文件 {save_path} 转换为 WAV")
            wav_path = os.path.join(temp_folder, Path(save_path).stem + ".wav")
            # 将 flac 转换为 wav
            audio = AudioSegment.from_file(save_path, format="flac")
            audio.export(wav_path, format="wav")
            self.logger.info(f"flac 文件已成功转换为 WAV 文件 {wav_path}")

        try:
            silkcoder.encode(wav_path, silk_path)
            self.logger.info(f"已将 WAV 文件 {wav_path} 转换为 SILK 文件 {silk_path}")
            return silk_path
        except Exception as e:
            self.logger.error(f"SILK 文件转换失败: {str(e)}")
            return None

    async def get_music_src(self, keyword):
        url = "https://api.xingzhige.com/API/QQmusicVIP/"
        params = {
            "name": keyword,
            "uin": self.uin,
            "skey": self.skey,
            "max": 3,
            "n": 1
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                if data and data.get("code") == 0:
                    src = data["data"]["src"]
                    return src
                else:
                    self.logger.error(f"获取音乐直链失败: {data}")
                    return None
            except httpx.HTTPStatusError as e:
                self.logger.error(f"获取音乐直链失败: {str(e)}")
                return None
                
    # 插件卸载时触发
    def __del__(self):
        if hasattr(self, 'folder_path'):
            shutil.rmtree(self.folder_path)
