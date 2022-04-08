import random

total = 10000
for item in range(total):
    conf = random.choice(("job", "job", "job", "nodeset", "pipeline", "nodeset"))
    r = random.randint(0, total)
    if conf == "job":
        attrs = "name=job%d nodeset=ns%d" % (item, r)
    elif conf == "pipeline":
        attrs = "name=pipeline%d job=job%d" % (item, r)
    elif conf == "nodeset":
        attrs = "name=ns%d" % item

    print("%s: %s" % (conf, attrs))
