from server.ws_manager import WebSocketManager

ws_manager = WebSocketManager()


class ScoreBroadcaster:
    """
    High-level broadcaster for live event scoring.
    """


    @staticmethod
    async def broadcast_brackets_payload(*, event_id: str, class_key: str | None, rounds_payload: list):
        channel = f"event:{event_id}"

        print(
            f"📣 WS BROADCAST | type=brackets_update | "
            f"channel={channel} | class={class_key} | "
            f"rounds={len(rounds_payload)}"
        )
        print("#############################")
        print(f"Payload: {rounds_payload}")
        print("#############################")

        await ws_manager.broadcast(
            channel=f"event:{event_id}",
            payload={
                "type": "brackets_update",
                "event_id": event_id,
                "class_key": class_key,
                "rounds": rounds_payload,
            },
        )

    @staticmethod
    async def broadcast_speed_session_payload(
            *,
            event_id: str,
            class_key: str,
            payload: dict,
    ):
        channel = f"event:{event_id}"

        print(
            f"📣 WS BROADCAST | type=speed_session_update | "
            f"channel={channel} | class={class_key}"
        )
        print("#############################")
        print(f"Payload: {payload}")
        print("#############################")
        await ws_manager.broadcast(
            channel=f"event:{event_id}",
            payload={
                "type": "speed_session_update",
                "event_id": event_id,
                "class_key": class_key,
                **payload,
            },
        )