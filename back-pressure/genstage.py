#!/bin/env python3
# Context: reproduce GenStage using python generator
# https://dev.to/dcdourado/understanding-genstage-back-pressure-mechanism-1b0i

# Stage A, data_ingestor
A_ENERGY = 1
# Stage B, republisher
B_ENERGY = 10
# Stage C, reporter
C_ENERGY = 2


import datetime, time


def loggy(msg):
    print("%s: %s" % (datetime.datetime.now(), msg))


# Back pressure using generator
def data_ingestor():
    for page in range(0, 10):
        time.sleep(A_ENERGY / 10)
        loggy("Ingesting page " + str(page))
        for result in range(0, 10):
            yield ("build-" + str(page) + ":" + str(result))


def republisher(stage_a):
    for result in stage_a:
        loggy("Republishing " + result)
        time.sleep(B_ENERGY / 10)
        for dest in ["mail", "blog", "elastic"]:
            yield ("publish-" + dest + " | " + result)


def reporter(stage_b):
    for event in stage_b:
        time.sleep(C_ENERGY / 10)
        loggy("Reporting " + event)


def backpressure_demo():
    reporter(republisher(data_ingestor()))


# Forward pressure using function call
def data_ingestor_forward():
    for page in range(0, 10):
        time.sleep(A_ENERGY / 10)
        loggy("Ingesting page " + str(page))
        for result in range(0, 10):
            republisher_forward("build-" + str(page) + ":" + str(result))


def republisher_forward(result):
    loggy("Republishing " + result)
    time.sleep(B_ENERGY / 10)
    for dest in ["mail", "blog", "elastic"]:
        reporter_forward("publish-" + dest + " | " + result)


def reporter_forward(event):
    time.sleep(C_ENERGY / 10)
    loggy("Reporting " + event)


def forward_demo():
    data_ingestor_forward()
