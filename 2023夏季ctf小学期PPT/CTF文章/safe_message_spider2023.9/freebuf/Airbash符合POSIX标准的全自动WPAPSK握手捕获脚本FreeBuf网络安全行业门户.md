**Airbash是针对渗透测试的符合POSIX标准的全自动WPA PSK握手捕获脚本。它与Bash和Android Shell（在Kali
Linux和Cyanogenmod 10.2上测试）兼容，并使用[aircrack-ng](https://www.darknet.org.uk/2007/10/aircrack-ng-wep-and-wpa-psk-key-cracking-program/)扫描当前连接到接入点（AP）的客户端。**

 **![Airbash-Fully-Automated-WPA-PSK-Handshake-Capture-Script-640x328.png](https://image.3001.net/images/20180522/15269395276677.png!small)**

这些客户端随后会被取消当前的身份验证，以便在其尝试重新连接到AP时捕获其握手数据。使用aircrack-ng验证捕获的握手包。如果捕获到一个或多个握手包，它们将被随着捕获时间和当前GPS数据（如果配置正确）被保存到SQLite3数据库中。

捕获完成后，我们可以使用crackdefault.sh并结合数据库，针对易受攻击的路由器模型进行测试。它将搜索与实现的模块相匹配的条目，其中包括用于计算Speedport
500-700系列，Thomson/SpeedTouch和 UPC 7 digits (UPC1234567) 路由器默认密钥的算法。

## 计算默认的WPA PSK密钥

捕获新的握手包后，可以查询数据库是否存在易受攻击的路由器模型。如果应用了模块，则将计算此路由器系列的默认密钥并将其用作aircrack-ng的输入，以尝试并恢复密码。

## Airbash WPA PSK握手捕获工具使用

运行install.sh将创建数据库，准备文件夹结构并为两个脚本创建短链接，这些脚本可以移动到$PATH下的目录以便从任何位置执行。

安装后，您可能需要手动调整airba.sh中第46行的INTERFACE。该设置现在默认为wlan0（以便与Android上的bcmon兼容），但在使用时它会自动识别确定。

\- ./airba.sh启动脚本，自动扫描并攻击在数据库中找不到的目标。

\- ./crackdefault.sh尝试中断已知的默认密钥算法。

查看数据库内容，请在主目录中运行sqlite3 .db.sqlite3 "SELECT * FROM hs"。

Airbash下载：[airbash-master.zip](https://github.com/tehw0lf/airbash/archive/master.zip)

 ***参考来源：[darknet](https://www.darknet.org.uk/2018/05/airbash-fully-automated-wpa-psk-handshake-capture-script/)，FB小编 secist 编译，转载请注明来自FreeBuf.COM**  

