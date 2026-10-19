![1.jpg](https://image.3001.net/images/20190710/1562748823_5d25a797dfa5e.jpg!small)

**Ocean Lotus
Group，也被称之为APT32，这个黑客组织此前主要的攻击目标以越南、老挝和菲律宾等东亚国家为主，虽然私营企业是该组织的主要目标，但外国政府、政治活动家和新闻记者也是他们的攻击目标之一。**

APT32的攻击工具非常多样化，从Mimikatz和Cobalt
Strike这样的高级定制工具，到ShellCode以及后门等等，应有尽有。而且他们所使用的很多代码都经过了高度模糊处理或混淆处理，并使用了不同的技术来提升检测和分析的难度，导致研究人员更加难以对它们进行逆向分析。

在这篇文章中，我们将介绍该组织所使用的其中一种代码混淆技术，而这种技术也被APT32广泛应用到了他们的后门代码中。反混淆处理的过程中需要使用到[Cutter](https://github.com/radareorg/cutter)以及官方开源逆向工程框架-radare2，还请各位同学自行搜索下载。

### 下载和安装Cutter

Cutter目前支持Linux、macOS和Windows。

Cutter下载地址：【[点我下载](https://github.com/radareorg/cutter/releases)】

Cutter基础教程：【[点我获取](https://cutter.re/docs/building.html)】

![2.png](https://image.3001.net/images/20190710/1562748861_5d25a7bdbd471.png!small)

## 后门分析

我们的样本（486be6b1ec73d98fdd3999abe2fa04368933a2ec）是多级感染链中的一部分，而且APT32在多个活动中都使用到了这个后门，例如恶意文件样本（115f3cb5bdfb2ffe5168ecb36b9aed54）。这个文档声称自己来自于360，但是其中包含了一个恶意VBA宏，这个恶意宏会向rundll32.exe注入恶意Shellcode。Shellcode中包含了解密代码，可以直接对恶意代码进行解密并将相应的DLL加载进内存，而DLL包含的就是后门逻辑。

首先，后门会解密一个配置文件，其中存储的信息包含C2服务器基础信息在内。接下来，代码会尝试使用自定义PE加载器向内存中加载恶意DLL。这个DLL会被HTTPProv.dll调用，并能够与C2服务器通信。后门还可以从C2服务器接收十几种不同的指令，包括Shellcode执行、新进程创建以及文件和目录修改等操作。

该组织所使用的很多混淆技术其目的就是要增加逆向分析的难度，而且其二进制代码中使用了大量的垃圾代码，这些垃圾代码会增加样本的体积和复杂性，以分散研究人员的注意力。而且，其中的代码集经常会与堆栈指针一起使用，而普通的反编译工具无法对这种情况进行有效处理。

## 混淆技术

APT32在进行代码混淆处理时，大量使用了控制流混淆，并且向函数流中注入了大量垃圾代码块。这些垃圾代码块不会实现任何功能，只是为了混淆视听而已。

![3.png](https://image.3001.net/images/20190710/1562748897_5d25a7e1b4719.png!small)

大家可以从上图中看到，其中包含了大量垃圾代码块。仔细分析后我们会发现，所有需要跳转到这些代码段的条件判断结果都为False，而且都是以条件跳转结束的，跟之前的条件判断正好相反。比如说，垃圾代码段之前的条件判断为jo
<some_addr>，那么垃圾代码很有可能以jno<some_addr>结束。如果之前的代码段以jne
<another_addr>结束，那么垃圾代码段就会以je <another_addr>结束。

![4.png](https://image.3001.net/images/20190710/1562748912_5d25a7f0b7631.png!small)

这样一来，我们就可以对这些垃圾代码段定性了。第一种特性：出现两个连续的垃圾代码块，以相反的条件跳转到相同的目标地址并结束。第二种特性：要求第二个块不包含有意义的指令，如字符串引用或代码调用等等。

当满足这两个特征时，我们可以说第二个块很可能是垃圾代码块。这样，我们就可以将垃圾块从图表中删除了，并使用无条件跳转来修补源代码。

![5.png](https://image.3001.net/images/20190710/1562748923_5d25a7fb0d25a.png!small)

## 编写核心类

首先，我们要创建一个Python类作为我们的核心类，这个类需要包含查找和移除垃圾代码块的逻辑。先定义__init__函数，该函数可以接收管道消息，可以是来自redare2的r2pipe对象（importr2pipe），也可以是来自Cutter的cutter对象（import
cutter）。

    
    
    class GraphDeobfuscator:
    
       def __init__(self, pipe):
    
           """an initializationfunction for the class
    
          
    
           Arguments:
    
               pipe {r2pipe} -- an instance ofr2pipe or Cutter's wrapper
    
           """
    
           self.pipe = pipe

现在我们就可以使用这个管道来执行radare2命令了。这个管道对象包含两种执行r2命令的方式。第一种为pipe.cmd(<command>)，它能够以字符串的形式返回命令执行结果。第二种为pipe.cmdj(<command>j)，它你能够根据radare2命令的输出结果返回解析后的JSON对象。

接下来就是从当前函数中获取所有的代码块，然后进行迭代。这里可以使用afbj米工龄来获取函数中所有代码块的JSON对象。

    
    
       def clean_junk_blocks(self):
    
           """Search a givenfunction for junk blocks, remove them and fix the flow.
    
           """
    
           # Get all the basic blocks of thefunction
    
           blocks = self.pipe.cmdj("afbj @$F")
    
           if not blocks:
    
               print("[X] No blocks found. Is it afunction?")
    
               return
    
           modified = False
    
           # Iterate over all the basic blocks ofthe function
    
           for block in blocks:
    
               # do something

针对每一个块，根据之前的判断条件进行分析，获取候选垃圾代码块：

    
    
       def get_fail_block(self, block):
    
           """Return the block towhich a block branches if the condition is fails
    
          
    
           Arguments:
    
               block {block_context} -- A JSONrepresentation of a block
    
          
    
           Returns:
    
               block_context -- The block to whichthe branch fails. If not exists, returns None
    
           """
    
           # Get the address of the"fail" branch
    
           fail_addr = self.get_fail(block)
    
           if not fail_addr:
    
               return None
    
           # Get a block context of the failaddress
    
           fail_block = self.get_block(fail_addr)
    
           return fail_block if fail_block elseNone
    
       def is_successive_fail(self, block_A,block_B):
    
           """Check if the endaddress of block_A is the start of block_B
    
           Arguments:
    
               block_A {block_context} -- A JSONobject to represent the first block
    
               block_B {block_context} -- A JSONobject to represent the second block
    
          
    
           Returns:
    
               bool -- True if block_B comes immediatelyafter block_A, False otherwise
    
           """
    
          return ((block_A["addr"] +block_A["size"]) == block_B["addr"])

接下来，我们要判断候选垃圾代码段是否包含无效指令：

    
    
       def contains_meaningful_instructions (self,block):
    
           '''Check if a block contains meaningfulinstructions (references, calls, strings,...)
    
          
    
           Arguments:
    
               block {block_context} -- A JSONobject which represents a block
    
          
    
           Returns:
    
               bool -- True if the block containsmeaningful instructions, False otherwise
    
           '''
    
           # Get summary of block - strings, calls,references
    
           summary = self.pipe.cmd("pdsb @{addr}".format(addr=block["addr"]))
    
           return summary != ""

最后，枚举出所有对立的跳转条件：

    
    
       jmp_pairs = [
    
           ['jno', 'jo'],
    
           ['jnp', 'jp'],
    
           ['jb', 'jnb'],
    
           ['jl', 'jnl'],
    
           ['je', 'jne'],
    
           ['jns', 'js'],
    
           ['jnz', 'jz'],
    
           ['jc', 'jnc'],
    
           ['ja', 'jbe'],
    
           ['jae', 'jb'],
    
           ['je', 'jnz'],
    
           ['jg', 'jle'],
    
           ['jge', 'jl'],
    
           ['jpe', 'jpo'],
    
           ['jne', 'jz']]
    
       def is_opposite_conditional(self, cond_A,cond_B):
    
           """Check if two operandsare opposite conditional jump operands
    
          
    
           Arguments:
    
               cond_A {string} -- the conditionaljump operand of the first block
    
               cond_B {string} -- the conditionaljump operand of the second block
    
          
    
           Returns:
    
               bool -- True if the operands areopposite, False otherwise
    
           """
    
           sorted_pair = sorted([cond_A, cond_B])
    
           for pair in self.jmp_pairs:
    
               if sorted_pair == pair:
    
                   return True
    
           return False

将上述所有代码整合到clean_junk_blocks()函数中：

    
    
       def clean_junk_blocks(self):
    
           """Search a givenfunction for junk blocks, remove them and fix the flow.
    
           """
    
           # Get all the basic blocks of thefunction
    
           blocks = self.pipe.cmdj("afbj @$F")
    
           if not blocks:
    
               print("[X] No blocks found. Isit a function?")
    
               return
    
           modified = False
    
           # Iterate over all the basic blocks ofthe function
    
           for block in blocks:
    
               fail_block =self.get_fail_block(block)
    
               if not fail_block or \
    
               not self.is_successive_fail(block,fail_block) or \
    
              self.contains_meaningful_instructions(fail_block) or \
    
               notself.is_opposite_conditional(self.get_last_mnem_of_block(block),self.get_last_mnem_of_block(fail_block)):
    
                   continue

## 使用Radare2

    
    
    if__name__ == "__main__":
    
       graph_deobfuscator = GraphDeobfuscator(pipe)
    
       graph_deobfuscator.clean_graph()

## 使用Cutter

    
    
    ifcutter_available:
    
       # This part will be executed only if Cutteris available.
    
       # This will create the cutter plugin and UIobjects for the plugin
    
       classGraphDeobfuscatorCutter(cutter.CutterPlugin):
    
           name = "APT32 GraphDeobfuscator"
    
           description = "Graph Deobfuscatorfor APT32 Samples"
    
           version = "1.0"
    
           author = "Itay Cohen(@Megabeets_)"
    
           def setupPlugin(self):
    
               pass
    
           def setupInterface(self, main):
    
               pass
    
       
    
       def create_cutter_plugin():
    
           return GraphDeobfuscatorCutter()

为了保证插件正常运行，我们还需要增加一个菜单入口来触发反混淆功能：

    
    
    ifcutter_available:
    
       # This part will be executed only if Cutteris available. This will
    
       # create the cutter plugin and UI objectsfor the plugin
    
       classGraphDeobfuscatorCutter(cutter.CutterPlugin):
    
           name = "APT32 GraphDeobfuscator"
    
           description = "Graph Deobfuscatorfor APT32 Samples"
    
           version = "1.0"
    
           author = "Megabeets"
    
           def setupPlugin(self):
    
               pass
    
           def setupInterface(self, main):
    
               # Create a new action (menu item)
    
               action = QAction("APT32 GraphDeobfuscator", main)
    
               action.setCheckable(False)
    
              # Connect the action to a function - cleaner.
    
               # A click on this action willtrigger the function
    
              action.triggered.connect(self.cleaner)
    
               # Add the action to the"Windows -> Plugins" menu
    
               pluginsMenu =main.getMenuByType(main.MenuType.Plugins)
    
               pluginsMenu.addAction(action)
    
           def cleaner(self):
    
               graph_deobfuscator =GraphDeobfuscator(pipe)
    
               graph_deobfuscator.clean_graph()
    
               cutter.refresh()
    
       def create_cutter_plugin():
    
           return GraphDeobfuscatorCutter()

![6.png](https://image.3001.net/images/20190710/1562749052_5d25a87c2676e.png!small)

![7.png](https://image.3001.net/images/20190710/1562749059_5d25a8836444c.png!small)

接下来，我们就可以看到图形化的分析结果了：

![8.png](https://image.3001.net/images/20190710/1562749069_5d25a88d025e7.png!small)

移除垃圾代码段之后的结果图如下所示：

![9.png](https://image.3001.net/images/20190710/1562749077_5d25a8952b5a3.png!small)

对比图如下：

![10.png](https://image.3001.net/images/20190710/1562749084_5d25a89c6d649.png!small)

![11.png](https://image.3001.net/images/20190710/1562749091_5d25a8a31ead6.png!small)

### 样本SHA256值

    
    
    Be6d5973452248cb18949711645990b6a56e7442dc30cc48a607a2afe7d8ec66
    
    8d74d544396b57e6faa4f8fdf96a1a5e30b196d56c15f7cf05767a406708a6b2

### APT32图形化反混淆工具-完整源代码

    
    
    """A plugin for Cutter and Radare2 to deobfuscate APT32 flow graphs
    
    Thisis a python plugin for Cutter that is compatible as an r2pipe script for
    
    radare2as well. The plugin will help reverse engineers to deobfuscate and remove
    
    junkblocks from APT32 (Ocean Lotus) samples.
    
    """
    
    __author__  = "Itay Cohen, aka @megabeets_"
    
    __company__= "Check Point Software Technologies Ltd"
    
    #Check if we're running from cutter
    
    try:
    
        import cutter
    
        from PySide2.QtWidgets import QAction
    
        pipe = cutter
    
        cutter_available = True
    
    # Ifno, assume running from radare2
    
    except:
    
        import r2pipe
    
        pipe = r2pipe.open()
    
        cutter_available = False
    
    classGraphDeobfuscator:
    
        # A list of pairs of opposite conditionaljumps
    
        jmp_pairs = [
    
            ['jno', 'jo'],
    
            ['jnp', 'jp'],
    
            ['jb', 'jnb'],
    
            ['jl', 'jnl'],
    
            ['je', 'jne'],
    
            ['jns', 'js'],
    
            ['jnz', 'jz'],
    
            ['jc', 'jnc'],
    
            ['ja', 'jbe'],
    
            ['jae', 'jb'],
    
            ['je', 'jnz'],
    
            ['jg', 'jle'],
    
            ['jge', 'jl'],
    
            ['jpe', 'jpo'],
    
           ['jne', 'jz']]
    
        def __init__(self, pipe, verbose=False):
    
            """an initializationfunction for the class
    
            
    
            Arguments:
    
                pipe {r2pipe} -- an instance ofr2pipe or Cutter's wrapper
    
            
    
            Keyword Arguments:
    
                verbose {bool} -- if True willprint logs to the screen (default: {False})
    
            """
    
            self.pipe = pipe
    
            self.verbose = verbose
    
        def is_successive_fail(self, block_A,block_B):
    
            """Check if the endaddress of block_A is the start of block_B
    
            Arguments:
    
                block_A {block_context} -- A JSONobject to represent the first block
    
                block_B {block_context} -- A JSONobject to represent the second block
    
            
    
            Returns:
    
                bool -- True if block_B comesimmediately after block_A, False otherwise
    
            """
    
            return ((block_A["addr"] +block_A["size"]) == block_B["addr"])
    
        def is_opposite_conditional(self, cond_A,cond_B):
    
            """Check if two operandsare opposite conditional jump operands
    
            
    
            Arguments:
    
                cond_A {string} -- the conditionaljump operand of the first block
    
                cond_B {string} -- the conditionaljump operand of the second block
    
            Returns:
    
                bool -- True if the operands areopposite, False otherwise
    
            """
    
            sorted_pair = sorted([cond_A, cond_B])
    
            for pair in self.jmp_pairs:
    
                if sorted_pair == pair:
    
                    return True
    
            return False
    
        defcontains_meaningful_instructions (self, block):
    
            '''Check if a block contains meaningfulinstructions (references, calls, strings,...)
    
            
    
            Arguments:
    
                block {block_context} -- A JSONobject which represents a block
    
            
    
            Returns:
    
                bool -- True if the block containsmeaningful instructions, False otherwise
    
            '''
    
            # Get summary of block - strings,calls, references
    
            summary = self.pipe.cmd("pdsb @{addr}".format(addr=block["addr"]))
    
            return summary != ""
    
        def get_block_end(self, block):
    
            """Get the address ofthe last instruction in a given block
    
            
    
            Arguments:
    
                block {block_context} -- A JSONobject which represents a block
    
            
    
            Returns:
    
                The address of the last instructionin the block
    
            """
    
            # save current seek
    
            self.pipe.cmd("s{addr}".format(addr=block['addr']))
    
            # This will return the address of ablock's last instruction
    
            block_end = self.pipe.cmd("?v $@B:-1")
    
            return block_end
    
        def get_last_mnem_of_block(self, block):
    
            """Get the mnemonic ofthe last instruction in a block
    
            
    
            Arguments:
    
                block {block_context} -- A JSONobject which represents a block
    
            
    
            Returns:
    
                string -- the mnemonic of the lastinstruction in the given block
    
            """
    
            inst_info = self.pipe.cmdj("aoj @{addr}".format(addr=self.get_block_end(block)))[0]
    
            return inst_info["mnemonic"]
    
        def get_jump(self, block):
    
            """Get the address towhich a block jumps
    
            
    
            Arguments:
    
                block {block_context} -- A JSONobject which represents a block
    
            
    
            Returns:
    
                addr -- the address to which theblock jumps to. If such address doesn't exist, returns False 
    
            """
    
            return block["jump"] if"jump" in block else None
    
        def get_fail_addr(self, block):
    
            """Get the address towhich a block fails
    
            
    
            Arguments:
    
                block {block_context} -- A JSONobject which represents a block
    
            
    
            Returns:
    
                addr -- the address to which theblock fail-branches to. If such address doesn't exist, returns False 
    
            """
    
            return block["fail"] if"fail" in block else None
    
        def get_block(self, addr):
    
            """Get the block contextin a given address
    
            
    
            Arguments:
    
                addr {addr} -- An address in ablock
    
            
    
            Returns:
    
                block_context -- the block to whichthe address belongs
    
            """
    
            block = self.pipe.cmdj("abj. @{offset}".format(offset=addr))
    
            return block[0] if block else None
    
        def get_fail_block(self, block):
    
            """Return the block towhich a block branches if the condition is fails
    
            
    
            Arguments:
    
                block {block_context} -- A JSONrepresentation of a block
    
            
    
            Returns:
    
                block_context -- The block to whichthe branch fails. If not exists, returns None
    
            """
    
            # Get the address of the"fail" branch
    
            fail_addr = self.get_fail_addr(block)
    
            if not fail_addr:
    
                return None
    
            # Get a block context of the failaddress
    
            fail_block = self.get_block(fail_addr)
    
            return fail_block if fail_block elseNone
    
        def reanalize_function(self):
    
            """Re-Analyze a functionat a given address
    
            
    
            Arguments:
    
                addr {addr} -- an address of afunction to be re-analyze
    
            """
    
            # Seek to the function's start
    
            self.pipe.cmd("s $F")
    
            # Undefine the function in this address
    
            self.pipe.cmd("af- $")
    
            # Define and analyze a function in thisaddress
    
            self.pipe.cmd("afr @ $")       
    
        def overwrite_instruction(self, addr):
    
            """Overwrite aconditional jump to an address, with a JMP to it
    
            
    
            Arguments:
    
                addr {addr} -- address of aninstruction to be overwritten
    
            """
    
            jump_destination =self.get_jump(self.pipe.cmdj("aoj @ {addr}".format(addr=addr))[0])
    
            if (jump_destination):
    
                self.pipe.cmd("wai jmp0x{dest:x} @ {addr}".format(dest=jump_destination, addr=addr))
    
        def get_current_function(self):
    
            """Return the startaddress of the current function
    
            Return Value:
    
                The address of the currentfunction. None if no function found.
    
            """
    
            function_start =int(self.pipe.cmd("?vi $FB"))
    
            return function_start if function_start!= 0 else None
    
        def clean_junk_blocks(self):
    
            """Search a givenfunction for junk blocks, remove them and fix the flow.
    
            """
    
            # Get all the basic blocks of thefunction
    
            blocks = self.pipe.cmdj("afbj @$F")
    
            if not blocks:
    
                print("[X] No blocks found. Isit a function?")
    
                return
    
            # Have we modified any instruction inthe function?
    
            # If so, a reanalyze of the function isrequired
    
            modified = False
    
            # Iterate over all the basic blocks ofthe function
    
            for block in blocks:
    
                fail_block =self.get_fail_block(block)
    
                # Make validation checks
    
                if not fail_block or \
    
                not self.is_successive_fail(block,fail_block) or \
    
               self.contains_meaningful_instructions(fail_block) or \
    
                notself.is_opposite_conditional(self.get_last_mnem_of_block(block),self.get_last_mnem_of_block(fail_block)):
    
                    continue
    
                if self.verbose:
    
                    print ("Potential junk:0x{junk_block:x}(0x{fix_block:x})".format(junk_block=fail_block["addr"],fix_block=block["addr"]))
    
               self.overwrite_instruction(self.get_block_end(block))
    
                modified = True
    
            if modified:
    
                self.reanalize_function()
    
            
    
        def clean_graph(self):
    
            """the initial functionof the class. Responsible to enable cache and start the cleaning
    
            """
    
            # Enable cache writing mode. changeswill only take place in the session and
    
            # will not override the binary
    
            self.pipe.cmd("eio.cache=true")
    
            self.clean_junk_blocks()
    
            
    
    ifcutter_available:
    
        # This part will be executed only if Cutteris available. This will
    
        # create the cutter plugin and UI objectsfor the plugin
    
        classGraphDeobfuscatorCutter(cutter.CutterPlugin):
    
            name = "APT32 GraphDeobfuscator"
    
            description = "Graph Deobfuscatorfor APT32 Samples"
    
            version = "1.0"
    
            author = "Itay Cohen(@Megabeets_)"
    
            def setupPlugin(self):
    
                pass
    
            def setupInterface(self, main):
    
                # Create a new action (menu item)
    
                action = QAction("APT32 GraphDeobfuscator", main)
    
                action.setCheckable(False)
    
                # Connect the action to a function- cleaner.
    
                # A click on this action willtrigger the function
    
                action.triggered.connect(self.cleaner)
    
                # Add the action to the"Windows -> Plugins" menu
    
                pluginsMenu =main.getMenuByType(main.MenuType.Plugins)
    
                pluginsMenu.addAction(action)
    
            def cleaner(self):
    
                graph_deobfuscator =GraphDeobfuscator(pipe)
    
                graph_deobfuscator.clean_graph()
    
                cutter.refresh()
    
        def create_cutter_plugin():
    
            return GraphDeobfuscatorCutter()
    
    if__name__ == "__main__":
    
        graph_deobfuscator =GraphDeobfuscator(pipe)
    
    graph_deobfuscator.clean_graph()

 *** 参考来源：[checkpoint](https://research.checkpoint.com/deobfuscating-apt32-flow-graphs-with-cutter-and-radare2/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

