## 一、Acunetix安装

1、下载软件压缩包文件，首先点击“Acunetix.Web.12.0.180911134.Retail.exe”安装最新版原程序

![1600959162_5f6cb2ba6c75fb255462b.png!small](https://image.3001.net/images/20200924/1600959162_5f6cb2ba6c75fb255462b.png!small)

2、阅读并同意软件安装协议

![1600959190_5f6cb2d62650d1622e1e3.png!small](https://image.3001.net/images/20200924/1600959190_5f6cb2d62650d1622e1e3.png!small)

3、设置登录信息，包括邮箱地址以及登录密码

![1600959213_5f6cb2edd655dfcb7eb39.png!small](https://image.3001.net/images/20200924/1600959213_5f6cb2edd655dfcb7eb39.png!small)

不需要真实的邮箱，但是需要记住填写的邮箱和密码。

4、设置默认端口，一般默认为3443

![1600959267_5f6cb323d075b1b923d24.png!small](https://image.3001.net/images/20200924/1600959267_5f6cb323d075b1b923d24.png!small)

5、选择附加任务，建议创建桌面快捷方式

![1600959289_5f6cb33993475db4ce0c8.png!small](https://image.3001.net/images/20200924/1600959289_5f6cb33993475db4ce0c8.png!small)

6、核对安装信息，确认无误后即可点击【Install】按钮继续

![1600959311_5f6cb34f59e64301cff06.png!small](https://image.3001.net/images/20200924/1600959311_5f6cb34f59e64301cff06.png!small)

7、等待程序安装完毕，直接点击【Finish】按钮退出向导即可

![1600959329_5f6cb361187d6c804d047.png!small](https://image.3001.net/images/20200924/1600959329_5f6cb361187d6c804d047.png!small)

8、打开任务管理器，停止服务中的 acunetix. msc

![1600959348_5f6cb3749afeb8d659ce0.png!small](https://image.3001.net/images/20200924/1600959348_5f6cb3749afeb8d659ce0.png!small)

不一定有，我安装时就没有。

9、将破解补丁复制到软件根目录下，双击打开，点击应用即可  
默认路径为：C:\Program Files (x86)\Acunetix\12.0.180911134

![1600959374_5f6cb38ed1b77203bdebd.png!small](https://image.3001.net/images/20200924/1600959374_5f6cb38ed1b77203bdebd.png!small)

10、在激活窗口中输入任何信息

![1600959406_5f6cb3ae89a57a1cef4e9.png!small](https://image.3001.net/images/20200924/1600959406_5f6cb3ae89a57a1cef4e9.png!small)

11、默认即可，直接点击下一部

![1600959426_5f6cb3c2c895503d1ddf7.png!small](https://image.3001.net/images/20200924/1600959426_5f6cb3c2c895503d1ddf7.png!small)

12、注册成功，点击【Finish】退出即可

![1600959444_5f6cb3d4d182ee1e46517.png!small](https://image.3001.net/images/20200924/1600959444_5f6cb3d4d182ee1e46517.png!small)

13、以管理员身份运行 cmd 并运行cacls "C:\ProgramData\Acunetix\shared\license." /t /p
everyone:r  
选择"是"

![1600959461_5f6cb3e5a75dddca5befa.png!small](https://image.3001.net/images/20200924/1600959461_5f6cb3e5a75dddca5befa.png!small)

## 二、Acunetix使用

1.浏览器中打开[https://localhost:3443](https://localhost:3443/)，输入登录信息，如下图所示：![1600959486_5f6cb3fe26690bbe13c44.png!small](https://image.3001.net/images/20200924/1600959486_5f6cb3fe26690bbe13c44.png!small)

2.登录成功以后进入主页，选择“Targets"->”Add
Target“，如下图所示：![1600959510_5f6cb416cd6aaae4322bf.png!small](https://image.3001.net/images/20200924/1600959510_5f6cb416cd6aaae4322bf.png!small)

3.在弹出的Add Target对话框中，输入要扫描的网站网址及描述，然后点击”Add
Target“,如下图所示：![1600959534_5f6cb42e676618278110d.png!small](https://image.3001.net/images/20200924/1600959534_5f6cb42e676618278110d.png!small)

4.然后点击“Scan”，如下图所示：![1600959560_5f6cb4489265d50072d86.png!small](https://image.3001.net/images/20200924/1600959560_5f6cb4489265d50072d86.png!small)

5.在打开的扫描选项对话框中，选择Scan Type、Report和Schedule，然后点击“Create
Scan”，如下图所示：![1600959576_5f6cb45815cc6b213d065.png!small](https://image.3001.net/images/20200924/1600959576_5f6cb45815cc6b213d065.png!small)

6.点击“Vulnerabilities”可以查看扫描出来的脆弱项，如下图所示：![1600959604_5f6cb474f31aeedc1d8f5.png!small](https://image.3001.net/images/20200924/1600959604_5f6cb474f31aeedc1d8f5.png!small)

7.点击“Scan”可以查看扫描的进程，如下图所示：![1600959623_5f6cb487304a9240a3b89.png!small](https://image.3001.net/images/20200924/1600959623_5f6cb487304a9240a3b89.png!small)

8.扫描完成结束后，可以点击“Reports"列表中的Download进行下载，如下图所示：![1600959641_5f6cb4999bde66a415887.png!small](https://image.3001.net/images/20200924/1600959641_5f6cb4999bde66a415887.png!small)

9.下载完成以后，就可以打开扫描过程的整个报告，如下图所示：![1600959657_5f6cb4a9c2d53bb60b065.png!small](https://image.3001.net/images/20200924/1600959657_5f6cb4a9c2d53bb60b065.png!small)

**免责声明：本人坚决反对利用教学方法进行犯罪的行为，一切犯罪行为必将受到严惩，绿色网络需要我们共同维护，更推荐大家了解它们背后的原理，更好地进行防护。禁止任何人转载到其他站点，禁止用于任何非法用途。如有任何人凭此做何非法事情，均于笔者无关，特此声明。**

