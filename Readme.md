/*
Title: CDR/CG Tools
*/

## CDR相关工具

### 1. asn1话单解码器：[`asn1decm.jar`](/downloads/asn1decm.jar)

本工具可以将asn1格式的话单文件解码为文本格式的话单。

* __环境要求：__

   * 安装Java Runtime 1.6以上

+ __例子:__

~~~~  {#code_quota}
    java -jar asn1decm.jar hizcg.sa.201202120812.asn1 
~~~~     
    

### 2. asn1话单查找：[`asn1find.jar`](/downloads/asn1find.jar)

本工具可以直接在asn1格式话单中查找某用户的话单，并以文本格式输出到文件中。

 + __环境要求：__

    * 安装Java Runtime 1.6以上

 + __例子:__

~~~~~
   java -jar asn1find.jar hizcg.sa.201202120812.asn1

~~~~~

### 3. 话单统计和查找：[`cdrparser.py`](/downloads/cdrparser.jar)

本工具可以对一个或多个文本格式话单进行统计和过滤。特点是除了可以使用MSISDN，
IMSI外，还可以使用ip地址，nodeID等其他话单里的字段做为过滤条件来查找话单。

+ __环境要求：__

    * 安装Python解析器。对于window系统，推荐使用[WinPython](http://winpython.sourceforge.net)

+ __例子:__


    * 分析并统计话单文件的话单数量，话单的字段由`cdr.rules`定义：
~~~~~
   cat hizcg.sa.txt | python cdrparser.py stats
~~~~~

   * 分析并统计话单文件的话单数量，需要统计的字段为为`fci`，`apn`及`nodeID`：
~~~~~
   cat hizcg.sa.txt | python cdrparser.py stats fci apn nodeID
~~~~~  
  
   * 分析话单并将话单信息以csv格式输出，还可以指定输出的字段为`fci`，`apn`和`nodeID`：
~~~~~
   cat hizcg.sa.txt | python cdrparser.py export fci apn nodeID
~~~~~  

   * 分析话单并根据过滤条件过滤出匹配的原始话单：
~~~~~
   cat hizcg.sa.txt | python cdrparser.py filter nodeID=GZGGSN101
~~~~~ 