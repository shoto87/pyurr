import typer
import json
import os
import time
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

app = typer.Typer(help="A cat that lives in your terminal.")
console = Console()

SAVE_FILE = Path.home() / ".pyurr_state.json"


class Cat:
    def __init__(self):
        self.state = {
            "name": "Purr",
            "hunger": 50.0,
            "happiness": 50.0,
            "last_update": time.time(),
        }
        self.load()
        self.apply_decay()

    def load(self):
        if SAVE_FILE.exists():
            self.state.update(json.loads(SAVE_FILE.read_text()))

    def save(self):
        self.state["last_update"] = time.time()
        SAVE_FILE.write_text(json.dumps(self.state))

    def apply_decay(self):
        now = time.time()
        elapsed_hours = (now - self.state["last_update"]) / 3600
        self.state["hunger"] = min(100.0, self.state["hunger"] + (elapsed_hours * 5))
        self.state["happiness"] = max(
            0.0, self.state["happiness"] - (elapsed_hours * 3)
        )

    def get_mood_art(self):
        h = self.state["hunger"]
        hap = self.state["happiness"]

        if h > 80:
            return "[red]( =ＴωＴ= )[/red]\n[italic]Purr is starving...[/italic]"
        if hap < 20:
            return "[blue](  - ω - )[/blue]\n[italic]Purr feels lonely.[/italic]"
        if hap > 80:
            return "[magenta](=^･ω･^=)ノ[/magenta]\n[italic]Purr is vibrating with joy![/italic]"
        return "[green](=^･ω･^=)[/green]\n[italic]Purr is chilling.[/italic]"


# Helper to get the pet instance
pet = Cat()


@app.command()
def status():
    """Check on your cat and see how they are doing."""

    cwd = os.getcwd()
    context_msg = ""
    if "Documents" in cwd:
        context_msg = "Purr is watching you work... it looks bored."
    elif "Downloads" in cwd:
        context_msg = "Purr is playing with a stray .zip file."
    else:
        context_msg = f"Purr is lounging in {os.path.basename(cwd) or 'root'}."

    console.print(
        Panel(pet.get_mood_art(), title="[bold white]Purr[/bold white]", expand=False)
    )

    console.print(
        f"Hunger:    [red]{'#' * int(pet.state['hunger'] // 10)}[/red] {pet.state['hunger']:.1f}%"
    )
    console.print(
        f"Happiness: [green]{'#' * int(pet.state['happiness'] // 10)}[/green] {pet.state['happiness']:.1f}%"
    )
    console.print(f"\n[dim]{context_msg}[/dim]")
    pet.save()


@app.command()
def feed(item: str = typer.Argument("kibble", help="What to feed the cat")):
    """Give your cat something to eat."""
    if pet.state["hunger"] < 10:
        console.print("Purr sniffs the food and walks away. Not hungry.")
    else:
        pet.state["hunger"] = max(0, pet.state["hunger"] - 25)
        pet.state["happiness"] = min(100, pet.state["happiness"] + 5)
        console.print(
            f"You fed Purr some [bold yellow]{item}[/bold yellow]! [magental]~nom nom~[/magenta]"
        )
    pet.save()


@app.command()
def play():
    """Play with your cat."""
    pet.state["happiness"] = min(100, pet.state["happiness"] + 30)
    pet.state["hunger"] = min(100, pet.state["hunger"] + 15)
    console.print("You waved a string! Purr did a [bold]backflip[/bold].")
    pet.save()


@app.command()
def rename(new_name: str):
    """Change your cat's name."""
    old_name = pet.state["name"]
    pet.state["name"] = new_name
    console.print(f"{old_name} is now known as [bold cyan]{new_name}[/bold cyan]!")
    pet.save()


if __name__ == "__main__":
    app()
