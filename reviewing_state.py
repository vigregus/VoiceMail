import uuid

class ReviewingState(object):
    state_name = "reviewing"

    def __init__(self,call):
        self.call = call
        self.playback_id = None
        self.hangup_event = None
        self.playback_finished = None
        self.dtmf_event = None
        self.playback = None

    def enter(self):
        self.playback_id = str(uuid.uuid4())
        print "Entering reviewing state"
        self.hangup_event = self.call.channel.on_event("ChannelHangupRequest",self.on_hangup)
        self.playback_finished = self.call.client.on_event("PlaybackFinished",self.on_playback_finished)
        self.dtmf_event = self.call.channel.on_event('ChannelDtmfReceived',self.on_dtmf)
        self.playback = self.call.channel.playWithId(playbackId=self.playback_id,media="recording:{0}".format(self.call.vm_path))

    def cleanup(self):
        self.playback_finished.close()
        if self.playback:
            self.playback.stop()
        self.dtmf_event.close()
        self.hangup_event.close()

    def on_hangup(self,channel,event):
        print "Accepted recording {0} on hangup".format(self.call.vm_path)
        self.cleanup()
        self.call.state_machine.change_state(Event.HANGUP)

    def on_playback_finished(self,event):
        if self.playback_id == event.get('playback').get('id'):
            self.playback = None

    def on_dtmf(self,channel,event):
        digit = event.get('digit')
        if digit == '#':
            print "Accepted recording {0} on DTMF #".format(self.call.vm_path)
            self.cleanup()
            self.call.state_machine.change_state(Event.DTMF_OCTOTHORPE)
        elif digit == '*':
            print "Discarding stored recording {0} on DTMF *".format(self.call.vm_path)
            self.cleanup()
            self.call.client.recordings.deleteStored(recordingName=self.call.vm_path)
            self.call.state_machine.change_state(Event.DTMF_STAR)
