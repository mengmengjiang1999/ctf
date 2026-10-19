## 自定义修改模块

opencanary 是一个pyhton开发的开源的蜜罐系统。

github地址在:
<https://github.com/thinkst/opencanary>。完成了常用的蜜罐捕获请求。但是，固有的opencanary 存在如下的问题：

> 只监听一个IP
>
> 日志存储到本地，无法外发
>
> iptables 产生的数据存储到固定文件，无法进一步处理。
>
> 部署节点状态无法统一管理

针对以上的问题，对opencanry 完成了相关的自定义化操作。接下来挨个详述各个问题的解决办法。

## 监听多个IP

通过网卡的trunk 技术在本机上配置相应的子接口，可以让一个服务器包含多个不同网段的IP。一个支持trunk的网卡配置如下:

    
    
    VLAN=yes
    TYPE=vlan
    DEVICE=eth0.1001
    PHYSDEV=eth0
    VLAN_ID=1001
    REORDED_HDR=0
    BOOTPROTO=static
    NAME=eth0.1001
    ONBOOT=yes
    IPADDR=10.211.1.10
    NETMASK=255.255.255.0

这样，同一台服务器就监听了多个IP地址。

通过opencanaryd --copyconfig 生成的配置文件中，修改 device.listen_addr 对应的配置项为 0.0.0.0
既可以完成所有地址的监听。

## 自定义日志处理器，外发报警日志

默认的日志处理文件在 opencanry/logger.py 中定义, 默认使用的 PyLogger 类的实现，我们只需要修改 该类的 log 方法即可,
修改逻辑如下:

    
    
    def post2server(self, serverip, jsondata):
            try:
                    import urllib2
                    url = 'http://'+serverip+'/log/'
                    req  = urllib2.Request(url, jsondata, {'Content-Type':'application/json'})
                    f = urllib2.urlopen(req)
                    response = f.read()
                    self.logger.warn(response)
                    f.close()       
            except urllib2.URLError, e:
                    self.logger.error(e)
    
        def log(self, logdata, retry=True):
            logdata = self.sanitizeLog(logdata)
            jsondata = json.dumps(logdata, sort_keys=True)
           serverip = "10.210.245.22" # 日志服务器的地址 
            if logdata['src_host']!='127.0.0.1' and logdata['dst_host']!='':
                import uuid
                scheduler = TwistedScheduler()
                scheduler.add_job(self.post2server, args=[serverip, jsondata], id=str(uuid.uuid1()))
                scheduler.start()
            elif logdata['src_host']!='127.0.0.1':
                self.logger.warn(jsondata)

## iptables 日志二次处理

默认的 iptables 产生的日志，通过rsyslog 存储在 /var/log/kern.log 中，通过FileSystemWatcher
完成相应的处理。某些环境下，FileSystemWatcher 依赖于 系统的 fsnotify 模块 偶尔不能正常工作。

通过配置rsylsog 的 转发配置，转发到本地监听的syslog 服务，完成iptables 日志的二次处理。

配置如下：

50i kern.* @127.0.0.1:7788

然后，本地在 7788 端口启动一个 syslog 服务完成相应的处理即可。

    
    
    canaryLogger = logging.getLogger()
    
    LOG_HOST = "127.0.0.1"
    LOG_PORT = 7788
    
    
    class SyslogHandler(SocketServer.BaseRequestHandler):
    
        def handle(self):
            addr = self.client_address
            data = self.request[0]
            self.handleLine(data)
    
        def handleLine(self, line):
            global canaryLogger
            self.logger = canaryLogger
            try:
                if 'canaryfw: ' in line:
                    logtype = self.logger.LOG_PORT_SYN
                    (rubbish, log) = line.split('canaryfw: ')
                elif "canarynmapNULL" in line:
                    logtype = self.logger.LOG_PORT_NMAPNULL
                    (rubbish, log) = line.split('canarynmapNULL: ')
                elif "canarynmapXMAS" in line:
                    logtype = self.logger.LOG_PORT_NMAPXMAS
                    (rubbish, log) = line.split('canarynmapXMAS: ')
                elif "canarynmapFIN" in line:
                    logtype = self.logger.LOG_PORT_NMAPFIN
                    (rubbish, log) = line.split('canarynmapFIN: ')
                elif 'canarynmap: ' in line:
                    logtype = self.logger.LOG_PORT_NMAPOS
                    (rubbish, log) = line.split('canarynmap: ')
            except ValueError:
                return
            tags = log.split(' ')
            kv = {}
            for tag in tags:
                if tag.find('=') >= 0:
                    (key, val) = tag.split('=')
                else:
                    key = tag
                    val = ''
                kv[key] = val
    
            try:
                kv.pop('')
            except:
                pass
    
            data = {}
            data['src_host'] = kv.pop('SRC')
            data['src_port'] = kv.pop('SPT')
            data['dst_host'] = kv.pop('DST')
            data['dst_port'] = kv.pop('DPT')
            data['logtype'] = logtype
            data['logdata'] = kv
    
            canaryLogger.log(data)
    
    
    class LogCollect:
    
        def start(self, logger):
            global canaryLogger
            canaryLogger = logger
            logging.basicConfig(
                level=logging.DEBUG, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s', datefmt='%a, %d %b %Y %H:%M:%S')
            try:
                logging.debug("slog start at %s : %d ", LOG_HOST, LOG_PORT)
                server = SocketServer.ThreadingUDPServer(
                    (LOG_HOST, LOG_PORT), SyslogHandler)
                server.allow_reuse_address = True
                #server.request_queue_size = 60
                server.serve_forever(poll_interval=0.5)
            except Exception as ex:
                logging.debug("error start , exit .....")
            except KeyboardInterrupt:
                print ("Crtl+C Pressed. Shutting down.")

## 添加自定义模块收集服务器信息，发送到中心服务器

    
    
    # coding=utf-8
    # /usr/lib/python2.7/site-packages/opencanary/modules/host.py
    
    from opencanary.modules import CanaryService
    from twisted.internet import reactor
    
    from datetime import datetime
    from apscheduler.schedulers.twisted import TwistedScheduler
    import psutil
    import os
    import json
    
    
    class CanaryHost(CanaryService):
        NAME = "host"
    
        def __init__(self, config=None, logger=None):
            CanaryService.__init__(self, config, logger)
    
            self.hostname = config.getVal('device.node_id')
            self.localip = config.getVal('device.listen_addr')
            self.serverip = config.getVal('server.ip')
            self.last_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            self.status = "online"
            self.logtype = logger.LOG_HOST
    
        def hoststatus(self):
            hostjson = json.dumps({
                "lasttime": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                "hostname": self.hostname,
                "ip": self.localip,
                "status": self.status,
                "bindIp": self.bindIp()
            })
            try:
                import urllib2
                url = 'http://' + self.serverip + '/host/'
                req = urllib2.Request(
                    url, hostjson, {'Content-Type': 'application/json'})
                f = urllib2.urlopen(req)
                response = f.read()
                f.close()
            except urllib2.URLError, e:
                e = {"Hoststatus urllib2 Error:": str(e)}
                self.logger.error(e)
    
        def bindIp(self):
            netcard_info = []
            info = psutil.net_if_addrs()
            for k, v in info.items():
                for item in v:
                    if item[0] == 2 and item[1] != '127.0.0.1':
                        netcard_info.append({
                            "name": str(k),
                            "ip": str(item[1])
                        })
    
            return json.dumps(netcard_info)
    
        def startYourEngines(self):
            sched = TwistedScheduler()
            sched.start()
            if not sched.get_job('host_status'):
                sched.add_job(self.hoststatus, 'interval',
                              seconds=10, id='host_status')
    
    
    CanaryServiceFactory = CanaryHost
    

