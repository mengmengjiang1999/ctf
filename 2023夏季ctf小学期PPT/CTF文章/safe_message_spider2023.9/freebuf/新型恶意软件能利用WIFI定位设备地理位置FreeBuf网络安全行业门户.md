Secureworks的研究人员发现，Smoke Loader 僵尸网络背后的网络犯罪分子正在使用一种名为 Whiffy Recon 的新恶意软件，通过
WiFi 扫描和 Google 地理定位 API 来定位受感染设备的位置。

![](https://image.3001.net/images/20230825/1692932300_64e818cca749ccb9918ff.png!small)

Google 的地理定位 API 是一项带有 WiFi 接入点信息的 HTTPS 请求，能返回纬度和经度坐标以定位没有 GPS 系统的设备。

在 Whiffy Recon 的案例中，了解受害者的位置有助于更好地针对特定地区甚至城市进行攻击，或者通过展示跟踪能力来帮助恐吓受害者。根据该区域 WiFi
接入点的数量，通过 Google 地理定位 API 进行的三角测量精度范围可达20米——50 米甚至更小。但在人口密度较低的区域，该精度可能会降低。

恶意软件首先检查服务名称“WLANSVC”，如果不存在，则会将僵尸程序注册到命令和控制（C2）服务器并跳过扫描部分。

![](https://image.3001.net/images/20230825/1692932316_64e818dc25f87b75d2818.png!small)Whiffy
Recon 主要功能

对于存在该服务的 Windows 系统，Whiffy Recon 会进入每分钟运行一次的 WiFi 扫描循环，滥用 Windows WLAN API
来收集所需数据，并向 Google 的地理定位 API 发送包含 JSON 格式的 WiFi 接入点信息的 HTTPS POST 请求。

使用 Google 响应中的坐标，恶意软件会制定有关接入点更完整的报告，包括其地理位置、加密方法、SSID，并将其作为 JSON POST
请求发送到攻击者的 C2。

由于此过程每 60 秒发生一次，因此攻击者可以几乎实时对设备进行跟踪。

Secureworks的研究人员于 8 月 8 日发现了这种新型恶意软件，并注意到恶意软件在向 C2 发出的初始 POST
请求中使用的版本号是“1”，表明恶意软件可能还会存在后续开发版本。

> 参考来源：[New Whiffy Recon malware uses WiFi to triangulate your
> location](https://www.bleepingcomputer.com/news/security/new-whiffy-recon-> malware-uses-wifi-to-triangulate-your-location/)

