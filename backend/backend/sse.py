import json
import os
import time

from django.http import HttpResponse, StreamingHttpResponse


def _get_redis():
    redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    try:
        import redis

        return redis.from_url(redis_url)
    except Exception:
        return None


def notify(event_type):
    """Publish a cache-invalidation event to all connected SSE clients."""
    r = _get_redis()
    if r:
        try:
            r.publish("lenore:events", json.dumps({"type": event_type}))
        except Exception:
            pass


def sse_view(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=401)

    def event_stream():
        r = _get_redis()
        if r:
            pubsub = r.pubsub()
            pubsub.subscribe("lenore:events")
            try:
                yield 'data: {"type":"connected"}\n\n'
                while True:
                    message = pubsub.get_message(timeout=25)
                    if message and message["type"] == "message":
                        yield f"data: {message['data'].decode()}\n\n"
                    else:
                        yield ": keepalive\n\n"
            except GeneratorExit:
                pubsub.unsubscribe()
                pubsub.close()
        else:
            # No Redis — keepalives only; cross-user broadcast not available
            yield 'data: {"type":"connected"}\n\n'
            while True:
                time.sleep(25)
                yield ": keepalive\n\n"

    response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"
    return response
