**作者: 360漏洞研究院 李双  
原文链接：<https://vul.360.net/archives/648>**

## 背景

Foxit Reader（旧名：Foxit PDF Reader），是一套用来阅读PDF格式文件的软件，由福建福昕软件所研发。

在 Adobe Reader 以及旧版本的 Foxit Reader 中，通常会利用 JS 的 ArrayBuffer
来布局内存并最终实现任意代码执行。然而，最新版本 Foxit Reader 中的 ArrayBuffer
已经被禁用，这导致漏洞利用的难度很大，目前还未见到网上有公开的漏洞利用方案。

这篇文章主要总结我在研究 Foxit Reader 漏洞利用的过程中积累的一些经验，从 Foxit Reader
的一套内存管理机制的角度出发，探索潜在的漏洞利用方式，为大家提供一些可能的思路。

## 内存管理

Foxit Reader 中可能存在有多套内存管理机制，其在文件解析中自己实现了一个内存池堆分配器来管理内存。

每个使用 malloc 分配的 chunk 都取自一个固定 0x1000 大小的池中。每个池都会分割成若干个指定 size 的 chunk，拥有相同的
chunk size 的池之间通过指针构成双向链表。所有的双向链表的头指针都保存在一个全局数组变量中。

    
    
    +--------+
    | 0x8    |--------> +--------+        +--------+
    +--------+          | head   | <====> | head   | <====> ...
    | 0x10   |------+   +--------+        +--------+
    +--------+      |   | chunk  |        | chunk  |
    | 0x18   |----+ |   +--------+        +--------+
    +--------+    | |   | chunk  |        | chunk  |
    | ...    |    | |   +--------+        +--------+
                  | |   | ...    |        | ...    |
                  | |
                  | +-> +--------+        +--------+
                  |     | head   | <====> | head   | <====> ...
                  |     +--------+        +--------+
                  |     | chunk  |        | chunk  |
                  |     +--------+        +--------+
                  |     | chunk  |        | chunk  |
                  |     +--------+        +--------+
                  |     | ...    |        | ...    |
                  |
                  +---> +--------+        +--------+
                        | head   | <====> | head   | <====> ...
                        +--------+        +--------+
                        | chunk  |        | chunk  |
                        +--------+        +--------+
                        | chunk  |        | chunk  |
                        +--------+        +--------+
                        | ...    |        | ...    |

当通过 malloc 分配小于 0x400 size 的 chunk 时，直接从全局数组变量 `poolheadarray` 中取得对应 size
的池，然后取得它的 `nextfreechunk` 返回。若 `nextfreechunk` 不存在，则分配一个新的 chunk。

    
    
    //...
      if ( size > 0x400 )
        return sub_1D92C70(a1, size);
      idx = (size - 1) >> 3;
      pool = poolheadarray[2 * idx];
      if ( pool == pool->nextpool )
        return sub_1D92D60(a1, (size - 1) >> 3);
      v5 = pool->nextfreechunk;
      ++pool->ref;
      v6 = *v5;
      pool->nextfreechunk = *v5;
      if ( !v6 )
      {
        sub_1D93260(pool, idx);
        return v5;
      }
    //...

当通过 free 释放时，将 chunk 链接到 `nextfreechunk` 下。

    
    
      v4 = *((a2 & 0xFFFFF000) + 4);
      *a2 = v4;
      v5 = pool->ref - 1;
      *((a2 & 0xFFFFF000) + 4) = a2;
      pool->ref = v5;

### 池的结构

池总是固定为 0x1000 大小，其前 0x20 字节保存了池的相关信息:

    
    
    base +--------+---------------+----------+-----------+
         |        | nextfreechunk | prevpool | nextpool  |
         +--------+---------------+----------+-----------+
         |        | sizeidx       | offset   | maxoffset |
         +--------+---------------+----------+-----------+
         |        |               |          |           |

相关成员如下

  * `nextfreechunk` ：

所有被释放掉的空闲 chunk 构成一个单向链表，`nextfreechunk` 指向链表头。分配内存时总是从 `nextfreechunk` 首先获取。

若 `nextfreechunk` 为空，则存在两种情况：所有 chunk 已经全部分配或者还有从未分配过的 chunk。

若所有 chunk 已经全部分配则会取下一个池，然后重复上述步骤。

  * `prevpool` 和 `nextpool` ：

指向上一个池和下一个池。

  * `sizeidx` ：

当前池对应的 chunk 大小的索引，chunk 的大小 8 字节对齐。

  * `offset` 和 `maxoffset` ：

在一个池初次创建时，所有的 chunk 都是空闲状态，但是 `nextfreechunk` 并不会指向他们，只有所有已分配的 chunk 经历过 free
之后才能通过 `nextfreechunk` 进行之后的分配。而第一次的分配就需要 `offset` 和 `maxoffset` 来判断下一个应该分配的
chunk。

`offset` 指向下一个尚未分配过的 chunk，`maxoffset` 指向池的末尾。当 `offset < maxoffset`
时，说明仍有尚未进行过分配的 chunk，若此时 `nextfreechunk` 为空，则返回 `offset` 处指向的 chunk。

### free chunk 的结构

释放后的 chunk 会被插入到空闲链表中， `nextfreechunk` 将指向该 chunk，而 `nextfreechunk` 原来所指向的
chunk 将放入该 chunk 中，其结构图如下。

    
    
    +---------------+--------+--------+--------+
    | nextfreechunk |        |        |        |
    +---------------+--------+--------+--------+
    |               |        |        |        |

## 漏洞利用

通过上述对 Foxit Reader 内存管理的分析，我们会有一些可能存在的漏洞利用的想法。

由于当前版本的 Foxit Reader 没有开启 CFG 机制，所以我们将很容易通过劫持虚表之类的方法劫持控制流从而实现任意代码执行。

Foxit Reader 的堆分配器主要通过一个空闲链表分配和释放内存，该空闲链表是一个单向链表，并且缺少对链表完整性的检验，因此如果我们有机会劫持
`nextfreechunk` 指针，我们将有机会操纵任意的内存块。

针对这种情况，我们可能需要有一个信息泄露和一个越界写漏洞，通过越界写覆盖下一个 chunk 的 `nextfreechunk`
为我们想要的地址，然后进行后续利用。

并且不止于此，由于 `nextfreechunk` 通常与 C++ 对象的虚表指针处在同一位置，所以当存在一个 UAF
漏洞，并且在释放后调用虚函数时，我们还有机会直接劫持控制流。

例如当前存在如下内存布局：

    
    
    |          |          |          |          |
    +----------+----------+----------+----------+ <- free chunk
    | 0        | AAAAAAAA | AAAAAAAA | AAAAAAAA |
    +----------+----------+----------+----------+ <- victim obj
    | vtb      |          |          |          |
    +----------+----------+----------+----------+
    |          |          |          |          |

其中 free chunk 的第一个成员指向 0，表示它是空闲链表的最后一个 chunk。

victim obj 为 C++ 对象，其第一个成员为虚表指针。

若 victim obj 存在 uaf 漏洞，在释放后，其第一个成员指向 free chunk。

    
    
        |          |          |          |          |
    +-> +----------+----------+----------+----------+ <- free chunk
    |   | 0        | AAAAAAAA | AAAAAAAA | AAAAAAAA |
    |   +----------+----------+----------+----------+ <- victim obj
    +-- | nextfree |          |          |          |
        +----------+----------+----------+----------+
        |          |          |          |          |

此后在调用虚函数 `obj.vtb->field_4()` 时，就会执行到我们提前在内存中布局的地址 `0x41414141` 处。

## 总结

Foxit Reader 实现的这套堆分配器在面对涉及大量的小块内存的对象申请与释放时将会有很高的效率，这可能也是 Foxit Reader
在很多方面的性能超过 Adobe Reader 的原因之一。然而这套堆分配器的特点也为漏洞利用提供了一些可能性。

这篇文章分享的漏洞利用思路还不太成熟，真正达到任意代码执行的目的事实上也十分困难。因为实际上 Foxit Reader 的 JS
引擎并没有使用这套堆分配器，尽管这样的思路不需要很复杂的内存布局，但是如果无法通过 JS
或类似的方式操纵内存，仍然很难将内存布局成预期的效果。同样的原因也使信息泄露比较困难，然而信息泄露对于这两种思路又是十分必要的。另外，由于空闲链表是一条单向链表，所以需要保证指针的合法性或者置0，否则可能造成崩溃，这也给利用增加了难度。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/2039/>

