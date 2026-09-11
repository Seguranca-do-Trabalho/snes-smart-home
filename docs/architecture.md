# Architecture

Home Assistant is the source of truth. The first version uses `GET /api/states` on the bridge. Home Assistant's WebSocket API offers `get_states`, `get_services`, and `state_changed` subscription; V1 should migrate to WebSocket to update the UI via events.

The ROM receives `domain + features + state + name + value` and chooses the renderer. X/Y coordinates exist only as layout calculation, never as device definition.
