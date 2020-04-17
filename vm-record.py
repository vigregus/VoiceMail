#!/usr/bin/env python

import ari
import logging
import time
import os
import sys

from event import Event
from state_machine import StateMachine
from recording_state import RecordingState
from ending_state import EndingState
from hungup_state import HungUpState
from reviewing_state import ReviewingState

#As we add more states to our state machine , we will import the necessary
#state here

logging.basicConfig(level=logging.ERROR)
LOGGER = logging.getLogger(__name__)

client = ari.connect('http://localhost:8088','asterisk','618553')

class VoiceMailCall(object):
    def __init__(self,ari_client, channel, mailbox):
        self.client = ari_client
        self.channel = channel
        self.vm_path = os.path.join('voicemail','mailbox',str(time.time()))
        self.setup_state_machine()

    def setup_state_machine(self):
        # This is where we will initialize states, create a state machine, add
        # state transitions to the state machine, and start the state machine.
        hungup_state = HungUpState(self)
        recording_state = RecordingState(self)
        ending_state = EndingState(self)
        reviewing_state = ReviewingState(self)

        self.state_machine = StateMachine()
        self.state_machine.add_transition(recording_state, Event.DTMF_OCTOTHORPE,
                                          ending_state)
        self.state_machine.add_transition(recording_state, Event.HANGUP,
                                          hungup_state)
        self.state_machine.add_transition(recording_state, Event.DTMF_STAR,recording_state)

        self.state_machine.add_transition(reviewing_state, Event.HANGUP,
                                          hungup_state)
        self.state_machine.add_transition(reviewing_state, Event.DTMF_OCTOTHORPE,
                                          ending_state)
        self.state_machine.add_transition(reviewing_state, Event.DTMF_STAR,
                                          recording_state)
        self.state_machine.start(recording_state)

def stasis_start_cb(channel_obj,event):
    channel = channel_obj['channel']
    channel_name = channel.json.get('name')
    mailbox = event.get('args')[0]

    print("Channel {0} recording voicemail for {1}".format(channel_name,mailbox))
    channel.answer()
    VoiceMailCall(client,channel,mailbox)

client.on_channel_event('StasisStart', stasis_start_cb)
client.run(apps=sys.argv[1])
