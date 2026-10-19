上一期跟大家介绍了Nmap中NSE脚本和常见的NSE的API，本期将为大家介绍Nmap的库文件以及如何利用Nmap的自身库将nmap的扫描结果保存在数据中。

## 0x01 NSE 中的库文件

NSE中的库文件实现了代码的分离和重构，有助于脚本的开发。斗哥的所用的Nmap库文件数目前有128个，存放在`/nselib/`文件夹中。

## 0x02 NSE库文件的编写

 **1\. 创建一个测试库文件**

NSE的库文件就是一个lua文件。要编写一个库文件，如我们在`/nselib/`文件夹中新建一个名为`testlib.lua`的文件，该库文件返回参数port是开启的。

![文库.png](https://image.3001.net/images/20180314/15210095282066.png!small)  

在新建的文件中，创建一个测试方法`Porttest()`：

    
    
    function Porttest(port)
        return string.format("The port '%s' is open",port)
    end
    

**2\. 在NSE脚本中引用测试库**

在`scripts`文件中新建一个测试脚本，`testlib.nse`文件，，如果端口开启则把端口传入`Porttest()`方法中。

    
    
    local shortport = require "shortport"
    local testlib = require "testlib"
    
    description = [[引用库文件测试]]
    
    author = "reborn"
    license = "Same as Nmap--See http://nmap.org/book/man-legal.html"
    categories = {"default"}
    
    portrule = function( host, port )
        return true
    end
    
    action = function(host,port)
        return Porttest(port.number)
    end
    

可以看到，引用库文件使用`local`，格式一般为：`local 库文件名 = require
"库文件名"`，引用完毕即可直接使用库里面的方法和属性值了。Nmap 命令：`nmap -Pn 10.10.10.39 --script
testlib`，如果需要脚本或者库需要调试，可以加上`-d`参数进入调试模式。

![模式.png](https://image.3001.net/images/20180314/15210095658575.png!small)  

## 0x03 利用自有库和自定义库实现MySql写库

 **1\. 需要用到的库**

  * `mysql`：用来进行数据库操作。
  * `nmap`：通过nmap建立socket连接mysql。
  * `shortport`：基本的port规则库。
  * `serializelib`：自定义库，将table数据转成字符串。

 **2\. 自定义库serializelib**
这个库是自己写的将table数据转成字符串，便于将`host.os`、`port.version`等数据转成字符串写到数据库中。该库下载地址：<https://gitee.com/RE13ORN/my_nmap/blob/master/serializelib.lua>

 **3\. 创建数据库和存放结果的表** 需要在你的MySql中建一个名为nmap的数据库，然后建立表和字段：

    
    
    CREATE TABLE IF NOT EXISTS nmap.scanData (date varchar(40),hostos varchar(200),hostname varchar(100), ip varchar(16), port integer(5), protocol varchar(3), state varchar(20), service varchar(100), version varchar(100));
    

  

![字段.png](https://image.3001.net/images/20180314/15210096034411.png!small)  

**4\. 连接MySQL的NSE脚本** 注意，我们使用的是socket来连接mysql，而不是使用lua的第三方库，这将使得我们的脚本更具通用性。

 **建立socket**

    
    
    local socket = nmap.new_socket()
    

**创建一个登录mysql的方法mysqlLogin**

    
    
    local function mysqlLogin(socket, username, password)
          local status, response = mysql.receiveGreeting( socket )
          if ( not(status) ) then
            return response
          end
          return mysql.loginRequest( socket, { authversion = "post41", charset = response.charset }, username, password, response.salt )
    end
    

`mysqlLogin`引用了mysql库的`receiveGreeting()`连接socket和`loginRequest`登录的方法。

`mysql.sqlQuery( socket, sql )`进行数据库查询。

注意：使用`sqlQuery`执行`SELECT`操作正常，但是执行`INSERT`操作时，虽然也能正常写数据到数据库，但是有一个警告异常`decodeDataPackets`无接收到参数。

查找官网手册对mysql库的说明，[https://nmap.org/nsedoc/lib/mysql.html，下面是官方对`sqlQuery`的介绍：](https://nmap.org/nsedoc/lib/mysql.html%EF%BC%8C%E4%B8%8B%E9%9D%A2%E6%98%AF%E5%AE%98%E6%96%B9%E5%AF%B9%60sqlQuery%60%E7%9A%84%E4%BB%8B%E7%BB%8D%EF%BC%9A)

    
    
    sqlQuery (socket, query)
    Sends the query to the MySQL server and then attempts to decode the response
    
    Parameters
        socket: socket already connected to mysql
        query: string containing the sql query
    Return values:
        status true on success, false on failure
        rows table containing row tables as decoded by decodeDataPackets
    

可以发现，`sqlQuery`必须要有返回值，因为其返回值会经过`decodeDataPackets`方法处理。而`SELECT`是有返回值的而`INSERT`无返回值故会报错。

解决的办法也很简单，在`INSERT`语句后添加一个`SELECT 1`语句使其有返回值即可。

完整代码：

    
    
    local mysql = require "mysql"
    local serializelib=require "serializelib"
    local nmap = require "nmap"
    local shortport = require "shortport"
    
    local function mysqlLogin(socket, username, password)
          local status, response = mysql.receiveGreeting( socket )
          if ( not(status) ) then
            return response
          end
          return mysql.loginRequest( socket, { authversion = "post41", charset = response.charset }, username, password, response.salt )
    end
    
    description = [[test api]]
    
    author = "reborn"
    license = "Same as Nmap--See http://nmap.org/book/man-legal.html"
    categories = {"default"}
    
    portrule = function () return true end
    
    function portaction (host,port)
        local host_local="127.0.0.1"
        local port_local="3306"
        local username="root"
        local password="root"
        local hostos_str=serialize(host.os)
        local version = serialize(port.version)
    
        if (port.version.product~=nil) then
            version = port.version.product
        end
        if (port.version.version~=nil) then
            version = version .. port.version.version
        end
    
        local date=os.date("%Y-%m-%d %H:%M:%S")
        local sql = string.format("INSERT INTO nmap.scanData (date,hostos,hostname,ip, port,protocol,state,service,version) VALUES ('%s','%s','%s', '%s', %d, '%s', '%s', '%s', '%s');select 1",date,hostos_str,host.name,host.ip, port.number,port.protocol,port.state,port.service,version)
    
        local socket = nmap.new_socket()
    
        if ( not(socket:connect(host_local, port_local)) ) then
            return fail("Failed to connect to server")
           end
        local status, response = mysqlLogin(socket, username, password)
        if ( status ) then
             local status, rs = mysql.sqlQuery( socket, sql )
            socket:close()
        else
             socket:close()
        end
    end
    local ActionsTable = {
      portrule = portaction
    }
    -- execute the action function corresponding to the current rule
    action = function(...) return ActionsTable[SCRIPT_TYPE](...) end
    

**Nmap语句：** `nmap -O 10.10.10.39 --script mysql-store`

`![语句.png](https://image.3001.net/images/20180314/15210096548708.png!small)  
`

## 0x04 小结

本期关于nmap库文件编写和mysql数据库存储就到这里了，更多库的使用和脚本应用可以查看官网手册去扩展或者自定义。另外，之前看到有人写数据库使用的是lua的第三方库，这种方式很繁琐且第三方库需要独立下载使用，建议还是使用“socket+自有库mysql”这种解决方案要好得多。

 **下期预告**

  * NSE漏洞审计和渗透脚本的demo
  * NSE的并发处理
  * ![qrcode_for_gh_223e082fe8a7_344.jpg](https://image.3001.net/images/20180314/15210096744534.jpg!small)  

