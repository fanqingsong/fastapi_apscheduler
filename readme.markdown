
# Purpose
With the help of fastapi and apscheduler, implement API to get cpu rate and set/delete periodical cpu scan job.

reference:
https://ahaw021.medium.com/scheduled-jobs-with-fastapi-and-apscheduler-5a4c50580b0e

# Architecture

Seperate workload from fastapi server, in order to prevent the server from being too busy.

Select APScheduler as time policy manager.

Select Ray as logic node to execute workload.

The call from fastapi or apscheduler to ray cluster is asynchronous, so all the communication is reactive, no blocking status exists.

![components](pics/architect.png)

# Description:
To demostrating how to use fastapi and apscheduler

Requirements:
previde API to get CPU rate, and get it periodically

(1) get_cpu_rate -- get current cpu rate by this call

(2) set_cpu_scanner_job -- set one scheduled job to scan cpu rate periodically

(3) del_cpu_scanner_job -- delete the scheduled job


# Install

run command
```
pip install cryptography APSCheduler SQLAlchemy
pip install -U ray[default]
```

# run:
## start ray cluster manually

reference:
reference to  https://docs.ray.io/en/master/configure.html
https://docs.ray.io/en/releases-0.8.5/using-ray-on-a-cluster.html


### Start HeadNode

Run Command

```
ray start --head
```

Get the output
```
root@XXXXXXX:~/win10/mine/fastapi_apscheduler# ray start --head
Local node IP: 192.168.1.10
2021-08-04 18:48:32,942 INFO services.py:1166 -- View the Ray dashboard at http://localhost:8265

--------------------
Ray runtime started.
--------------------

Next steps
  To connect to this Ray runtime from another node, run
    ray start --address='192.168.1.10:6379' --redis-password='5241590000000000'

  Alternatively, use the following Python code:
    import ray
    ray.init(address='auto', _redis_password='5241590000000000')

  If connection fails, check your firewall settings and network configuration.

  To terminate the Ray runtime, run
    ray stop
```

### Start workder node 

That node can locate in a different machine.
If you don't run this command, It's OK, because the head node has worker node as well.

reference URL: https://docs.ray.io/en/master/cluster/index.html

```
ray start --address='192.168.1.10:6379'
```


### start fastapi server

run the following command
```
cd app
uvicorn cpu_scanner:app --reload
```

Then go to browser, access the swagger page to test API:
http://127.0.0.1:8000/docs



