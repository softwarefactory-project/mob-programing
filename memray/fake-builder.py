import time
print("Starting the builder")

ctx = 0

class Image:
    def __init__(self, ctx):
        self.ctx = ctx

    def display_image_name(self):
        return 35535 * ("building image %d" % self.ctx) + 35535 * 'a' + 1024 * 'b'


def leak_logs():
    logs.append(logs)
    s = str(logs)

# Logs is leaking...
logs = []
while True:
    image = Image(ctx)
    logs.append(image.display_image_name())

    time.sleep(0.5)
 
    leak_logs()

    time.sleep(0.5)
    ctx += 1
    print(ctx)

    if ctx % 3 == 0:
        logs.pop()

    if ctx % 10 == 0:
        logs.clear()
