# Copyright (C) 2023 Red Hat
# SPDX-License-Identifier: Apache-2.0
import os
import re

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Initializes your app with your bot token and socket mode handler
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

@app.message(":wave:")
def say_hello(message, say):
    user = message["user"]
    print("Got: ", message)
    say("Hello " + user + "!")


def get_text(json) -> str:
    #import pdb; pdb.set_trace()
    if isinstance(json, list):
        for elem in json:
            v = get_text(elem)
            if v:
                return v
    elif isinstance(json, dict):
        for k,v in json.items():
            if k == "text":
                return v
            value_content = get_text(v)
            if value_content:
                return value_content
    return ""

@app.message("new topic")
def set_topic(message, say):
    topic = get_text(message['text'])
    app.client.conversations_setTopic(channel=message['channel'], topic=topic)

def setup_db():
    import sqlite3
    con = sqlite3.connect("threads.db")
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS threads(name, count)")
    return con

def incr_thread_message_count(thread):
    counters = setup_db()
    counter = counters.execute("SELECT count FROM threads WHERE name = ?", (thread,)).fetchone()
    if not counter:
        counter = 0
        counters.execute("INSERT INTO threads VALUES (?, 1)", (thread,))
    else:
        counter = counter[0]
        counters.execute("UPDATE threads SET count = ? WHERE name = ?", (counter + 1, thread))
    counters.commit()
    return counter
    

@app.message(".*")
def thread_killer(message, say):
    thread_ts = message.get("thread_ts")
    if thread_ts:
        count = incr_thread_message_count(str(thread_ts))
        if count > 2:
            msg = "Move the thread to JIRA! The thread will be terminated after the next message"
            # TODO: register notification to avoid repeat?
            say(text=msg, thread_ts=thread_ts)
            # TODO: delete new message?


# Start your app
if __name__ == "__main__":
        SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
