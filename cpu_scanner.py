
#FastAPI and Pydantic Related Libraries
from fastapi import FastAPI
from pydantic import BaseModel,Field
from typing import List

#APScheduler Related Libraries
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

import uuid

import logging
import psutil
from datetime import datetime
import os


# Global Variables
app = FastAPI(title="APP for demostrating integration with FastAPI and APSCheduler", version="2020.11.1",
              description="An Example of Scheduling CPU scanner info periodically")
Schedule = None
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def tick(job_id):
    print(f'!!!!!!!!!!!!!!!! Tick! call by job {job_id}')


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
    global Schedule
    try:
        jobstores = {
            'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
        }
        Schedule = AsyncIOScheduler(jobstores=jobstores)
        Schedule.start()
        logger.info("Created Schedule Object")
    except:
        logger.error("Unable to Create Schedule Object")


@app.on_event("shutdown")
async def pickle_schedule():
    """
    An Attempt at Shutting down the schedule to avoid orphan jobs
    """
    global Schedule
    Schedule.shutdown()
    logger.info("Disabled Schedule")


@app.post("/enable_cpu_scanner/", response_model=CPURateResponse, tags=["API"])
def enable_cpu_scanner():
    cpu_rate = psutil.cpu_percent(interval=1)

    logging.info(f"cpu_rate = {cpu_rate}")

    return {"cpu_rate": cpu_rate}


@app.post("/set_cpu_scanner_job/", response_model=SetCPUScannerJobResponse, tags=["API"])
def set_cpu_scanner_job():
    random_suffix = uuid.uuid1()
    job_id = str(random_suffix)

    cpu_scanner_job = Schedule.add_job(tick, 'interval', seconds=30, id=job_id, args=[job_id])

    job_id = cpu_scanner_job.id
    logging.info(f"set cpu scanner job, id = {job_id}")

    return {"job_id": job_id}


@app.post("/del_cpu_scanner_job/", response_model=DelCPUScannerJobResponse, tags=["API"])
def del_cpu_scanner_job(job_id:str):

    Schedule.remove_job(job_id)

    logging.info(f"set cpu scanner job, id = {job_id}")

    return {"job_id": job_id}



