from event import Event

def sounds_installed(client):
    try:
        client.sounds.get(soundId='vm-intro')
        print "checking sounds"
    except:
        print "Required sound 'vm-intro' not installed. Aborting"
        raise

class GreetingState(object):
    state_name = "greeing"

    def __init__(self, call):
        self.call = call
        self.hangup_event = None
        self.playback_finished = None
        self.dtmf_event = None
        self.playback = None
        sounds_installed(call.client)

    def enter(self):
        print "Entering greeting state"
        self.hangup_event = self.call.channel.on_event('ChannelHangupRequest', self.on_hangup)
        self.playback_finished = self.call.client.on_event('PlaybackFinished', self.on_playback_finished)
        self.dtmf_event = self.call.channel.on_event('ChannelDtmfReceived', self.on_dtmf)
        self.playback = self.call.channel.play(media="sound:vm-intro")

    def cleanup(self):
#        print "Cleaning voicemail recording "
        self.playback_finished.close()
        self.dtmf_event.close()
        self.hangup_event.close()

    def on_hangup(self, channel, event):
        print "Abandoning voicemail recording on hangup"
        self.cleanup()
        self.call.state_machine.change_state(Event.HANGUP)

    def on_playback_finished(self, playback):
        self.cleanup()
        self.call.state_machine.change_state(Event.PLAYBACK_COMPLETE)

    def on_dtmf(self, channel, event):
        digit = event.get('digit')
        if digit == '#':
            print "Cutting off greeting on DTMF #"
            #Let on_playback_finished take care of state change
            self.playback.stop()
