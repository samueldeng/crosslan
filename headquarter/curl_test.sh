curl http://127.0.0.1:5000/cl-containers/10000 -X POST
echo ------------------------------------------------------
curl http://127.0.0.1:5000/cl-containers/10000/running-status -X PUT -d '{"action": "start"}' 
echo ------------------------------------------------------
curl http://127.0.0.1:5000/cl-containers/10000/running-status -X PUT -d '{"action": "stop"}' 
echo ------------------------------------------------------ 
curl http://127.0.0.1:5000/cl-containers/10000/running-status
echo ------------------------------------------------------ 
curl http://127.0.0.1:5000/cl-containers/10000/binding-ips -X PUT -d '{"ipset": "[202.117.15.84]"}' 
echo ------------------------------------------------------ 
curl http://127.0.0.1:5000/cl-containers/10000/data-usage
