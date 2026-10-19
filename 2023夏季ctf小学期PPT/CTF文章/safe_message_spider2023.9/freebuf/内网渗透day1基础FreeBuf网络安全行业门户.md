  

### 粘滞键和放大镜

1\. 到/windows/system32下用takeown改变该文件夹下的文件拥有权（因为粘滞键和放大镜都在system32文件夹下）

[![wps24](https://image.3001.net/images/20201115/1605443114.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111104024811-574800964.jpg)

cd /Windows/system32 --跳转到/windows/system32文件夹下

takeown /F . /R /A --改变文件拥有权

/F是指定目录 .是本身

/R是递归 /A是将所有权给管理员组  
  
---  
  
  

2\. 在system32文件夹下更改全部的文件访问权限

[![wps25](https://image.3001.net/images/20201115/1605443115.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111104025715-401977662.jpg)

cacls * /T /E /G administrators:F --更改文件访问权限

/T 递归 * 所有 /E编辑ACL而不替换

/G指定指定用户的访问权限 RWCF R是读 W是写 C是更改 F是完全控制

/C在出现错误访问的时候继续  
  
---  
  
  

3\. 有了对文件的访问权限后将cmd.exe覆盖sethc.exe（粘滞键）

[![wps26](https://image.3001.net/images/20201115/1605443116.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111104026226-2085907479.jpg)

4\. 这时候可以看到sethc.exe已经不是粘滞键的图标了

[![wps27](https://image.3001.net/images/20201115/1605443463.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111104026898-1641117562.jpg)

5\. 双击后打开了cmd

[![wps28](https://image.3001.net/images/20201115/1605443117.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111104027616-2046767778.jpg)

6\. 在登录界面的时候连按5次shift调用粘滞键（这时候已经是cmd了）

[![wps29](https://image.3001.net/images/20201115/1605443117.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111104028401-72875537.jpg)

7\. 同理覆盖放大镜的exe文件

[![wps30](https://image.3001.net/images/20201115/1605443118.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111104029024-1531109838.jpg)

8\. 在登录界面调用放大镜

[![wps31](https://image.3001.net/images/20201115/1605444414.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111104029757-409540050.jpg)

  

###  **注册表创建** **自启动**

1\. 准备一个脚本文件

[![wps32](https://image.3001.net/images/20201115/1605443119.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111104030537-1205463347.jpg)

2\. 打开注册表

[![wps33](https://image.3001.net/images/20201115/1605443120.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111104031288-909132450.jpg)

[![wps34](https://image.3001.net/images/20201115/1605443121.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111104032052-2127074724.jpg)

3\.
到\HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run为当前用户的启动项。用户登录，也就是说只要有登录操作就会执行，注销然后登录，也会执行这个键值。

4\. 新建启动项为字符串值

[![wps36](https://image.3001.net/images/20201115/1605444414.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111104033868-357608659.jpg)

5\. 编辑名称和数值（数值为脚本所在的位置）

[![wps37](https://image.3001.net/images/20201115/1605443122.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111104034588-844967514.jpg)

  

6\. 重启电脑（显示为启动脚本的状态）

[![wps39](https://image.3001.net/images/20201115/1605443124.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111104036020-583454825.jpg)

命令操作

[![wps40](https://image.3001.net/images/20201115/1605443125.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111104036788-976578007.jpg)

/v 命名

/d 要启动东西的位置

/f 覆盖

######
[![wps41](https://image.3001.net/images/20201115/1605443126.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111104037413-1281446925.jpg)

[![wps42](https://image.3001.net/images/20201115/1605443127.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111104038102-1830098094.jpg)

  

### 用户克隆

1\. 到注册表的HKEY_LOCAL_MACHINE\SAM\SAM\Domains\Account\Users中

[![wps43](https://image.3001.net/images/20201115/1605443127.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111104039068-1798686895.jpg)

2\. 将哦用户ZJW（3E8）的F值复制

[![wps44](https://image.3001.net/images/20201115/1605443128.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111104039804-832783852.jpg)

3\. 到test（3f3）用户将复制的F值覆盖

[![wps45](https://image.3001.net/images/20201115/1605444415.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111104040578-1748346673.jpg)

4\. 这时候test就跟ZJW用户一样了

[![wps46](https://image.3001.net/images/20201115/1605443129.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111104041335-1284553383.jpg)

