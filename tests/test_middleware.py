import pytest

from starlette.responses import PlainTextResponse
from starlette.testclient import TestClient

from content_size_limit_asgi import ContentSizeLimitMiddleware, ContentSizeExceeded


def test_content_size_limit_exceeded(app):
    app.add_middleware(ContentSizeLimitMiddleware, max_content_size=1000)

    @app.route("/", methods=["POST"])
    async def index(request):
        body = await request.body()
        return PlainTextResponse(f"test: {body}")

    client = TestClient(app)

    with pytest.raises(ContentSizeExceeded):
        client.post("/", data=b"a" * 1001)


def test_content_size_within_limit(app):
    app.add_middleware(ContentSizeLimitMiddleware, max_content_size=1000)

    @app.route("/", methods=["POST"])
    async def index(request):
        body = await request.body()
        return PlainTextResponse(f"test: {body}")

    client = TestClient(app)

    resp = client.post("/", data=b"a" * 10)
    assert resp.status_code == 200


def test_no_content_size_limit(app):
    app.add_middleware(ContentSizeLimitMiddleware)

    @app.route("/", methods=["POST"])
    async def index(request):
        body = await request.body()
        return PlainTextResponse(f"test: {body}")

    client = TestClient(app)

    resp = client.post("/", data=b"a" * 100)
    assert resp.content == f"test: {b'a' * 100}".encode('utf-8')


def test_custom_exception_class(app):
    class MyException(Exception):
        pass

    app.add_middleware(ContentSizeLimitMiddleware, exception_cls=MyException, max_content_size=1000)

    @app.route("/", methods=["POST"])
    async def index(request):
        body = await request.body()
        return PlainTextResponse(f"test: {body}")

    client = TestClient(app)

    with pytest.raises(MyException):
        client.post("/", data=b"a" * 1001)
