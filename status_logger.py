import json

def update_status(stage, status):
    with open(f'{stage}_status.json', 'w') as file:
        json.dump({'stage': stage, 'status': status}, file)