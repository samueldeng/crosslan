curl -H "Content-Type: application/json"  http://127.0.0.1:5000/cl-containers/10001 -X POST
echo ----------------------------------------------------
curl -H "Content-Type: application/json"  http://127.0.0.1:5000/cl-containers/10001/running-status -X PUT -d '{"action": "start"}'
echo ----------------------------------------------------
curl -H "Content-Type: application/json"  http://127.0.0.1:5000/cl-containers/10001/running-status -X PUT -d '{"action": "restart"}'
echo ----------------------------------------------------
curl -H "Content-Type: application/json"  http://127.0.0.1:5000/cl-containers/10001/running-status -X PUT -d '{"action": "stop"}'
echo ----------------------------------------------------
curl -H "Content-Type: application/json"  http://127.0.0.1:5000/cl-containers/10001/running-status
echo ----------------------------------------------------
curl -H "Content-Type: application/json"  http://127.0.0.1:5000/cl-containers/10001/binding-ips -X PUT -d '{"ipset": ["202.117.15.84", "202.117.12.123","10.0.0.1"]}'
echo ----------------------------------------------------
curl -H "Content-Type: application/json"  http://127.0.0.1:5000/cl-containers/10001/data-usage
echo ----------------------------------------------------
echo ----------------------------------------------------
curl -H "Content-Type: application/json"  http://127.0.0.1:5000/cl-containers/10001/user-passwd -X PUT -d '{"userpasswd": "samueldeng:samueldeng"}'
