
#FastAPI and Pydantic Related Libraries
from fastapi import FastAPI
from pydantic import BaseModel,Field
from typing import List
import asyncio

#APScheduler Related Libraries
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

import uuid

import logging
import psutil
from datetime import datetime
import os

import ray

import time

ray.init(address="192.168.1.10:6379")

# Global Variables
app = FastAPI(title="APP for demostrating integration with FastAPI and APSCheduler", version="2020.11.1",
              description="An Example of Scheduling CPU scanner info periodically")

Schedule = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CPURateResponse(BaseModel):
    cpu_rate:float=Field(title="CPU Rate", description="The current CPU rate")


class SetCPUScannerJobResponse(BaseModel):
    job_id:str=Field(title="CPU Scanner Job ID", description="CPU Scanner Job ID")


class DelCPUScannerJobResponse(BaseModel):
    job_id:str=Field(title="CPU Scanner Job ID", description="CPU Scanner Job ID")



@app.on_event("startup")
async def load_schedule_or_create_blank():
    """
    Instatialise the Schedule Object as a Global Param and also load existing Schedules from SQLite
    This allows for persistent schedules across server restarts.
    """
    print("#####startup event is called.")

    global Schedule
    try:
        jobstores = {
            'default': SQLAlchemyJobStore(url='sqlite:///../store/jobs.sqlite')
        }
        Schedule = AsyncIOScheduler(jobstores=jobstores)
        Schedule.start()
        # asyncio.get_event_loop().run_forever()
        logger.info("Created Schedule Object")
    except:
        logger.error("Unable to Create Schedule Object")


@app.on_event("shutdown")
async def pickle_schedule():
    """
    An Attempt at Shutting down the schedule to avoid orphan jobs
    """
    print("#####shutdown event is called.")

    global Schedule
    Schedule.shutdown()
    logger.info("Disabled Schedule")


@ray.remote
def get_cpu_rate_on_ray():
    logging.info("get_cpu_rate_on_ray called.")
    print("get_cpu_rate_on_ray called. !!")

    job_id = ray.get_runtime_context().job_id
    print(f"job_id={job_id}")

    # time.sleep(10)

    cpu_rate = psutil.cpu_percent(interval=1)

    logging.info(f"cpu_rate = {cpu_rate}")

    return cpu_rate

async def scan_cpu_rate(job_id):
    logging.info(f'###!!!!!!!!!!!!! Tick! call by apscheduler job {job_id}')

    future = get_cpu_rate_on_ray.remote()

    logging.info(future)

    # with wait to prevent blocking status
    # https://medium.com/distributed-computing-with-ray/ray-tips-and-tricks-part-i-ray-wait-9ed7a0b9836d
    ids = [future]
    ready, not_ready = ray.wait(ids)
    print('Ready length, values: ', len(ready), ray.get(ready))
    print('Not Ready length:', len(not_ready))

    cpu_rate = ray.get(future)

    logging.info(f"cpu_rate = {cpu_rate}")

@app.post("/get_cpu_rate/", response_model=CPURateResponse, tags=["API"])
def get_cpu_rate():
    future = get_cpu_rate_on_ray.remote()

    logging.info(future)

    # with wait to prevent blocking status
    # https://medium.com/distributed-computing-with-ray/ray-tips-and-tricks-part-i-ray-wait-9ed7a0b9836d
    ids = [future]
    ready, not_ready = ray.wait(ids)
    print('Ready length, values: ', len(ready), ray.get(ready))
    print('Not Ready length:', len(not_ready))

    cpu_rate = ray.get(future)

    logging.info(f"cpu_rate = {cpu_rate}")

    return {"cpu_rate": cpu_rate}


@app.post("/set_cpu_scanner_job/", response_model=SetCPUScannerJobResponse, tags=["API"])
def set_cpu_scanner_job():
    random_suffix = uuid.uuid1()
    job_id = str(random_suffix)

    cpu_scanner_job = Schedule.add_job(scan_cpu_rate, 'interval', seconds=30, id=job_id, args=[job_id])

    job_id = cpu_scanner_job.id
    logging.info(f"set cpu scanner job, id = {job_id}")

    return {"job_id": job_id}


@app.post("/del_cpu_scanner_job/", response_model=DelCPUScannerJobResponse, tags=["API"])
def del_cpu_scanner_job(job_id:str):

    Schedule.remove_job(job_id)

    logging.info(f"set cpu scanner job, id = {job_id}")

    return {"job_id": job_id}



