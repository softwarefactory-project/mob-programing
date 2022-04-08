#!/bin/env python3
# Copyright (C) 2022 Red Hat
# SPDX-License-Identifier: Apache-2.0

class Node:
    def __init__(self, conf, attrs):
        self.conf = conf
        self.name = attrs.pop("name")
        self.attrs = attrs

    def __repr__(self):
        return "<Node %s %s %s>" % (self.conf, self.name, self.attrs)


def solve(conf):
    nodes = []
    for (conf, attrs) in conf:
        node = Node(conf, attrs)
        nodes.append(node)

    pipelines = {}
    for node in nodes:
        if node.conf == "pipeline":
            pipelines[node.name] = node.attrs["job"]

    jobs_alive = {}
    for node in nodes:
        if node.conf == "job":
            if node.name in pipelines.values():
                jobs_alive[node.name] = node.attrs["nodeset"]

    nodesets_alive = set()
    for node in nodes:
        if node.conf == "nodeset":
            if node.name in jobs_alive.values():
                nodesets_alive.add(node.name)

    weeds = set()
    for node in nodes:
        if node.conf == "job" and node.name not in jobs_alive:
            weeds.add(node.name)
        if node.conf == "nodeset" and node.name not in nodesets_alive:
            weeds.add(node.name)

    return weeds


def read_configuration(line):
    [name, attrs] = line.split(': ')
    return (name, {k:v for [k,v] in [kv.split('=') for kv in attrs.split()]})


if __name__ == "__main__":
    import sys
    if sys.argv.pop() == "input":
        result = solve(list(map(read_configuration, sys.stdin.readlines())))
        print(len(result))
    else:
        result = solve(list(map(read_configuration, """

job: name=job1 nodeset=ns1
job: name=job2 nodeset=ns2
nodeset: name=ns1
nodeset: name=ns2
nodeset: name=ns3
pipeline: name=check job=job1

""".strip().split('\n'))))

        if result == set(("job2", "ns2", "ns3")):
            print("Success!")
        else:
            print("Bad weeder result:", result)
