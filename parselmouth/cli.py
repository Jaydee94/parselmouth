import click
import os
import yaml
import subprocess
from pathlib import Path
from click.shell_completion import CompletionItem
from parselmouth.gemini import analyze_document


def load_config_from_file(config_path: Path) -> dict:
    if config_path.exists():
        with open(config_path, 'r') as f:
            return yaml.safe_load(f) or {}
    return {}


def find_and_load_config(config_file: Path = None) -> dict:
    if config_file:
        return load_config_from_file(config_file)
    
    default_locations = [
        Path("parselmouth.yaml"), 
        Path("~/.config/parselmouth/config.yaml").expanduser()
    ]
    
    for location in default_locations:
        if location.exists():
            return load_config_from_file(location)
    
    return {}


def load_config(ctx, param, value):
    config = find_and_load_config(Path(value) if value else None)
    
    if ctx.default_map is None:
        ctx.default_map = {}
    ctx.default_map.update(config)
    return value


def validate_api_key(api_key: str):
    if not api_key:
        raise click.UsageError(
            "API Key is required. Set via --api-key, env var PARSELMOUTH_API_KEY, or config file."
        )


def get_analysis_params(ctx) -> dict:
    return {
        'api_key': ctx.obj['api_key'],
        'model': ctx.obj['model'],
        'include_date': ctx.obj['include_date'],
        'date_format': ctx.obj['date_format'],
        'separator': ctx.obj['separator']
    }


def analyze_file(input_file: Path, params: dict) -> str:
    return analyze_document(
        input_file,
        params['api_key'],
        params['model'],
        include_date=params['include_date'],
        date_format=params['date_format'],
        separator=params['separator']
    )


def build_new_path(input_file: Path, title: str) -> Path:
    return input_file.parent / f"{title}{input_file.suffix}"


def confirm_overwrite(file_path: Path) -> bool:
    if file_path.exists():
        return click.confirm(f"{file_path} already exists. Overwrite?")
    return True


def perform_rename(input_file: Path, new_path: Path, dry_run: bool):
    if dry_run:
        click.echo(f"Would rename: {input_file} -> {new_path}")
    else:
        if not confirm_overwrite(new_path):
            click.echo("Rename cancelled.")
            return
        input_file.rename(new_path)
        click.echo(f"Renamed: {input_file} -> {new_path}")


@click.group()
@click.option(
    '--config', 
    callback=load_config, 
    is_eager=True, 
    expose_value=False, 
    help="Path to config file.",
    type=click.Path(exists=True, dir_okay=False)
)
@click.option('--api-key', envvar='PARSELMOUTH_API_KEY', help="Gemini API Key.")
@click.option('--model', envvar='PARSELMOUTH_MODEL', default="gemini-2.5-flash", help="Gemini Model to use.")
@click.option('--include-date/--no-include-date', default=True, help="Include extracted date in the title.")
@click.option('--date-format', default="YYYY-MM-DD", help="Date format to use in the title.")
@click.option('--separator', default="_", help="Separator character for the title.")
@click.pass_context
def cli(ctx, api_key, model, include_date, date_format, separator):
    ctx.ensure_object(dict)
    ctx.obj['api_key'] = api_key
    ctx.obj['model'] = model
    ctx.obj['include_date'] = include_date
    ctx.obj['date_format'] = date_format
    ctx.obj['separator'] = separator


@cli.command()
@click.argument('input_file', type=click.Path(exists=True, path_type=Path), shell_complete=None)
@click.pass_context
def suggest(ctx, input_file):
    """Analyze a document and suggest a title."""
    validate_api_key(ctx.obj['api_key'])
    
    click.echo(f"Processing {input_file} with model {ctx.obj['model']}...")
    try:
        params = get_analysis_params(ctx)
        title = analyze_file(input_file, params)
        click.echo(f"Suggested Title: {title}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@cli.command()
@click.argument('input_file', type=click.Path(exists=True, path_type=Path), shell_complete=None)
@click.option('--dry-run', is_flag=True, help="Show what would be renamed without actually renaming.")
@click.pass_context
def rename(ctx, input_file, dry_run):
    """Analyze a document and rename it with the suggested title."""
    validate_api_key(ctx.obj['api_key'])
    
    click.echo(f"Processing {input_file} with model {ctx.obj['model']}...")
    try:
        params = get_analysis_params(ctx)
        title = analyze_file(input_file, params)
        new_path = build_new_path(input_file, title)
        perform_rename(input_file, new_path, dry_run)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


def detect_shell() -> str:
    shell = os.environ.get('SHELL', '')
    if 'bash' in shell:
        return 'bash'
    elif 'zsh' in shell:
        return 'zsh'
    elif 'fish' in shell:
        return 'fish'
    return None


def get_completion_config(shell: str) -> dict:
    home = Path.home()
    configs = {
        'bash': {
            'env_var': 'bash_source',
            'script_path': home / '.parselmouth-complete.bash',
            'rc_file': home / '.bashrc',
            'source_line': 'source ~/.parselmouth-complete.bash'
        },
        'zsh': {
            'env_var': 'zsh_source',
            'script_path': home / '.parselmouth-complete.zsh',
            'rc_file': home / '.zshrc',
            'source_line': 'source ~/.parselmouth-complete.zsh'
        },
        'fish': {
            'env_var': 'fish_source',
            'script_path': home / '.config/fish/completions/parselmouth.fish',
            'rc_file': None,
            'source_line': None
        }
    }
    return configs.get(shell)


def install_completion(shell: str):
    config = get_completion_config(shell)
    if not config:
        raise ValueError(f"Unsupported shell: {shell}")
    
    script_path = config['script_path']
    script_path.parent.mkdir(parents=True, exist_ok=True)
    
    env_var = f"_PARSELMOUTH_COMPLETE={config['env_var']}"
    result = subprocess.run(
        f"{env_var} parselmouth",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        raise RuntimeError(f"Failed to generate completion script: {result.stderr}")
    
    script_path.write_text(result.stdout)
    click.echo(f"✓ Generated completion script: {script_path}")
    
    if config['rc_file']:
        rc_file = config['rc_file']
        source_line = config['source_line']
        
        if rc_file.exists():
            content = rc_file.read_text()
            if source_line not in content:
                with rc_file.open('a') as f:
                    f.write(f"\n# Parselmouth completion\n{source_line}\n")
                click.echo(f"✓ Added source line to {rc_file}")
            else:
                click.echo(f"✓ Source line already exists in {rc_file}")
        else:
            rc_file.write_text(f"# Parselmouth completion\n{source_line}\n")
            click.echo(f"✓ Created {rc_file} with source line")
    
    click.echo(f"\n✓ Shell completion installed successfully!")
    click.echo(f"\nTo activate, run: source {config['rc_file'] or script_path}")
    click.echo(f"Or restart your shell.")


@cli.command('setup-completion')
def setup_completion():
    """Install shell auto-completion for parselmouth."""
    shell = detect_shell()
    
    if not shell:
        click.echo("Could not detect your shell. Supported shells: bash, zsh, fish", err=True)
        click.echo("\nManual setup instructions:")
        click.echo("  Bash: _PARSELMOUTH_COMPLETE=bash_source parselmouth > ~/.parselmouth-complete.bash")
        click.echo("  Zsh:  _PARSELMOUTH_COMPLETE=zsh_source parselmouth > ~/.parselmouth-complete.zsh")
        click.echo("  Fish: _PARSELMOUTH_COMPLETE=fish_source parselmouth > ~/.config/fish/completions/parselmouth.fish")
        return
    
    click.echo(f"Detected shell: {shell}")
    
    try:
        install_completion(shell)
    except Exception as e:
        click.echo(f"Error installing completion: {e}", err=True)


if __name__ == '__main__':
    cli(obj={})
