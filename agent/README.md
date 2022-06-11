# Monitor Agent

## 概要
Monitor Agent 是使用 `Python` 作为脚本语言，使用  工具对 `hpb` 服务的状态进行查询，使用 `prometheus-client` 模块将数据格式化输出，使用 `Flask` 工具提供外部访问接口，将格式化后的数据直接进行展示；

## 部署
为了保证数据采集的基础环境一致性，数据采集进程均使用 `docker` 方式部署;
### 容器编排部署
如果你希望采集关于运行 hpb 服务的主机资源更多的信息，你可以使用 `docker-compose` 来进行批量部署多个数据采集进程；
* prom/node-exporter （获取主机资源 | 参考: https://github.com/prometheus/node_exporter）
* ncabatoff/process-exporter （获取指定进程资源 | 参考: https://github.com/rberwald/process-exporter）
* hpbmon/agent-hpb-exporter

#### 步骤
1、修改配置
修改agent.yaml 中的配置信息

2、启动agent

./startagent.sh

3、查看数据采集信息
```
#hpbmon_agent_host_exporter
curl http://localhost:9100/metrics/

#hpbmon_agent_hpb_exporter
curl http://localhost:9101/metrics/ghpb
```
4、关闭agent
```
docker-compose down
```

### 单个容器部署
如果你希望只采集 hpb 服务的运行状态信息，你可以使用 `docker` 命令来运行一个数据采集容器；

#### 步骤
1、编译镜像
```
cd ./hpb_exporter
docker build -t hpbmon/agent-hpb-exporter .
cd ..
```
2、启动容器
Tips：
请填入宿主机物理网卡 IP 地址，切勿使用 127.0.0.1，exporter 进程在容器中运行，127.0.0.1 将会导致访问容器本地端口，以下示例中x.x.x.x表示为本地宿主机内网IP；

示例：
```
docker run -d --name="hpbmon_agent_hpb_exporter_1337" \
--pid="host" \
-p 1920:1923 \
-v /etc/localtime:/etc/localtime \
-v "/data/hpb_secp256k1_sha3/":"/data/hpb_secp256k1_sha3/" \
-v "/data/hpb_secp256k1_sha3/test-chain/0":"/data/hpb_secp256k1_sha3/test-chain/0" \
-v "`pwd`/hpb_monitor_agent.py":"/config/hpb_monitor_agent.py" \
-e node_ip_PORT="x.x.x.x:1337" \
-e NODE_DIR="/data/hpb_secp256k1_sha3/test-chain/0" \
hpbmon/agent-hpb-exporter
```
3、查看数据采集信息
```
#hpbmon_agent_hpb_exporter
curl http://localhost:1920/metrics/hpb
```

### 错误信息
1、容器启动失败
* 使用 `docker-compose logs container-name` or `docker logs container-name` 查看容器错误信息，一般原因是参数传入有误

2、容器启动成功，但是查看数据为空
* 启动数据采集进程时，会检查本地是否运行 hpb 服务，如果没有运行 hpb 服务，则 `Node_Get_ServiceStatus` 标签返回数值为 0，其他标签为空
