2020 年第四季度以来，MuddyWater
一直针对中东国家发起持久的攻击行动。根据最新发现的样本，研究人员认为攻击活动仍处于活跃状态。MuddyWater
被认为是由伊朗革命卫队运营的组织，主要维护伊朗的国家利益。

攻击通常从一个压缩文件开始，文件中包含一个嵌入 VBA 宏代码的恶意 Word 文档。

![image.png-103.2kB](https://image.3001.net/images/20220701/1656645067_62be65cb0c1152644b86d.png!small)恶意文档样本

根据文件内容，可以看出似乎为讲阿语的用户专门设计的。也有一些样本包含英语的通用消息，诱导用户启用宏代码。

![image.png-138.8kB](https://image.3001.net/images/20220701/1656645067_62be65cbf03e468cc6547.png!small)恶意文档样本

![image.png-196kB](https://image.3001.net/images/20220701/1656645069_62be65cd024d4d1456198.png!small)恶意文档样本

尽管不能明确确定攻击的具体目标，但根据分析攻击针对巴基斯坦、哈萨克斯坦、亚美尼亚、叙利亚、以色列、巴林、土耳其、南非、苏丹等国家。这些国家都被认为是伊朗的利益相关，或者是伊朗在其他地区的发展与战略相关。

宏代码实际上非常简洁，将一个模糊程度不高的 VBS 脚本写入 C:\ProgramData 或 Windows 启动文件夹，文件名为 `Temp_[3-5
随机字符].txt`。

![image.png-291.5kB](https://image.3001.net/images/20220701/1656645069_62be65cdc464665698eeb.png!small)恶意
VBA 宏代码

释放的样本是一个小型的 RAT。首先通过 whoami 进行侦察，再结合所属国家信息构建 C&C 通信的 URI。样本中发现的国家代码有：

> PK -> 巴基斯坦
>
> AR -> 阿根廷
>
> AM -> 亚美尼亚
>
> SY -> 叙利亚
>
> IL -> 以色列
>
> BH -> 巴林
>
> TR -> 土耳其
>
> SA -> 沙特
>
> SD -> 苏丹
>
> KK -> 哈萨克斯坦

![image.png-84.3kB](https://image.3001.net/images/20220701/1656645070_62be65cec7b742ef90185.png!small)去混淆代码

![image.png-64.5kB](https://image.3001.net/images/20220701/1656645071_62be65cf8a3d04745a592.png!small)去混淆代码

函数在执行 explorer.exe 后再调用一个函数从一个数组中选择一个 IP 地址，如果所选 IP 没有回复将会重新选择。C&C 使用的 HTTP
GET 请求结构为：`http://{ IP_address }/getCommand?guid={ recon_string }`。

![image.png-48kB](https://image.3001.net/images/20220701/1656645072_62be65d02c0c23bb3fcd4.png!small)HTTP
GET 请求

没有响应的情况下将轮换下一个 IP 地址。如果有响应则需要去混淆并创建 WScript.Shell 对象来调用函数执行。

![image.png-87kB](https://image.3001.net/images/20220701/1656645072_62be65d0c81a7f39928e0.png!small)部分代码

执行结果输出到 TXT 文件中，读取并将其发送回 C&C 服务器。后续使用 HTTP POST 请求，结构如下所示：

![image.png-65.6kB](https://image.3001.net/images/20220701/1656645073_62be65d17d0508ca65d8f.png!small)HTTP
POST 请求

`flag_value`实际为状态，在脚本中也是一个初始值为 0 的变量。执行并接收命令回传结果后会将其设置为 1，除此之外没有任何修改。在脚本初始执行
whoami_wrap 时会检查该值，与 126 进行比较，如果解析为 True，则会显示以下提示消息。

![image.png-61.5kB](https://image.3001.net/images/20220701/1656645074_62be65d2299ad7ce94802.png!small)提示消息

样本中唯一实现的就是通过 WMI 获取失陷主机相关信息：

![image.png-118.5kB](https://image.3001.net/images/20220701/1656645074_62be65d2c5e3612f92dbb.png!small)部分代码

这样一个功能并不完整的样本，在长达两年的时间被多次用于各种攻击。攻击者可能会根据失陷主机的具体情况，再决定是否需要深入下一阶段。

## IOC

> 4e8a2b592ed90ed13eb604ea2c29bfb3fbc771c799b3615ac84267b85dd26d1c  
> ae6dba7da3c8b2787b274c660e0b522ce8ebda89b1864d8a2ac2c9bb2bd4afa6  
> 185.117.73.52  
> fbd2a9f400740610febd5a1ae7448536dd95f37b85dfd2ca746e11a51086bd4b  
> 2245fc9d9aea07b0ffdac792d4851ceed851a3bf1d528384e94306e59e3abd16  
> 84d523833db6cc74a079b12312da775d4281bf1034b2af0203c9d14c098e6f29  
> cab75e26febd111dd5483666c215bb6b56059f806f83384f864c51ceddd0b1cf  
> faa6258d7bd355329a9ad69e15b2857d24f9ac11a9782d1a215149938460ac4b  
> 2f2492b7bb55f7a12f7530c9973c9b81fdd5e24001e4a21528ff1d5b47e3446e  
> ed4b523a0eecc5de172a97eb8acb357bc1f4807efec761ec2764f20ef028cc63  
> ea24c5a8b976919d4c8c4779dc0b7ef887373f126c4732edf9023b827b4e4dc4  
> 1d133cc388415592e2e2246e6fb1903690068577fc82e2ae682ba0a661cea0dd  
> 107.174.68.60  
> 192.227.147.152  
> dba90bd5fdf0321a28f21fccb3a77ee1ed5d73e863e4520ce8eb8fca670189c3  
> 0b4d660335b55d96ddf4c76664341ed52519639161a0a0a1aa0ae82951feba01

## 参考来源

> [Lab52](https://lab52.io/blog/muddywaters-light-first-stager-targetting-> middle-east/)

