import click
from g4.main import app
import uvicorn # pyright: reportMissingTypeStubs=false

@click.group()
def g4():
    pass

@g4.command("run")
def run():
    uvicorn.run(app, host="127.0.0.1", port=5000, log_level="info") # pyright: ignore


if __name__ == "__main__":
    g4()