**sqlmap是一款人见人爱的自动化SQL渗透工具，能够以良好的引擎发现给定URL中的可注入处，并自动化的完成注入。但是由于SQL注入的影响过于广泛，致使现代程序的防护越来越严密。sqlmap/tamper是官方给出的一些绕过脚本，可以配合渗透测试人员完成更高效更高质量的测试。**  

本文共分为三个部分，第一部分简要对tamper进行介绍，以及为何要使用它，如何使用；第二部分给出当前最新版本（1.2.7-26）的官方sqlmap提供的tamper脚本，第三部分以数据库为区分，给出相应数据库可使用的tamper脚本，以便使用。

## Part 1

【为什么】WAF，Web Application
Firewall，即网站应用级入侵防御系统，通过执行一系列针对HTTP/HTTPS的安全策略来专门为Web应用提供保护，有很强的输入验证功能，通过一定的判断机制检测输入的内容是否含有非法攻击语句。

为了绕过输入验证，达到预期的SQL注入目标，须对原本SQL语句进行同义改写，这种改写在很多情况下是莫名其妙的，但就是这莫名其妙的语句可以通过严密的WAF防守，达到数据库层面。更为神奇的是，数据库可以执行这段看似奇怪的SQL语句，实现预期的攻击。

【怎么做】当原始注入遇到困难时，可尝试加载相应脚本，进行绕过，说不定会有意外惊喜。在sqlmap的原命令中加入以下代码，即可使用脚本，进行更加强有力的渗透。

    
    
    --tamper“脚本名称”

## Part 2

sqlmap版本当前为1.2.7.20，共有57个tamper脚本，与1.0版本相比新增了19个脚本。

序号 | 脚本名称 | 注释  
---|---|---  
1 | 0x2char | 将每个编码后的字符转换为等价表达  
2 | apostrophemask | 单引号替换为Utf8字符  
3 | apostrophenullencode | 替换双引号为%00%27  
4 | appendnullbyte | 有效代码后添加%00  
5 | base64encode | 使用base64编码  
6 | between | 比较符替换为between  
7 | bluecoat | 空格替换为随机空白字符，等号替换为like  
8 | chardoubleencode | 双url编码  
9 | charencode | 将url编码  
10 | charunicodeencode | 使用unicode编码  
11 | charunicodeescape | 以指定的payload反向编码未编码的字符  
12 | commalesslimit | 改变limit语句的写法  
13 | commalessmid | 改变mid语句的写法  
14 | commentbeforeparentheses | 在括号前加内联注释  
15 | concat2concatws | 替换CONCAT为CONCAT_WS  
16 | equaltolike | 等号替换为like  
17 | escapequotes | 双引号替换为\\\\\\\  
18 | greatest | 大于号替换为greatest  
19 | halfversionedmorekeywords | 在每个关键字前加注释  
20 | htmlencode | html编码所有非字母和数字的字符  
21 | ifnull2casewhenisnull | 改变ifnull语句的写法  
22 | ifnull2ifisnull | 替换ifnull为if(isnull(A))  
23 | informationschemacomment | 标示符后添加注释  
24 | least | 替换大于号为least  
25 | lowercase | 全部替换为小写值  
26 | modsecurityversioned | 空格替换为查询版本的注释  
27 | modsecurityzeroversioned | 添加完整的查询版本的注释  
28 | multiplespaces | 添加多个空格  
29 | nonrecursivereplacement | 替换预定义的关键字  
30 | overlongutf8 | 将所有字符转义为utf8  
31 | overlongutf8more | 以指定的payload转换所有字符  
32 | percentage | 每个字符前添加%  
33 | plus2concat | 将加号替换为concat函数  
34 | plus2fnconcat | 将加号替换为ODBC函数{fn CONCAT()}  
35 | randomcase | 字符大小写随机替换  
36 | randomcomments | /**/分割关键字  
37 | securesphere | 添加某字符串  
38 | sp_password | 追加sp_password字符串  
39 | space2comment | 空格替换为/**/  
40 | space2dash | 空格替换为--加随机字符  
41 | space2hash | 空格替换为#加随机字符  
42 | space2morecomment | 空格替换为/**_**/  
43 | space2morehash | 空格替换为#加随机字符及换行符  
44 | space2mssqlblank | 空格替换为其他空符号  
45 | space2mssqlhash | 空格替换为%23%0A  
46 | space2mysqlblank | 空格替换为其他空白符号  
47 | space2mysqldash | 空格替换为--%0A  
48 | space2plus | 空格替换为加号  
49 | space2randomblank | 空格替换为备选字符集中的随机字符  
50 | symboliclogical | AND和OR替换为&&和||  
51 | unionalltounion | union all select替换为union select  
52 | unmagicquotes | 宽字符绕过GPC  
53 | uppercase | 全部替换为大写值  
54 | varnish | 添加HTTP头  
55 | versionedkeywords | 用注释封装每个非函数的关键字  
56 | versionedmorekeywords | 使用注释绕过  
57 | xforwardedfor | 添加伪造的HTTP头  
  
## Part 3

下面以数据库为区分，给出每种数据库可供选择的tamper。若同一脚本适用不同数据库，则在每个数据库中都指出。

###  **【MySQL】**

版本 | 可用tamper编号 | 脚本名称  
---|---|---  
4/5.0/5.5 | 1 | 0x2char  
6 | between  
9 | charencode  
16 | concat2concatws  
18 | greatest  
24 | least  
25 | lowercase  
35 | randomcase  
39 | space2comment  
49 | space2randomblank  
53 | uppercase  
5.1 | 7 | bluecoat  
46 | space2mysqlblank  
5.0/5.5 | 12 | commalesslimit  
13 | commalessmid  
21 | ifnull2casewhenisnull  
22 | ifnull2ifisnull  
42 | space2morecomment  
5.0 | 15 | concat2concatws  
26 | modsecurityversioned  
27 | modsecurityzeroversioned  
4.0/5.0 | 41 | space2hash  
5.1.56 | 10 | charunicodeencode  
5.1.56/5.5.11 | 32 | percentage  
56 | versionedmorekeywords  
4.0.18/5.0.22 | 19 | halfversionedmorekeywords  
4.0.18/5.1.56/5.5.11 | 55 | versionedkeywords  
5.1.41 | 43 | space2morehash  
未指定版本 | 14 | commentbeforeparentheses  
40 | space2dash  
45 | space2mssqlhash  
47 | space2mysqldash  
  
### 【SQLServer】

版本 | 可用tamper编号 | 脚本名称  
---|---|---  
2005/2000 | 10 | charunicodeencode  
32 | percentage  
44 | space2mssqlblank  
2005 | 6 | between  
9 | charencode  
16 | equaltolike  
25 | lowercase  
35 | randomcase  
39 | space2comment  
49 | space2randomblank  
53 | uppercase  
2002+ | 33 | plus2concat  
2008+ | 34 | plus2fnconcat  
未指定 | 14 | commentbeforeparentheses  
  
【Access】

版本 | 可用tamper编号 | 脚本名称  
---|---|---  
未指定 | 4 | appendnullbyte  
  
【Oracle】

版本 | 可用tamper编号 | 脚本名称  
---|---|---  
10g | 6 | between  
9 | charencode  
14 | commentbeforeparentheses  
18 | greatest  
24 | least  
25 | lowercase  
35 | randomcase  
39 | space2comment  
49 | space2randomblank  
53 | uppercase  
  
【PostgreSQL】

版本 | 可用tamper编号 | 脚本名称  
---|---|---  
8.3/8.4/9.0 | 6 | between  
9 | charencode  
18 | greatest  
24 | least  
25 | lowercase  
39 | space2comment  
49 | space2randomblank  
53 | uppercase  
9.0 | 32 | percentage  
9.0.3 | 10 | charunicodeencode  
未指定 | 14 | commentbeforeparentheses  
35 | randomcase  
  
【MSSQL】

版本 | 可用tamper编号 | 脚本名称  
---|---|---  
未指定 | 38 | sp_password  
  
【SQLite】

版本 | 可用tamper编号 | 脚本名称  
---|---|---  
未指定 | 40 | space2dash  
  
【未知适用范围】

若以上脚本未解决问题，可尝试使用一下脚本。

版本 | 可用tamper编号 | 脚本名称  
---|---|---  
| 2 | apostrophemask  
3 | apostrophenullencode  
5 | base64encode  
8 | chardoubleencode  
11 | charunicodeescape  
17 | escapequotes  
20 | htmlencode  
23 | informationschemacomment  
28 | multiplespaces  
29 | nonrecursivereplacement  
30 | overlongutf8  
31 | overlongutf8more  
36 | randomcomments  
37 | securesphere  
48 | space2plus  
50 | symboliclogical  
51 | unionalltounion  
52 | unmagicquotes  
54 | varnish  
57 | xforwardedfor  
  
欢迎收藏，评论，纠正，分享请注明来源。真诚期待各位大佬勘误。

 ***文章作者xiaohong0，转载请注明来自FreeBuf.COM**

