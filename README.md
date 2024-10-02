## 致谢：

[zzseki的音乐插件](https://github.com/zzseki/QChatGPT_Plugin_Music） 和  
[星之阁API](https://api.xingzhige.com)

## 安装

配置完成 [QChatGPT](https://github.com/RockChinQ/QChatGPT) 主程序后使用管理员账号向机器人发送命令即可安装：

```
!plugin get <插件发布仓库地址>
```
或查看详细的[插件安装说明]([https://github.com/RockChinQ/QChatGPT/wiki/5-%E6%8F%92%E4%BB%B6%E4%BD%BF%E7%94%A8](https://qchatgpt.rockchin.top/posts/PluginsUse/plugin_network.html))

## 使用


需要下载安装ffmpeg

Linux可执行如下命令来安装ffmpeg
```
sudo apt install ffmpeg
```


在本插件文件夹下main.py文件中找到这行，并替换成你获取到的uin和skey（不要弄丢引号）

```
self.uin = "YOUR_UIN"  # 请将这里的'YOUR_UIN'替换为你实际获取的o_cookie（其实就是提供skey的qq号）
self.skey = "YOUR_SKEY"  # 请将这里的'YOUR_SKEY'替换为你实际获取的qqmusic_key
```

另外main.py中的self.skey和self.uin为你qq号和qq音乐的qqmusic_key，如果没有请将其设为空，若设为空一些vip歌曲可能无法获取，得看api接口的站长的skey有没有失效了

只能获取QQ音乐上有的音乐


## 注意

如果该插件目录内没有”temp“文件夹需自行创建


## 配置GPT

向QChatGpt发送：播放音乐：XXX(歌名)(空格)XXX(歌手)
也可以不限制歌手，会默认搜索到的第一首音乐
