## php序列化数据格式

参考：https://www.neatstudio.com/show-161-1.shtml

  * NULL，boolean ，integer，double

    
    
    N;
    b:<digit>;
    i:<number>;
    d:<number>;
    

true时digit=1，false时digit=0

  * string

    
    
    s:<length>:"<value>";
    

length 字符串长度， **数字前可以带有正号+**

  * 数组

    
    
    a:<n>:{<key 1><value 1><key 2><value 2>...<key n><value n>}
    

n 数组个数，key1、key2……数组下标，

【示例】

    
    
    <?php
      $arr = array('a'，'b'，'c');
      $sarr = serialize($arr);
      print_r($sarr);
    

输出结果

    
    
    a:3:{i:0;s:1:"a";i:1;s:1:"b";i:2;s:1:"c";}
    

  * 对象

    
    
    O:<length>:"<class name>":<n>:{<field name 1><field value 1><field name 2><field value 2>...<field name n><field value n>}
    

length表示class name的长度，n表示对象中的字段个数，这些字段包括在对象所在类及其祖先类中用 var、public、protected 和
private 声明的字段，但是不包括 static 和 const 声明的静态字段

【示例】

    
    
    O:6:"people":2:{s:4:"name";s:2:"xy";s:3:"age";s:2:"18";}
    对象类型:长度:"名字":类中变量的个数:{类型:长度:"名字";类型:长度:"值";......}
    

【类型字母详解】

    
    
    a - array                  b - boolean  
    d - double                 i - integer
    o - common object          r - reference
    s - string                 C - custom object
    O - class                  N - null
    R - pointer reference      U - unicode string
    

## 规则研究

如下示例：

    
    
    $a[] = 'jelly'
    $b = serialize($a);//	a:1:{i:0;s:5:"jelly";}
    

如果我在$a中拼接了`jelly"};`，此时为，反序列化字符串为：`a:1:{i:0;s:8:"jelly";}";}`，注入的`";}`似乎不影响其结果，会不会是`s:8`部分其主要的控制作用呢

现在来处理几种情况，然后查看反序列化的结果

    
    
    a:1:{i:0;s:5:"jelly";}123				//	a[] = 'jelly'
    a:1:{i:0;s:5:"jelly";}";}123			//	a[] = 'jelly'
    a:1:{i:0;s:8:"jelly";}";}123			//	a[] = 'jelly";}'
    

测试发现，`s:<n>`在n个字符结束后，必须以`;}`结尾，其中的`";}`符号并不会影响其反序列化。确定结尾后，后面再多字符也不会影响反序列化结果，记住这个规则，后面我们将会巧妙利用这个规则

## 字符逃逸

假设存在一下代码，$username可控，$password被写死保证密码不能修改，其组成的数组数据被序列化，然后过滤。最后反序列过滤后的字符串，利用其数据。

    
    
    function filter($string){
        $a = str_replace('x','zz',$string);
        return $a;
    }
    $username = "jelly";
    $password = "strong";
    $user = array($username, $password);
    $r = filter(serialize($user));			
    var_dump(unserialize($r));
    

示例数据的序列化如下

    
    
    a:2:{i:0;s:5:"jelly";i:1;s:6:"strong";}
    

这里只有username可控，如果在username中注入`jelly";i:1;s:6:"123456";}`，试图修改其密码，最后序列化字符串会如下

    
    
    //	$username = jelly";i:1;s:6:"123456";}
    a:2:{i:0;s:25:"jelly";i:1;s:6:"123456";}";i:1;s:6:"123456";}
    

这里我们额外注入了`";i:1;s:6:"123456";}`20个字符，其中具有`";}`试图闭合其中的一些符号，但 **s:25**
会使我们注入的`";}`毫无效果

恰好这里的过滤规则具有一个添加字符的效果，这里我们额外注入了`";i:1;s:6:"123456";}`20个字符，那我们注入20个'x'，经过'x'->'zz'的过滤，会多20个字符出来，使得我们注入的20个payload字符逃出
**s:25** 的范围。所以这种手动一般叫做字符逃逸

如果我先把$password改成123456，就可以注入以下语句

    
    
    a:2:{i:0;s:45:"jellyxxxxxxxxxx";i:1;s:6:"123456";}";i:1;s:6:"strong";}
    //  filter() 过滤后 x->zz
    a:2:{i:0;s:45:"jellyzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz";i:1;s:6:"123456";}";i:1;s:6:"123456";}
    

另外如果过滤规则是 xx->z，即可以减少字符串，也可以减少到第一个值吞掉第二个值，然后注入

参考：

PHP字符逃逸导致的对象注入：https://blog.csdn.net/dengyu810/article/details/103213750

