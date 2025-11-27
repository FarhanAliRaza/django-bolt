from pathlib import Path
import click


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def main():
    """Django-Bolt command line interface."""


@main.command()
def version():
    """Show Django-Bolt version."""
    import tomllib

    cli_dir = Path(__file__).parent.resolve()
    toml_file = cli_dir / "../../pyproject.toml"

    with toml_file.open("rb") as f:
        pyproject = tomllib.load(f)

    click.echo(f"Django-Bolt version: {pyproject['project']['version']}")


@main.command()
def init():
    """Initialize Django-Bolt in an existing Django project."""
    # Find Django project root (look for manage.py)
    current_dir = Path.cwd()
    project_root = None
    for path in [current_dir] + list(current_dir.parents):
        if (path / "manage.py").exists():
            project_root = path
            break

    if not project_root:
        click.echo("Error: No Django project found (manage.py not found)", err=True)
        click.echo("Please run this command from within a Django project directory.")
        return

    click.echo(f"Found Django project at: {project_root}")

    # Find settings.py to determine project name
    settings_files = list(project_root.glob("*/settings.py"))
    if not settings_files:
        click.echo("Error: Could not find settings.py", err=True)
        return

    project_name = settings_files[0].parent.name
    settings_file = settings_files[0]

    click.echo(f"Project name: {project_name}")

    # 1. Add django_bolt to INSTALLED_APPS
    settings_content = settings_file.read_text()
    if "'django_bolt'" not in settings_content and '"django_bolt"' not in settings_content:
        if "INSTALLED_APPS" in settings_content:
            # Find INSTALLED_APPS and add django_bolt
            lines = settings_content.splitlines()
            new_lines = []
            in_installed_apps = False
            added = False

            for line in lines:
                if "INSTALLED_APPS" in line and "=" in line:
                    in_installed_apps = True
                elif in_installed_apps and not added:
                    # Look for the first app entry and add django_bolt before it
                    if line.strip().startswith(("'", '"')) and not added:
                        new_lines.append('    "django_bolt",')
                        added = True
                    elif "]" in line and not added:
                        # End of INSTALLED_APPS, add before closing
                        new_lines.append('    "django_bolt",')
                        added = True
                        in_installed_apps = False

                new_lines.append(line)

            if added:
                settings_file.write_text("\n".join(new_lines))
                click.echo("✓ Added 'django_bolt' to INSTALLED_APPS")
            else:
                click.echo("Warning: Could not automatically add to INSTALLED_APPS. Please add 'django_bolt' manually.")
        else:
            click.echo("Warning: INSTALLED_APPS not found in settings.py. Please add 'django_bolt' manually.")
    else:
        click.echo("✓ 'django_bolt' already in INSTALLED_APPS")

    # 2. Create api.py template
    api_file = project_root / project_name / "api.py"
    if not api_file.exists():
        api_template = '''"""Django-Bolt API routes."""
from django_bolt import BoltAPI
import msgspec
from typing import Optional

api = BoltAPI()


@api.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Welcome to Django-Bolt!"}


@api.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "service": "django-bolt"}


# Example with path parameters
@api.get("/items/{item_id}")
async def get_item(item_id: int, q: Optional[str] = None):
    """Get an item by ID."""
    return {"item_id": item_id, "q": q}


# Example with request body validation using msgspec
class Item(msgspec.Struct):
    name: str
    price: float
    is_offer: Optional[bool] = None


@api.post("/items")
async def create_item(item: Item):
    """Create a new item."""
    return {"item": item, "created": True}
'''
        api_file.write_text(api_template)
        click.echo(f"✓ Created {api_file.relative_to(project_root)}")
    else:
        click.echo(f"✓ {api_file.relative_to(project_root)} already exists")

    click.echo("\n🚀 Django-Bolt initialization complete!")
    click.echo("\nNext steps:")
    click.echo("1. Run migrations: python manage.py migrate")
    click.echo("2. Start the server: python manage.py runbolt")
    click.echo(f"3. Edit your API routes in {project_name}/api.py")
    click.echo("\nFor more information, visit: https://github.com/FarhanAliRaza/django-bolt")
