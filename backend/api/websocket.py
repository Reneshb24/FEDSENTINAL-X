"""
FedSentinel WebSocket API.

The WebSocket layer exposes the existing EventManager event stream
to realtime consumers such as the security dashboard.

Responsibilities:
    - accept WebSocket connections
    - optionally filter events by round
    - replay historical events
    - receive newly emitted events immediately
    - disconnect cleanly

This module does NOT perform detection or create security decisions.
"""

from __future__ import annotations

import asyncio

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from backend.api.dependencies import get_orchestrator
from backend.schemas.events import SecurityEvent
from backend.services.event_manager import SecurityEventRecord
from backend.services.round_orchestrator import RoundOrchestrator


router = APIRouter(
    prefix="/ws",
    tags=["Realtime"],
)


def _event_to_response(
    event: SecurityEventRecord,
) -> SecurityEvent:
    """
    Convert an internal SecurityEventRecord into the public
    SecurityEvent schema.
    """

    return SecurityEvent(
        event_id=event.event_id,
        event_type=event.event_type,
        timestamp=event.timestamp,
        round_id=event.round_id,
        client_id=event.client_id,
        update_id=event.data.get("update_id"),
        message=event.message,
        payload=event.data,
    )


def _matches_round(
    event: SecurityEventRecord,
    round_id: str | None,
) -> bool:
    """
    Determine whether an event belongs to a WebSocket's round filter.
    """

    if round_id is None:
        return True

    return event.round_id == round_id


async def _stream_events(
    websocket: WebSocket,
    orchestrator: RoundOrchestrator,
    round_id: str | None,
) -> None:
    """
    Replay existing events and stream newly emitted events.

    The EventManager provides an event subscription mechanism, so
    new events are delivered without polling.
    """

    event_manager = orchestrator.event_manager

    loop = asyncio.get_running_loop()

    # Queue owned by this WebSocket connection.
    queue: asyncio.Queue[SecurityEventRecord] = asyncio.Queue()

    def subscriber(
        event: SecurityEventRecord,
    ) -> None:
        """
        Receive events from EventManager.

        EventManager.emit() is synchronous, while the WebSocket
        coroutine runs on an asyncio event loop. call_soon_threadsafe()
        safely transfers the event into the async queue.
        """

        if not _matches_round(event, round_id):
            return

        loop.call_soon_threadsafe(
            queue.put_nowait,
            event,
        )

    # --------------------------------------------------------------
    # Replay historical events first
    # --------------------------------------------------------------

    historical_events = event_manager.query(
        round_id=round_id,
    )

    sent_event_ids: set[str] = set()

    for event in historical_events:
        await websocket.send_json(
            _event_to_response(event).model_dump(
                mode="json"
            )
        )

        sent_event_ids.add(event.event_id)

    # --------------------------------------------------------------
    # Subscribe for future events
    # --------------------------------------------------------------

    event_manager.subscribe(subscriber)

    try:
        while True:
            event = await queue.get()

            # Avoid sending an event twice if it was already included
            # during historical replay.
            if event.event_id in sent_event_ids:
                continue

            await websocket.send_json(
                _event_to_response(event).model_dump(
                    mode="json"
                )
            )

            sent_event_ids.add(event.event_id)

    finally:
        event_manager.unsubscribe(subscriber)


@router.websocket("/events")
async def websocket_events(
    websocket: WebSocket,
    orchestrator: RoundOrchestrator = Depends(
        get_orchestrator
    ),
) -> None:
    """
    Global realtime FedSentinel event stream.

    Endpoint:
        /ws/events
    """

    await websocket.accept()

    try:
        await _stream_events(
            websocket=websocket,
            orchestrator=orchestrator,
            round_id=None,
        )
    except WebSocketDisconnect:
        return
    except asyncio.CancelledError:
        return


@router.websocket("/events/{round_id}")
async def websocket_round_events(
    websocket: WebSocket,
    round_id: str,
    orchestrator: RoundOrchestrator = Depends(
        get_orchestrator
    ),
) -> None:
    """
    Realtime event stream restricted to one round.

    Endpoint:
        /ws/events/{round_id}
    """

    await websocket.accept()

    try:
        await _stream_events(
            websocket=websocket,
            orchestrator=orchestrator,
            round_id=round_id,
        )
    except WebSocketDisconnect:
        return
    except asyncio.CancelledError:
        return