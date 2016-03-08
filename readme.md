grok-test
=====================
grok表达式调试工具
依赖pygrok库


创建项目
--------------

    ./grok-check.py --init logback

测试项目
--------------

    ./grok-check.py syslog logback nginx

部署项目
--------------

    ./grok-check.py --logstash syslog

目录结构
---------------

    + syslog
    | + patterns
    | |   cust          #自定义grok表达式
    | |   ...           #可以有多个文件
    |   datapattern     #数据提取主表达式
    |   sample1.log     #测试样本数据
    |   sample2.log     #更多测试样本
    |   ...
    |   80-syslog.conf  #logstash配置文件模版

调试过程
-----------------
- 创建项目
    ./grok-check.py -i hello
- 复制样本数据
- 定制cust
- 定制datapattern
- 测试项目
    ./grok-check.py hello
- 生成配置
    ./grok-check.py -l hello
- 部署项目
    复制配置文件和自定义pattern到logstash配置目录

