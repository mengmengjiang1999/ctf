**最近搭建各种蜜罐测试，这篇文章主要分享 HFish V0.4 使用过程中的一些心得。**

## 部署

### 单节点部署

单点部署官方文档介绍已经很全面了，不过windows 家庭中文版docker部署有点坑需要注意的。

![systeminfo](https://image.3001.net/images/20191120/1574231804_5dd4defc45a37.png!small)

家庭版不能直接安装docker，需要安装docker tool box ，原理是开启vm vbox
的linux虚拟机，然后在linux虚拟机里面安装docker，所以，在启用docker容器的时候，如果指定 -p 127.0.0.1:22:22
物理机是无法访问蜜罐，只能把容器的端口映射到0.0.0.0的地址上，物理机才可以访问。

eg:

    
    
    docker run -d -p 2222:22 -p 23:23 -p 9001:9001 -e USERNAME=god -e PASSWORD=123456 --name hfish imdevops/hfish:latest
    

![win
docker](https://image.3001.net/images/20191120/1574231829_5dd4df155525e.bmp!small)

然后进入linux虚拟机里面，查看虚拟机具体的ip地址

![linux
ifconfig](https://image.3001.net/images/20191120/1574231846_5dd4df2675f2d.bmp!small)

成功访问

![win
master](https://image.3001.net/images/20191120/1574231867_5dd4df3b59c2f.bmp!small)

### 分布式部署

为了能尽可能全的收集全球攻击数据，这次计划采用分布式部署方式。使用vps供应商为 vultr ，IDC机房分布如下图

![IDC机房列表](https://image.3001.net/images/20191120/1574231892_5dd4df549248d.bmp!small)

列表中有9个国家，ubuntu 系统最低配置每个月5美元，每个国家一台vps deploy
也没多少钱。这边有个注意点就是，在deploy时候，可以直接添加自己的ssh key，这样后面管理vps也很方便，因为我忘了我的ssh key
的密码了，就直接用账户密码管理。vps过多，管理起来挺麻烦的，这里我使用python3 的 paramiko 自动化一键配置，主要代码如下：

初始化服务器，并安装docker.io ：

![初始化](https://image.3001.net/images/20191120/1574231909_5dd4df6566255.bmp!small)

启动 docker 容器：

![启动docker](https://image.3001.net/images/20191120/1574231925_5dd4df7531718.bmp!small)

官方分布式部署命令会少些端口，可以根据 config.ini 端口自行增删。

这边还有一些需要注意的地方，国内访问国外服务器，可能会丢包，最好是在其中一台vps上面执行初始化脚本

运行完后，查看主节点，成功接收到数据。

![主节点面板](https://image.3001.net/images/20191120/1574231944_5dd4df880d56a.bmp!small)

## 攻击数据分析

分布式蜜罐部署了几天后，接下来是对捕获的数据进行分析了，下面主要以 SSH
蜜罐攻击行为为例。各位大佬也可以从附件里下载数据库自行分析。往后如果有能力，会定期提供蜜罐捕获数据给各位。

### 攻击字典统计

先来看下数据库 hfish_info 表结构及数据：

![sqlite数据库表](https://image.3001.net/images/20191120/1574231971_5dd4dfa3d787e.png!small)

可以看到数据库用 && 替换换行符，保存在数据库中，接下来可以写个统计攻击字典脚本。以下为关键部分示例代码：

    
    
        def __init__(self):        self.hfish_db = './file/hfish.db'        self.hfish_split = '&&'        self.sql = sqlite3.connect(self.hfish_db)        #这里需要注意一下，测试时候发现，有些字符无法用utf-8解码，所以得用bytes        self.sql.text_factory = bytes
    

搜索 sqlite 数据库中所有 ssh 攻击的类型

![搜索SSH类型](https://image.3001.net/images/20191120/1574231991_5dd4dfb708339.bmp!small)

然后分割 && ，把用户名密码分割开，并输出到文本里面

![输出到文本](https://image.3001.net/images/20191120/1574232008_5dd4dfc8508d8.bmp!small)

打印一下用户名及密码频次

![打印字典频次](https://image.3001.net/images/20191120/1574232029_5dd4dfdd98298.bmp!small)

取用户名及密码出现次数top10

    
    
            # 按字典值反序排序,方法一        user = sorted(user_pwd_dic['user'].items(), key=lambda x:x[1],reverse=True)        # 按字典值反序排序,方法二        password = list(user_pwd_dic['pwd'].items())        password.sort(key=lambda x:x[1],reverse=True)
    

将结果打印

![字典频次打印](https://image.3001.net/images/20191120/1574232066_5dd4e00244468.png!small)

其实字典具有地域性，可以根据攻击字典地域性，配置下蜜罐，由于默认蜜罐账户密码均为root，不在常见外网爆破攻击字典里，所以后续很多攻击都无法捕捉。

### 字典地域性分析

接下来分析一下各个国家的蜜罐收集到的字典差异，主要代码如下：

    
    
        def RegionDic(self):        agent_sql = "select agent from hfish_info"        data = self.sql.execute(agent_sql).fetchall()        agents = []        for agent in list(set(data)):            agents.append(agent[0].decode('utf-8'))​        agents_dic = {}        for agent in agents:            agents_dic[agent] = {}            data = self.sql.execute(dic_sql_tpl.format(agent)).fetchall()            for d in data:                if d[0] in agents_dic[agent].keys():                    agents_dic[agent][d[0]] = agents_dic[agent][d[0]] + 1                else:                    agents_dic[agent][d[0]] = 1​            agents_dic[agent] = sorted(agents_dic[agent].items(), key=lambda x:x[1],reverse=True)​        for agent in agents:            print(agent)            for i in range(5):                #这里不直接用decode utf-8 是因为捕获到的一些字符无法用utf-8解码，这个在上一节连接数据库里面有提到。                print("%s\t\t%s"%(str(agents_dic[agent][i][0]).replace("b'",'').replace("'",''), agents_dic[agent][i][1]))            print()
    

得到的结果如下：

![字典地域性](https://image.3001.net/images/20191120/1574232087_5dd4e017caea9.png!small)

使用 pyecharts 生成图表，

    
    
                bar = (Bar(options.InitOpts(width='1000px', height='500px'))                   .add_xaxis(u_p_dic)                   .add_yaxis(agent, u_p_count)                   .set_global_opts(                title_opts=options.TitleOpts(title=("%s统计"%agent))                    )                   )            tab.add(bar, agent)        tab.render()
    

![字典图表](https://image.3001.net/images/20191120/1574232104_5dd4e0285a326.png!small)

这里墙裂推荐直接看 [pyecharts 官方文档](https://pyecharts.org/#/zh-cn/)，特别详细全面，不要搜CSDN里面的博客，不忍吐槽某些博文。

因为收集时间不长，且子节点和主节点通信莫名中断，此结果不具有普遍性。

这里只是简单提取攻击字典，并没有做更深入分析，各位可以通过后面附件下载，自行分析。

后面会根据字典的地域性，在部署蜜罐的时候，修改特定的标致。

## 蜜罐检测

### 基于流量识别

这里以攻击者在内网，且蜜罐是以分布式部署情况作为示例，拓扑图如下：

![内网拓扑图](https://image.3001.net/images/20191120/1574232153_5dd4e059092e2.bmp!small)

使用 tcpdump dump数据包，wireshark 打开，可以看到子节点和主节点之间的通信以明文传输，且有明显的特征

![wireshark](https://image.3001.net/images/20191120/1574232164_5dd4e064189ef.bmp!small)

使用scapy 识别主节点和子节点的地址，主要代码如下

![scapy](https://image.3001.net/images/20191120/1574232175_5dd4e06f108d7.bmp!small)

存在问题的代码在 /core/rpc/client/client.go

![report
bug](https://image.3001.net/images/20191120/1574232190_5dd4e07e17549.png!small)

在内网渗透过程中，如果能发现部署的蜜罐，可以降低被发现可能性。

### 基于高交互蜜罐返回内容识别

hfish 高交互式蜜罐是根据特征字符回显，匹配的规则有限，比如常见的读取 passwd 通常使用 cat /etc/passwd
，在SSH规则里有相应的规则

![ssh蜜罐配置](https://image.3001.net/images/20191120/1574232208_5dd4e09073528.bmp!small)

如果变形使用

    
    
    cat /etc/passwd &
    

或者

    
    
    tail /etc/passwd
    

在正常的 vps 里面也是可以正常读取到 passwd 的内容，

![变形shell](https://image.3001.net/images/20191120/1574232220_5dd4e09cb20b2.bmp!small)

![变形shell2](https://image.3001.net/images/20191120/1574232230_5dd4e0a653a64.bmp!small)

但如果在蜜罐里面，则会显示异常，未修改配置的情况下是 test .

![蜜罐回显](https://image.3001.net/images/20191120/1574232242_5dd4e0b21be9c.bmp!small)

基于字符匹配的规则，总会有遗漏的地方，可以尝试变形的命令测试是否是hfish蜜罐。

高交互式蜜罐的配置文件在相应的 /libs/蜜罐类型/ 下面，默认default 值在 /libs/蜜罐类型/default.hf 。

![蜜罐default配置](https://image.3001.net/images/20191120/1574232257_5dd4e0c1ca0b6.bmp!small)

![蜜罐default配置值](https://image.3001.net/images/20191120/1574232268_5dd4e0ccac8a4.bmp!small)

### 基于管理端口返回内容识别

这个很好理解了，如果返回包含管理页面特征字符就可以判断了，这里就直接给出 POC 了。

![HFish_http](https://image.3001.net/images/20191120/1574232284_5dd4e0dc9e10f.png!small)

### 非授权接口获取信息

问题代码在 /view/url.go 文件中

![api_code](https://image.3001.net/images/20191120/1574232305_5dd4e0f19ded7.png!small)

可以发现，这里连身份鉴别都没作，当获取到主机点ip及端口后，直接请求uri，就可以获取蜜罐捕获的信息，从而分析蜜罐位置。

验证POC：

    
    
    http://ip:port/api/v1/get/iphttp://ip:port/api/v1/get/fish_info
    

![api_bp_1](https://image.3001.net/images/20191120/1574232317_5dd4e0fd75483.png!small)

![api_bp_2](https://image.3001.net/images/20191120/1574232326_5dd4e106c8372.png!small)

## 蜜罐攻击

### 非授权攻击

查看下主节点面板查询传输的数据包，用户认证是通过后，is_login
的值就是登陆用户，也就是说我们可以直接爆破这个用户，绕过登陆，直接设置后端各种参数，比如将报警参数置为空。

![master_bp](https://image.3001.net/images/20191120/1574232341_5dd4e115acebb.bmp!small)

对应的问题源码在 /view/login/view.go 里

![问题源码](https://image.3001.net/images/20191120/1574232353_5dd4e1215a92b.bmp!small)

更新报警邮件的具体配置参数在 /view/setting/view.go 里面，禁止报警 poc 就不给出了，可自行查看对应参数。

![报警参数](https://image.3001.net/images/20191120/1574232367_5dd4e12f0f314.bmp!small)

### 存储型XSS

这个漏洞是某位不愿提供ID大佬提醒的（手动滑稽）。

因为这漏洞是后台展示的原因，所以任何一个蜜罐都可以触发这个漏洞，这里以 ssh 蜜罐演示。

使用如下payload连接

    
    
    ssh ^<script^>alert^(1234^)^<^/script^>@192.168.99.101 -p 2222
    

我使用的是window系统，需要用 ^ 转义特殊字符

![ssh_payload](https://image.3001.net/images/20191120/1574233551_5dd4e5cfed646.png!small)

提交之后，返回 上钩列表 ，点击查看详情，可以看到成功执行xss。

![xss](https://image.3001.net/images/20191120/1574233560_5dd4e5d8df3d2.png!small)

## 特性化配置

这里以攻击字典地域性特点及蜜罐检测中的交互式返回内容缺陷，特性化配置蜜罐。

### 根据地域，特性化蜜罐配置

将用户名、密码修改为统计的字典出现频率最高的值。

    
    
    # 替换密码和用户名set_user_tpl = 'sed -i "s/\\"account\\": \\"root\\"/\\"account\\": \\"{}\\"/g" %s'%ssh_conf_pathset_pwd_tpl = 'sed -i "s/\\"password\\": \\"root\\"/\\"password\\": \\"{}\\"/g" %s'%ssh_conf_path
    

### 高交互式蜜罐默认返回修改

咱们用一台Ubuntu 的vps测试一下，未知的命令返回：

![unknow](https://image.3001.net/images/20191120/1574233573_5dd4e5e53206f.png!small)

也就是说，我们可以把默认返回修改为"command not found"的话，可以稍微改善下返回结果。

    
    
    set_default_tpl = 'sed -i "s/test/: command not found/g" %s'%ssh_default_path
    

## 致谢

感谢三斤大佬解惑。

HFish 是一款非常不错的高交互式蜜罐，可扩展性好，可以帮忙点击一下 start，支持一下国产蜜罐。

> [HFish github](https://github.com/hacklcx/HFish)
>
> [HFish document](https://hfish.io/docs/)

### 附件

> [sqlite数据库](https://github.com/cyker/HFishDB/blob/master/db/hfish.7z)
>
> [HFish数据分享github](https://github.com/cyker/HFishDB)
>
> [攻击用户名字典](https://github.com/cyker/HFishDB/blob/master/user.txt)
>
> [攻击密码字典](https://github.com/cyker/HFishDB/blob/master/passw'/d.txt)
>
> [地域字典统计图表](https://github.com/cyker/HFishDB/blob/master/render.txt)

 ***本文原创作者：cyker，本文属FreeBuf原创奖励计划，未经许可禁止转载**

