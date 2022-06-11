 docker-compose down
 ps -ef | grep monitor_agent | grep -v grep | awk '{print $2}' | xargs kill -9