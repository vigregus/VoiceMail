class StateMachine(object):
    def __init__(self):
        self.transitions = {}
        self.current_state = None

    def add_transition(self,src_state,event,dst_state):
        if not self.transitions.get(src_state.state_name):
            self.transitions[src_state.state_name] = {}

        self.transitions[src_state.state_name][event] = dst_state

    def change_state(self,event):
        self.current_state = self.transitions[self.current_state.state_name][event]

    def start(self,initial_state):
        self.current_state = initial_state
        self.current_state.enter()
            
