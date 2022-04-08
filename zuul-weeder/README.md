Given a list of nodeset, job and pipeline configuration, e.g.:

- job: name=job1 nodeset=ns1
- job: name=job2 nodeset=ns2
- nodeset: name=ns1
- nodeset: name=ns2
- nodeset: name=ns3
- pipeline: name=check job=job1

Zuul weeder finds the unused configuration:

- job2, because not attached to a pipeline
- ns2, because no pipeline job use it
- ns3, because no job use it


# Part2

If the `job1` is defined as: `name=job1 nodeset=ns1 parent=job2`
Then only `ns3` is unused.


# Graph based solution.

The configuration is actually a graph:

    check
    .    job1
    \---.
         \---.ns1

   job2 .
         \---.ns2         .ns3


And from the roots, e.g. the pipeline, we want to collect all the reachable node,
then the dead node are: `all_nodes - reachable_nodes`
