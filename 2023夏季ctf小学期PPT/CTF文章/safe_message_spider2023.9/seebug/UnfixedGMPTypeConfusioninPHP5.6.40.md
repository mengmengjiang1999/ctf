**Authors: Alexey Moskvin, Daniil Sadyrin  
<https://github.com/CFandR-github/PHP-binary-bugs/blob/main/GMP_type_conf_unserialize/GMP_type_conf_advisory.md>**

Requirements: PHP <= 5.6.40  
Compiled with: '--with-gmp'

## Bug summary

Original GMP Type confusion bug was found by taoguangchen researcher and
reported [1]. The idea of exploit is to change zval structure [2] of GMP
object during deserialization process. In original exploit author says about
changing zval type using this code lines:

    
    
        function __wakeup()
            {
                $this->ryat = 1;
            }

PHP supports serialization/deserialization of references. It is done using
"R:" syntax. this→ryat property leads to rewrite of GMP zval. There are many
ways to rewrite zval in PHP, easies is code line like this:

    
    
    $this->a = $this->b;

Part of exploit is to find this line in code of real web-application, and
execute it during deserialization process. Bug in GMP extension was "fixed" as
part of delayed `__wakeup` patch. But source code in gmp.c file was not
patched. So bypassing delayed `__wakeup` would result that this bug is still
exploitable. Delayed `__wakeup` patch was introduced in PHP 5.6.30. Generally
it was a patch to prevent use-after-free bugs in unserialize. Exploits using
use-after-free bugs are based on removing zval’s from memory in the middle of
deserialization process and further reusing freed memory. Introduced patch
suspends execution of object’s `__wakeup` method after deserialization process
finishes. It prevents removing zval’s from memory during deserialization
process.

But there is another way to execute code in the middle of deserialization in
PHP. In PHP there exists Serializable interface [3] It is for classes that
implement custom serialization/deserialization methods. Deserialization of
these classes can not be delayed. They have special syntax in unserialize
starting with "C:". In real web-apps "unserialize" methods are small and don’t
have code lines to rewrite zval.

    
    
    public function unserialize($data) {
        unserialize($data);
    }

If data) call will not throw any fatal error. Deserialization process will
continue after unserializing custom-serialized object. This can be used to
trigger `__destruct` method using unclosed brace in serialized $data string.
Code of `__destruct` method will be executed in the middle of unserialization
process! In code of `__destruct` method there is a big chance to find code
lines that rewrite zval. The only restriction for this trick is to find a
class in web-application code that implements Serializable interface.

## POC debug

Let us run [bug POC](https://github.com/CFandR-github/PHP-binary-bugs/blob/main/GMP_type_conf_unserialize/GMP_type_conf_POC.php) and understand
how it works.

Code line to rewrite zval is located in `*obj1*` class.

![](https://images.seebug.org/content/images/2022/05/27/1653624557000-gmp_type_conf_html_de16b5bb2238a9b7.png-w331s)

Class `*obj2*` has unserialize method with another unserialize function call
in it.

![](https://images.seebug.org/content/images/2022/05/27/1653624558000-gmp_type_conf_html_d0543afac0dcd60c.png-w331s)

Set two breakpoints in gdb. First, when GMP object is created.  
gdb-peda$ b gmp.c:640

![](https://images.seebug.org/content/images/2022/05/27/1653624558000-gmp_type_conf_html_6ad048eec7b2057f.png-w331s)

Another breakpoint, where type confusion bug happens.  
gdb-peda$ b gmp.c:661

![](https://images.seebug.org/content/images/2022/05/27/1653624558000-gmp_type_conf_html_e4a58805756091b1.png-w331s)

Rub gdb, unserialization of GMP object properties starts.  
Stop on line 640 and print object zval. It is GMP object with handle = 0x2

![](https://images.seebug.org/content/images/2022/05/27/1653624558000-gmp_type_conf_html_57ecb71f480ddf12.png-w331s)

Set breakpoint on unserialize call.  
gdb-peda$ b var.c:967  
Continue execution.

Execution reaches second unserialize function call, located in unserialize
method of obj2 class.

![](https://images.seebug.org/content/images/2022/05/27/1653624558000-gmp_type_conf_html_d0543afac0dcd60c.png-w331s)

Because of invalid serialization string (it has “A” char instead of closing
bracket at the end), php_var_unserialize call returns false and
zval_dtor(return_value) is called. If the zval_dtor argument has object type,
it’s `__destruct` method executes.

![](https://images.seebug.org/content/images/2022/05/27/1653624558000-gmp_type_conf_html_2e481d6c5646c62e.png-w331s)

Output return_value using printzv macros. It is object of `*obj1*` class with
unserialized properties.

![](https://images.seebug.org/content/images/2022/05/27/1653624559000-gmp_type_conf_html_69633d182ced5abf.png-w331s)

Now destructor of obj1 class executes.

![](https://images.seebug.org/content/images/2022/05/27/1653624559000-gmp_type_conf_html_b1c9863272aabe0.png-w331s)

this->test rewrites zval of GMP object. Value to write is taken from $this→foo
and equal to `**i:1;**`

Continue execution.

![](https://images.seebug.org/content/images/2022/05/27/1653624558000-gmp_type_conf_html_e4a58805756091b1.png-w331s)

See what happened with GMP zval.

![](https://images.seebug.org/content/images/2022/05/27/1653624559000-gmp_type_conf_html_2f77c8e6b87a72bf.png-w331s)

Handle of GMP zval is equal to $this→foo, it is 0x1. See what function
zend_std_get_properties does.

![](https://images.seebug.org/content/images/2022/05/27/1653624559000-gmp_type_conf_html_8f366306486ad4f2.png-w331s)

![](https://images.seebug.org/content/images/2022/05/27/1653624559000-gmp_type_conf_html_1ef82a2ecc309fad.png-w331s)

#define Z_OBJ_HANDLE_P(zval_p) Z_OBJ_HANDLE(*zval_p)  
#define Z_OBJ_HANDLE(zval) Z_OBJVAL(zval).handle  
#define Z_OBJVAL(zval) (zval).value.obj

Z_OBJ_HANDLE_P(zval_p) returns zval_p.value.obj.handle it is an object handle
taken from zval structure. Z_OBJ_P macro takes a object handle number, and
returns property hashtable of object with the given handle number.
zend_hash_copy copies props of GMP object into this hashtable. GMP handle
number is fully controlled from exploit. Using this bug an attacker can
rewrite props of any object in PHP script. GMP handle is overwritten with 0x1.
In the POC script, `*stdClass*` object created before unserialize call has
handle = 0x1. Properties of this object are overwritten, see it in GDB.

![](https://images.seebug.org/content/images/2022/05/27/1653624559000-gmp_type_conf_html_ba791a6b19815137.png-w331s)

To write 0x1 into handle id, sometimes no need to use integer zval, attacker
can use boolean type. PHP boolean type is represented in memory as 0 or 1
integer. Code lines like $this→prop = true are more common in real code than
property assignment demonstrated previously.

Usage of this bug in the real-world CMS / frameworks demonstrated as follows.

## Vulnerability Cases:

Advisory of Exploits AI POP Builder

Collection of advisory:

### Symfony <= 3.4.47 0day GMP Type Confusion RCE

#### symfony/process

Idea: PHP <= 5.6.40 with GMP + packages symfony/process and symfony/routing +
fast "__destruct"

POC source: [./symfony_process_gmp/poc.php](https://github.com/CFandR-github/advisory/blob/main/symfony_process_gmp/poc.php)

[Advisory](https://github.com/CFandR-github/advisory/blob/main/symfony_process_gmp/symfony_0day_GMP_exploit.md)

#### symfony/dependency-injection

Idea: PHP <= 5.6.40 with GMP + packages symfony/dependency-injection and
symfony/routing + var overwrite into boolean

POC source:
[./symfony_rewrite_with_boolean/tester.php](https://github.com/CFandR-github/advisory/blob/main/symfony_rewrite_with_boolean/tester.php)

[Advisory](https://github.com/CFandR-github/advisory/blob/main/symfony_rewrite_with_boolean/rewrite_with_boolean_gmp.md)

### swiftmailer/swiftmailer <= 5.4.12 0day GMP Type Confusion RCE

Idea: PHP <= 5.6.40 with GMP + packages swiftmailer/swiftmailer and
pear/net_geoip + var pass by ref

POC source: [./swiftmailer_gmp_rce/poc.php](https://github.com/CFandR-github/advisory/blob/main/swiftmailer_gmp_rce/poc.php)

[Advisory](https://github.com/CFandR-github/advisory/blob/main/swiftmailer_gmp_rce/swiftmailer_0day_GMP_exploit.md)

### Drupal <= 8.7.14 GMP Type Confusion RCE

Idea: PHP <= 5.6.40 with GMP + Drupal CMS

POC source: [./drupal_gmp_rce/poc.php](https://github.com/CFandR-github/advisory/blob/main/drupal_gmp_rce/poc.php)

[Advisory](https://github.com/CFandR-github/advisory/blob/main/drupal_gmp_rce/drupal_gmp_unserialize_rce.md)

### phpmailer + swiftmailer 0day unserialize RCE (any PHP version)

Idea: packages phpmailer/phpmailer and swiftmailer/swiftmailer + is_resource
bypass + fast "__destruct"

POC source: [./phpmailer_rce_poi/phpmailer_poc.php](https://github.com/CFandR-github/advisory/blob/main/phpmailer_rce_poi/phpmailer_poc.php)

[Advisory](https://github.com/CFandR-github/advisory/blob/main/phpmailer_rce_poi/phpmailer_unserialize_rce_0day.md)

References:

[1] <https://bugs.php.net/bug.php?id=70513>  
[2] <https://www.phpinternalsbook.com/php5/zvals/basic_structure.html>  
[3] <https://www.php.net/manual/en/class.serializable>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1909/>

