# Start routine on opentron
tmux new -d -s protocol_session "opentrons_execute /data/custom_protocols/main_protocol.py"
