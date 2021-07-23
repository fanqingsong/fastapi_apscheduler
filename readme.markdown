
# ssl_check 
https://ahaw021.medium.com/scheduled-jobs-with-fastapi-and-apscheduler-5a4c50580b0e

run command:
pip install cryptography APSCheduler SQLAlchemy
uvicorn ssl_check:app


# cpu scanner
uvicorn cpu_scanner:app --reload

Description:
To demostrating how to use fastapi and apscheduler

Requirements:
previde API to get CPU rate, and get it periodically

(1) get_cpu_rate -- get current cpu rate by this call

(2) set_cpu_scanner_job -- set one scheduled job to scan cpu rate periodically

(3) del_cpu_scanner_job -- delete the scheduled job


