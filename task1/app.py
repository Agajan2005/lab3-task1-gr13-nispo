import os
import time
import random

from flask import Flask
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.flask import FlaskInstrumentor

app = Flask(__name__)

resource = Resource(attributes={SERVICE_NAME: "lab3-flask-app"})

jaeger_exporter = JaegerExporter(
    agent_host_name=os.getenv("JAEGER_AGENT_HOST", "jaeger"),
    agent_port=int(os.getenv("JAEGER_AGENT_PORT", 6831)),
)

provider = TracerProvider(resource=resource)
provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
trace.set_tracer_provider(provider)

FlaskInstrumentor().instrument_app(app)

tracer = trace.get_tracer(__name__)


@app.route("/")
def index():
    with tracer.start_as_current_span("index-handler") as span:
        span.set_attribute("http.route", "/")
        time.sleep(random.uniform(0.05, 0.2))
        return "Hello from lab3 task1!\n"


@app.route("/error")
def error():
    with tracer.start_as_current_span("error-handler") as span:
        span.set_attribute("http.route", "/error")
        raise RuntimeError("Искусственная ошибка для демонстрации трассировки")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)