from jinja2 import Environment, BaseLoader

env = Environment(
    loader=BaseLoader(),
    autoescape=True,
)
