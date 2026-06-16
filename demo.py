import requests
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.text import Text
from rich import box

console = Console()
BASE = "http://127.0.0.1:8000"


def show_response(response):
    """Display API response with color coding."""
    status = response.status_code
    data = response.json()

    if status < 400:
        console.print(f"  ✅ [{status}]", style="bold green", end=" ")
        console.print(data.get("message", data), style="green")
    else:
        detail = data.get("detail", data)
        console.print(f"  ❌ [{status}]", style="bold red", end=" ")
        console.print(detail, style="red")
    console.print()


def create_event():
    console.print("\n[bold cyan]── Create New Event ──[/bold cyan]\n")
    name = Prompt.ask("  Event name")
    seats = IntPrompt.ask("  Total seats")
    date = Prompt.ask("  Event date (YYYY-MM-DD)")

    r = requests.post(f"{BASE}/create-event", json={
        "event_name": name,
        "total_seats": seats,
        "event_date": date,
    })
    show_response(r)


def register_user():
    console.print("\n[bold cyan]── Register User ──[/bold cyan]\n")
    username = Prompt.ask("  Username")
    event_id = IntPrompt.ask("  Event ID")

    r = requests.post(f"{BASE}/register-user", json={
        "username": username,
        "event_id": event_id,
    })
    show_response(r)


def view_events():
    console.print("\n[bold cyan]── View Events ──[/bold cyan]\n")
    upcoming = Confirm.ask("  Show upcoming only?", default=False)
    sort_date = Confirm.ask("  Sort by date?", default=False)

    r = requests.get(f"{BASE}/view-events", params={
        "upcomming_only": upcoming,
        "order_by_date": sort_date,
    })

    if r.status_code >= 400:
        show_response(r)
        return

    events = r.json()

    if not events:
        console.print("  [yellow]No events found.[/yellow]\n")
        return

    table = Table(
        title="Events",
        box=box.ROUNDED,
        title_style="bold magenta",
        header_style="bold cyan",
        row_styles=["", "dim"],
    )
    table.add_column("ID", justify="center", style="bold")
    table.add_column("Event Name", style="white")
    table.add_column("Total Seats", justify="center")
    table.add_column("Remaining", justify="center")
    table.add_column("Registrations", justify="center")
    table.add_column("Date", justify="center", style="yellow")

    for e in events:
        remaining = e.get("remaining_seats", "?")
        remaining_style = "green" if remaining > 0 else "bold red"

        table.add_row(
            str(e["event_id"]),
            e["event_name"],
            str(e["total_seats"]),
            f"[{remaining_style}]{remaining}[/{remaining_style}]",
            str(e.get("total_registrations", "?")),
            e["event_date"],
        )

    console.print()
    console.print(table)
    console.print()


def cancel_registration():
    console.print("\n[bold cyan]── Cancel Registration ──[/bold cyan]\n")
    username = Prompt.ask("  Username")
    event_id = IntPrompt.ask("  Event ID")

    r = requests.delete(f"{BASE}/cancel-user-registration", json={
        "username": username,
        "event_id": event_id,
    })
    show_response(r)


def main():
    console.print(
        Panel(
            Text.from_markup(
                "[bold white]Event Management System[/bold white]\n"
                "[dim]Interactive API Demo[/dim]"
            ),
            box=box.DOUBLE_EDGE,
            style="cyan",
            padding=(1, 4),
        )
    )

    menu_options = {
        "1": ("Create Event", create_event),
        "2": ("Register User", register_user),
        "3": ("View Events", view_events),
        "4": ("Cancel Registration", cancel_registration),
        "5": ("Exit", None),
    }

    while True:
        console.print("\n[bold white]What would you like to do?[/bold white]\n")
        for key, (label, _) in menu_options.items():
            if key == "5":
                console.print(f"  [red]{key}.[/red] [dim]{label}[/dim]")
            else:
                console.print(f"  [cyan]{key}.[/cyan] {label}")

        console.print()
        choice = Prompt.ask(
            "  [bold]Select option[/bold]",
            choices=["1", "2", "3", "4", "5"],
            default="3",
        )

        if choice == "5":
            console.print("\n[bold green]👋 Goodbye![/bold green]\n")
            break

        _, action = menu_options[choice]
        try:
            action()
        except requests.ConnectionError:
            console.print(
                "\n  [bold red]⚠ Cannot connect to server![/bold red]"
                "\n  [dim]Make sure the server is running: uvicorn main:app --reload[/dim]\n"
            )
        except KeyboardInterrupt:
            console.print("\n[bold yellow]Returning to menu...[/bold yellow]")


if __name__ == "__main__":
    main()
