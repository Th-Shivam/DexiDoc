import typer
import sys
import shlex
from pathlib import Path
from typing import Optional
from .config import load_config
from .logger import setup_logging
from .discovery import FileScanner

app = typer.Typer()

@app.callback(invoke_without_command=True)
def callback(ctx: typer.Context):
    """
    Dexidoc AI Help CLI
    """
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())

@app.command()
def status():
    """
    Show status info
    """
    config = load_config()
    logger = setup_logging(config)
    
    logger.info("Dexidoc status checked")
    typer.echo("Dexidoc CLI is running!")
    typer.echo(f"Config loaded from: {config.get('config_path', 'unknown')}")

def start():
    if len(sys.argv) > 1:
        app()
    else:
        # Interactive mode
        typer.echo("Dexidoc Interactive Shell. Type 'exit' to quit.")
        while True:
            try:
                command = input("dexidoc> ")
                if not command.strip():
                    continue
                
                if command.strip().lower() in ("exit", "quit"):
                    break
                
                args = shlex.split(command)
                try:
                    # standalone_mode=False prevents click from calling sys.exit()
                    app(args=args, standalone_mode=False, prog_name="dexidoc")
                except SystemExit:
                    pass
                except Exception as e:
                    typer.echo(f"Error: {e}")
                    
            except KeyboardInterrupt:
                typer.echo("\nType 'exit' to quit.")
            except EOFError:
                break



@app.command()
def scan(
    path: Path = typer.Argument(
        None,
        help="Directory to scan. Defaults to current directory.",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
    )
):
    """
    Scan a directory for supported document types.
    """
    config = load_config()
    logger = setup_logging(config) # Ensure logging is set up
    
    target_path = path if path else Path.cwd()
    
    typer.echo(f"Scanning directory: {target_path}")
    
    excludes = config.get("excludes", [])
    extensions = config.get("extensions", [])
    
    scanner = FileScanner(base_path=target_path, excludes=excludes, extensions=extensions)
    
    count = 0
    # Create a nice layout for the output maybe? For "not a single cent more", simple print is fine.
    # But user wants "Project runs from source cleanly".
    
    try:
        for file in scanner.scan():
            count += 1
            # Relative path for cleaner output if possible
            try:
                display_path = file.path.relative_to(target_path)
            except ValueError:
                display_path = file.path
                
            typer.echo(f"[FOUND] {display_path} ({file.size} bytes)")
    except Exception as e:
        logger.error(f"Scan failed: {e}")
        typer.echo(f"Scan failed: {e}")
        raise typer.Exit(code=1)
        
    typer.echo(f"Scan complete. Found {count} files.")

if __name__ == "__main__":
    app()
