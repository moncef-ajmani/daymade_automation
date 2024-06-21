from status_logger import update_status
from threading import Thread
import time

class Pipeline(Thread):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.phases = []
        self.running = False

    def add_phase(self, phase):
        self.phases.append(phase)

    def run(self):
        self.running = True
        try:
            update_status(self.name, 'Pipeline execution started')
            for phase in self.phases:
                update_status(self.name, f'Phase {phase.name}: STARTED')
                phase.execute()
                update_status(self.name, f'Phase {phase.name}: COMPLETED')
            update_status(self.name, 'Pipeline execution completed')
        except Exception as e:
            update_status(self.name, 'FAILED')
            raise e
        finally:
            self.running = False

    def get_status(self):
        if self.running:
            return {"stage": self.name, "status": "Running"}
        else:
            return {"stage": self.name, "status": "Not started"}
