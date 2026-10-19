# 1 json对象的介绍

在mysql未支持json数据类型时，我们通常使用varchar、blob或text的数据类型存储json字符串，对mysql来说，用户插入的数据只是序列化后的一个普通的字符串，不会对JSON文档本身的语法合法性做检查，文档的合法性需要用户自己保证。在使用时需要先将整个json对象从数据库读取出来，在内存中完成解析及相应的计算处理，这种方式增加了数据库的网络开销并降低处理效率。

从 MySQL 5.7.8 开始，MySQL 支持RFC 7159定义的全部json 数据类型，具体的包含四种基本类型（strings, numbers,
booleans,and null）和两种结构化类型（objects and arrays）。可以有效地访问 JSON文档中的数据。与将 JSON
格式的字符串存储在字符串列中相比，该数据类型具有以下优势：

  * 自动验证存储在 JSON列中的 JSON 文档。无效的文档会产生错误。
  * 优化的存储格式。存储在列中的 JSON 文档被转换为允许快速读取文档元素的内部格式。当读取 JSON 值时，不需要从文本表示中解析该值，使服务器能够直接通过键或数组索引查找子对象或嵌套值，而无需读取文档中它们之前或之后的所有值。

# 2 json类型的存储结构

mysql为了提供对json对象的支持，提供了一套将json字符串转为结构化二进制对象的存储方式。json会被转为二进制的doc对象存储于磁盘中（在处理JSON时MySQL使用的utf8mb4字符集，utf8mb4是utf8和ascii的超集）。

doc对象包含两个部分，type和value部分。其中type占1字节，可以表示16种类型：大的和小的json object类型、大的和小的 json
array类型、literal类型（true、false、null三个值）、number类型（int6、uint16、int32、uint32、int64、uint64、double类型、utf8mb4
string类型和custom data（mysql自定义类型），具体可以参考源码json_binary.cc和json_binary.h进行学习。

下面进行简单介绍：  
type ::=  
0x00 | // small JSON object  
0x01 | // large JSON object  
0x02 | // small JSON array  
0x03 | // large JSON array  
0x04 | // literal (true/false/null)  
0x05 | // int16  
0x06 | // uint16  
0x07 | // int32  
0x08 | // uint32  
0x09 | // int64  
0x0a | // uint64  
0x0b | // double  
0x0c | // utf8mb4 string  
0x0f // custom data (any MySQL data type)

  1. value包含 object、array、literal、number、string和custom-data六种类型，与type的16种类型对应。
  2. object表示json对象类型，由6部分组成：
  3. object ::= element-count size key-entry **value-entry** key **value**  
其中:  
element-count表示对象中包含的成员（key）个数，在array类型中表示数组元素个数。  
size表示整个json对象的二进制占用空间大小。小对象用2Bytes空间表示（最大64K），大对象用4Bytes表示（最大4G）  
key-entry可以理解为一个用于指向真实key值的数组。本身用于二分查找，加速json字段的定位。  
key-entry由两个部分组成：  
key-entry ::= key-offset key-length  
其中:  
key-offset：表示key值存储的偏移量，便于快速定位key的真实值。  
key-length：表示key值的长度，用于分割不同key值的边界。长度为2Bytes，这说明，key值的长度最长不能超过64kb.

  4. value-entry与key-enter功能类似，不同之处在于，value-entry可能存储真实的value值。  
value-entry由两部分组成：  
value-entry ::= type offset-or-inlined-value  
其中：  
type表示value类型，如上文所示，支持16种基本类型，从而可以表示各种类型的嵌套。

  5. offset-or-inlined-value：有两层含义，如果value值足够小，可以存储于此，那么就存储数据本身，如果数据本身较大，则存储真实值的偏移用于快速定位。  
key 表示key值的真实值，类型为：key ::= utf8mb4-data,这里无需指定key值长度，因为key-entry中已经声明了key的存储长度。同时，在同一个json对象中，key值的长度总是一样的。

array表示json数组，array类型主要包含4部分：  
array ::= element-count size value-entry **value**

我们来使用示意图更清晰的展示它的结构：

![1690768684_64c7152ca6eb17ca34165.png!small?1690768687802](https://image.3001.net/images/20230731/1690768684_64c7152ca6eb17ca34165.png!small?1690768687802)

举例说明：

![1690768692_64c715344cb7e599dc1af.png!small?1690768695542](https://image.3001.net/images/20230731/1690768692_64c715344cb7e599dc1af.png!small?1690768695542)

![1690768698_64c7153abf98839b9ab64.png!small?1690768701860](https://image.3001.net/images/20230731/1690768698_64c7153abf98839b9ab64.png!small?1690768701860)

![1690768703_64c7153feea8d0e2a7365.png!small?1690768707070](https://image.3001.net/images/20230731/1690768703_64c7153feea8d0e2a7365.png!small?1690768707070)

![1690768720_64c71550f04245f40cdcd.png!small?1690768724221](https://image.3001.net/images/20230731/1690768720_64c71550f04245f40cdcd.png!small?1690768724221)

需要注意的是：

  * JSON对象的Key索引（图中橙色部分）都是排序好的，先按长度排序，长度相同的按照code point排序；Value索引（图中黄色部分）根据对应的Key的位置依次排列，最后面真实的数据存储（图中白色部分）也是如此
  * Key和Value的索引对存储了对象内的偏移和大小，单个索引的大小固定，可以通过简单的算术跳转到距离为N的索引
  * 通过MySQL5.7.16源代码可以看到，在序列化JSON文档时，MySQL会动态检测单个对象的大小，如果小于64KB使用两个字节的偏移量，否则使用四个字节的偏移量，以节省空间。同时，动态检查单个对象是否是大对象，会造成对大对象进行两次解析，源代码中也指出这是以后需要优化的点
  * 现在受索引中偏移量和存储大小四个字节大小的限制，单个JSON文档的大小不能超过4G；单个KEY的大小不能超过两个字节，即64K
  * 索引存储对象内的偏移是为了方便移动，如果某个键值被改动，只用修改受影响对象整体的偏移量
  * 索引的大小现在是冗余信息，因为通过相邻偏移可以简单的得到存储大小，主要是为了应对变长JSON对象值更新，如果长度变小，JSON文档整体都不用移动，只需要当前对象修改大小
  * 现在MySQL对于变长大小的值没有预留额外的空间，也就是说如果该值的长度变大，后面的存储都要受到影响
  * 结合JSON的路径表达式可以知道，JSON的搜索操作只用反序列化路径上涉及到的元素，速度非常快，实现了读操作的高性能
  * MySQL对于大型文档的变长键值的更新操作可能会变慢，可能并不适合写密集的需求

# 3 json类型基本操作

### 3.1 json数据插入

json类型数据插入时有两种方式，一种是基于字符串格式插入，另一种是基于json_object()函数，在使用json_object()函数只需按k-v顺序，以,符号隔开顺序插入即可，MYSQL会自动验证 JSON 文档，无效的文档会产生错误。

    
    
    mysql> CREATE TABLE t1 (jdoc JSON);
    Query OK, 0 rows affected (0.20 sec)
    
    mysql> INSERT INTO t1 VALUES('{"key1": "value1", "key2": "value2"}');
    Query OK, 1 row affected (0.01 sec)
    
    mysql> INSERT INTO t1 VALUES('[1, 2,');
    ERROR 3140 (22032) at line 2: Invalid JSON text:
    "Invalid value." at position 6 in value (or column)  '[1, 2,'.

当一个字符串被解析并发现是一个有效的 JSON 文档时，它也会被规范化：具有与文档中先前找到的键重复的键的成员被丢弃（即使值不同）。以下第一个sql中通过
JSON_OBJECT()调用生成的对象值不包括第二个key1元素，因为该键名出现在值的前面；第二个sql中只保留了x第一次出现的值：

    
    
    mysql> SELECT JSON_OBJECT('key1', 1, 'key2', 'abc', 'key1', 'def');
    +------------------------------------------------------+
    | JSON_OBJECT('key1', 1, 'key2', 'abc', 'key1', 'def') |
    +------------------------------------------------------+
    | {"key1": 1, "key2": "abc"}                           |
    +------------------------------------------------------+
    
    mysql> INSERT INTO t1 VALUES
         >     ('{"x": 17, "x": "red"}'),
         >     ('{"x": 17, "x": "red", "x": [3, 5, 7]}');
    
    mysql> SELECT c1 FROM t1;
    +-----------+
    | c1        |
    +-----------+
    | {"x": 17} |
    | {"x": 17} |
    +-----------+

### 3.2 json合并

MySQL 5.7支持JSON_MERGE（）的合并算法，多个对象合并时产生一个对象。  
可将多个数组合并为一个数组：

    
    
    mysql> SELECT JSON_MERGE('[1, 2]', '["a", "b"]', '[true, false]');
    +-----------------------------------------------------+
    | JSON_MERGE('[1, 2]', '["a", "b"]', '[true, false]') |
    +-----------------------------------------------------+
    | [1, 2, "a", "b", true, false]                       |
    +-----------------------------------------------------+

当合并数组与对象时，会将对象转换为新数组进行合并：

    
    
    mysql> SELECT JSON_MERGE('[10, 20]', '{"a": "x", "b": "y"}');
    +------------------------------------------------+
    | JSON_MERGE('[10, 20]', '{"a": "x", "b": "y"}') |
    +------------------------------------------------+
    | [10, 20, {"a": "x", "b": "y"}]                 |
    +------------------------------------------------+

如果多个对象具有相同的键，则生成的合并对象中该键的值是包含键值的数组

    
    
    mysql> SELECT JSON_MERGE('{"a": 1, "b": 2}', '{"c": 3, "a": 4}');
    +----------------------------------------------------+
    | JSON_MERGE('{"a": 1, "b": 2}', '{"c": 3, "a": 4}') |
    +----------------------------------------------------+
    | {"a": [1, 4], "b": 2, "c": 3}                      |
    +----------------------------------------------------+

MySQL 8.0.3（及更高版本）支持两种合并算法，由函数 JSON_MERGE_PRESERVE()和 JSON_MERGE_PATCH().
它们在处理重复键的方式上有所不同：JSON_MERGE_PRESERVE()保留重复键的值（与5.7版本的JSON_MERGE（）相同），而
JSON_MERGE_PATCH()丢弃除最后一个值之外的所有值。具体的

  * JSON_MERGE_PRESERVE() 函数接受两个或多个 JSON 文档并返回组合结果。如果参数为两个object,相同的key将会把value合并为array(即使value也相同，也会合并为array),不同的key则直接合并。如果其中一个参数为json array，则另一个json object整体作为一个元素，加入array结果。
  * JSON_MERGE_PATCH()函数接受两个或多个 JSON 文档并返回组合结果。如果参数为两个object,相同的key的value将会被后面参数的value覆盖,不同的key则直接合并。如果合并的是数组，将按照“最后一个重复键获胜”逻辑仅保留最后一个参数。

    
    
    mysql> SELECT JSON_MERGE_PRESERVE('{"a":1,"b":2}', '{"a":3,"c":3}');
    +-------------------------------------------------------+
    | JSON_MERGE_PRESERVE('{"a":1,"b":2}', '{"a":3,"c":3}') |
    +-------------------------------------------------------+
    | {"a": [1, 3], "b": 2, "c": 3}                         |
    +-------------------------------------------------------+
    1 row in set (0.01 sec)
    mysql> SELECT JSON_MERGE_PATCH('{"a":1,"b":2}', '{"a":3,"c":3}');
    +----------------------------------------------------+
    | JSON_MERGE_PATCH('{"a":1,"b":2}', '{"a":3,"c":3}') |
    +----------------------------------------------------+
    | {"a": 3, "b": 2, "c": 3}                           |
    +----------------------------------------------------+
    1 row in set (0.02 sec)
    
    mysql> SELECT JSON_MERGE_PRESERVE('["a", 1]', '"a"','{"key": "value"}');
    +-----------------------------------------------------------+
    | JSON_MERGE_PRESERVE('["a", 1]', '"a"','{"key": "value"}') |
    +-----------------------------------------------------------+
    | ["a", 1, "a", {"key": "value"}]                           |
    +-----------------------------------------------------------+
    1 row in set (0.00 sec)
    mysql> SELECT JSON_MERGE_PATCH('["a", 1]', '"a"','{"key": "value"}') ;
    +--------------------------------------------------------+
    | JSON_MERGE_PATCH('["a", 1]', '"a"','{"key": "value"}') |
    +--------------------------------------------------------+
    | {"key": "value"}                                       |
    +--------------------------------------------------------+
    1 row in set (0.01 sec)

### 3.3 json数据查询

MySQL 5.7.7+本身提供了很多原生的函数以及路径表达式来方便用户访问JSON数据。  
JSON_EXTRACT()函数用于解析json对象，->符号是就一种JSON_EXTRACT()函数的等价模式。例如查询上面t1表中
jdoc字段中key值为x的值

    
    
    SELECT jdoc->'$.x' FROM t1;
    SELECT JSON_EXTRACT(jdoc,'$.x') FROM t1;

JSON_EXTRACT返回值会带有” “,如果想获取原本的值可以使用JSON_UNQUOTE

    
    
    mysql> SELECT JSON_EXTRACT('{"id": 14, "name": "Aztalan"}', '$.name');
    +---------------------------------------------------------+
    | JSON_EXTRACT('{"id": 14, "name": "Aztalan"}', '$.name') |
    +---------------------------------------------------------+
    | "Aztalan"                                               |
    +---------------------------------------------------------+
    
    mysql> SELECT JSON_UNQUOTE(json_extract('{"id": 14, "name": "Aztalan"}', '$.name'));;
    +-----------------------------------------------------------------------+
    | JSON_UNQUOTE(json_extract('{"id": 14, "name": "Aztalan"}', '$.name')) |
    +-----------------------------------------------------------------------+
    | Aztalan                                                               |
    +-----------------------------------------------------------------------+

json路径的语法：

    
    
    pathExpression:
        scope[(pathLeg)*]
    
    pathLeg:
        member | arrayLocation | doubleAsterisk
    
    member:
        period ( keyName | asterisk )
    
    arrayLocation:
        leftBracket ( nonNegativeInteger | asterisk ) rightBracket
    
    keyName:
        ESIdentifier | doubleQuotedString
    
    doubleAsterisk:
        '**'
    
    period:
        '.'
    
    asterisk:
        '*'
    
    leftBracket:
        '['
    
    rightBracket:
        ']'

以json { “a”: [ [ 3, 2 ], [ { “c” : “d” }, 1 ] ], “b”: { “c” : 6 }, “one
potato”: 7, “b.c” : 8 } 为例：  
$.a[1] 获取的值为 [ { “c” : “d” }, 1 ]  
$.b.c 获取的值为 6  
$.”b.c” 获取的值为 8（因为键名包含不合法的表达式所以需要使用引号）

![1690768749_64c7156d895f2b27a9c60.png!small?1690768752756](https://image.3001.net/images/20230731/1690768749_64c7156d895f2b27a9c60.png!small?1690768752756)

    
    
    mysql>  select json_extract('{ "a": [ [ 3, 2 ], [ { "c" : "d" }, 1 ] ], "b": { "c" : 6 }, "one potato": 7, "b.c" : 8 }','$**.c');
    +-------------------------------------------------------------------------------------------------------------------+
    | JSON_EXTRACT('{ "a": [ [ 3, 2 ], [ { "c" : "d" }, 1 ] ], "b": { "c" : 6 }, "one potato": 7, "b.c" : 8 }','$**.c') |
    +-------------------------------------------------------------------------------------------------------------------+
    | ["d", 6]                                                                                                          |
    +-------------------------------------------------------------------------------------------------------------------+

$**.c 匹配到了两个路径 :  
$.a[1].c 获取的值是”d”  
$.b.c 获取的值为 6

### 3.4 json数据更新

一些函数采用现有的 JSON 文档，以某种方式对其进行修改，然后返回结果修改后的文档。路径表达式指示在文档中进行更改的位置。例如，JSON_SET()、
JSON_INSERT()和 JSON_REPLACE()函数各自采用现有的 JSON
文档，加上一个或多个路径和值对，来描述修改文档和要更新的值。这些函数在处理文档中现有值和不存在值的方式上有所不同。  
具体如下

    
    
    mysql> SET @j = '["a", {"b": [true, false]}, [10, 20]]';

JSON_SET()替换存在的路径的值并添加不存在的路径的值：

    
    
    mysql> SELECT JSON_SET(@j, '$[1].b[0]', 1, '$[2][2]', 2);
    +--------------------------------------------+
    | JSON_SET(@j, '$[1].b[0]', 1, '$[2][2]', 2) |
    +--------------------------------------------+
    | ["a", {"b": [1, false]}, [10, 20, 2]]      |
    +--------------------------------------------+

在这种情况下，路径$[1].b[0]选择一个现有值 ( true)，该值将替换为路径参数 ( 1) 后面的值。该路径$[2][2]不存在，因此将相应的值 (
2) 添加到 选择的值中$[2]。  
JSON_INSERT()添加新值但不替换现有值：

    
    
    mysql> SELECT JSON_INSERT(@j, '$[1].b[0]', 1, '$[2][2]', 2);
    +-----------------------------------------------+
    | JSON_INSERT(@j, '$[1].b[0]', 1, '$[2][2]', 2) |
    +-----------------------------------------------+
    | ["a", {"b": [true, false]}, [10, 20, 2]]      |
    +-----------------------------------------------+

JSON_REPLACE()替换现有值并忽略新值：

    
    
    mysql> SELECT JSON_REPLACE(@j, '$[1].b[0]', 1, '$[2][2]', 2);
    +------------------------------------------------+
    | JSON_REPLACE(@j, '$[1].b[0]', 1, '$[2][2]', 2) |
    +------------------------------------------------+
    | ["a", {"b": [1, false]}, [10, 20]]             |
    +------------------------------------------------+

JSON_REMOVE()接受一个 JSON 文档和一个或多个路径，这些路径指定要从文档中删除的值。返回值是原始文档减去文档中存在的路径选择的值：

    
    
    mysql> SELECT JSON_REMOVE(@j, '$[2]', '$[1].b[1]', '$[1].b[1]');
    +---------------------------------------------------+
    | JSON_REMOVE(@j, '$[2]', '$[1].b[1]', '$[1].b[1]') |
    +---------------------------------------------------+
    | ["a", {"b": [true]}]                              |
    +---------------------------------------------------+

$[2]匹配[10, 20] 并删除它。  
$[1].b[1]匹配 元素false中 的第一个实例b并将其删除。  
不匹配的第二个实例$[1].b[1]：该元素已被删除，路径不再存在，并且没有效果。

### 3.5 json比较与排序

JSON值可以使用=, <, <=, >, >=, <>, !=, <=>等操作符，BETWEEN, IN,GREATEST,
LEAST等操作符现在还不支持。JSON值使用的两级排序规则，第一级基于JSON的类型，类型不同的使用每个类型特有的排序规则。  
JSON类型按照优先级从高到低为

    
    
    BLOB
    BIT
    OPAQUE
    DATETIME
    TIME
    DATE
    BOOLEAN
    ARRAY
    OBJECT
    STRING
    INTEGER, DOUBLE
    NULL

优先级高的类型大，不用再进行其他的比较操作；如果类型相同，每个类型按自己的规则排序。具体的规则如下：

  * BLOB/BIT/OPAQUE: 比较两个值前N个字节，如果前N个字节相同，短的值小
  * DATETIME/TIME/DATE: 按照所表示的时间点排序
  * BOOLEAN: false小于true
  * ARRAY: 两个数组如果长度和在每个位置的值相同时相等，如果不想等，取第一个不相同元素的排序结果，空元素最小。例：[] < [“a”] < [“ab”] < [“ab”, “cd”, “ef”] < [“ab”, “ef”]
  * OBJECT: 如果两个对象有相同的KEY，并且KEY对应的VALUE也都相同，两者相等。否则，两者大小不等，但相对大小未规定。例：{“a”: 1, “b”: 2} = {“b”: 2, “a”: 1}
  * STRING: 取两个STRING较短的那个长度为N，比较两个值utf8mb4编码的前N个字节，较短的小，空值最小。例：”a” < “ab” < “b” < “bc”；此排序等同于使用 collat​​ion 对 SQL 字符串进行排序utf8mb4_bin。因为 utf8mb4_bin是二进制排序规则，所以 JSON 值的比较区分大小写：”A” < “a”
  * INTEGER/DOUBLE: 包括精确值和近似值的比较

# 4 JSON的索引

现在MySQL不支持对JSON列进行索引，官网文档的说明是：

JSON columns cannot be indexed. You can work around this restriction by
creating an index on a generated column that extracts a scalar value from the
JSON column.

虽然不支持直接在JSON列上建索引，但MySQL规定，可以首先使用路径表达式对JSON文档中的标量值建立虚拟列，然后在虚拟列上建立索引。这样用户可以使用表达式对自己感兴趣的键值建立索引。举个具体的例子来说明：

    
    
    ALTER TABLE features ADD feature_street VARCHAR(30) AS (JSON_UNQUOTE(feature->"$.properties.STREET"));
    ALTER TABLE features ADD INDEX (feature_street);

两个步骤，可以对feature列中properties键值下的STREET键(feature->”$.properties.STREET”)创建索引。

其中，feature_street列就是新添加的虚拟列。之所以取名虚拟列，是因为与它对应的还有一个存储列(stored
column)。它们最大的区别为虚拟列只修改数据库的metadata，并不会存储真实的数据在硬盘上，读取过程也是实时计算的方式；而存储列会把表达式的列存储在硬盘上。两者使用的场景不一样，默认情况下通过表达式生成的列为虚拟列。

这样虚拟列的添加和删除都会非常快，而在虚拟列上建立索引跟传统的建立索引的方式并没有区别，会提高虚拟列读取的性能，减慢整体插入的性能。虚拟列的特性结合JSON的路径表达式，可以方便的为用户提供高效的键值索引功能。

# 5 总结

  1. JSON类型无须预定义字段，适合拓展信息的存储
  2. 单个JSON文档的大小不能超过4G；单个KEY的大小不能超过两个字节，即64K
  3. JSON类型适合应用于不常更新的静态数据
  4. 对搜索较频繁的数据建议增加虚拟列并建立索引

> 作者：京东物流 王凤辉
>
> 来源：京东云开发者社区 自猿其说Tech

  

