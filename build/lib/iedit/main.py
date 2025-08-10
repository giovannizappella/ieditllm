import click
import boto3
import json
import difflib
import os
import glob
import re
import google.generativeai as genai
import toml

@click.group()
def cli():
    pass

def load_config():
    config = {}
    # Check for global config
    global_config_path = os.path.join(os.path.expanduser('~/.config/iedit'), 'config.toml')
    if os.path.exists(global_config_path):
        with open(global_config_path, 'r') as f:
            config.update(toml.load(f))

    # Check for local config
    local_config_path = 'config.toml'
    if os.path.exists(local_config_path):
        with open(local_config_path, 'r') as f:
            config.update(toml.load(f))
    return config

def polish_text_bedrock(text, model_id, region):
    bedrock = boto3.client(service_name='bedrock-runtime', region_name=region)
    
    prompt = f"\n\nHuman: Please polish the following LaTeX document. Do not change any numerical values. Only return the polished document, without any other text.\n\n{text}\n\nAssistant:"
    
    body = json.dumps({
        "prompt": prompt,
        "max_tokens_to_sample": 4096,
        "temperature": 0.5,
        "top_k": 250,
        "top_p": 1,
        "stop_sequences": ["\n\nHuman:"],
        "anthropic_version": "bedrock-2023-05-31"
    })
    
    response = bedrock.invoke_model(
        body=body,
        modelId=model_id,
        accept='application/json',
        contentType='application/json'
    )
    
    response_body = json.loads(response.get('body').read())
    
    return response_body.get('completion')

def polish_text_gemini(text, model_id):
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel(model_id)
    prompt = f"Please polish the following LaTeX document. Do not change any numerical values. Only return the polished document, without any other text.\n\n{text}"
    response = model.generate_content(prompt)
    return response.text

def interactive_diff(original_text, polished_text):
    d = difflib.Differ()
    diff = list(d.compare(original_text.splitlines(keepends=True), polished_text.splitlines(keepends=True)))
    
    new_text = []
    
    for line in diff:
        if line.startswith(' '):
            new_text.append(line[2:])
        elif line.startswith('-'):
            click.echo(click.style(line, fg='red'), nl=False)
        elif line.startswith('+'):
            click.echo(click.style(line, fg='green'), nl=False)
            new_text.append(line[2:])

    return "".join(new_text)

def get_numbers(text):
    return re.findall(r'\d+\.\d+|\d+', text)

def polish_file(file_path, provider, model_id, region):
    click.echo(f"Polishing {file_path}...")
    with open(file_path, 'r') as f:
        original_text = f.read()
    
    original_numbers = get_numbers(original_text)

    try:
        if provider == 'bedrock':
            polished_text = polish_text_bedrock(original_text, model_id, region)
        elif provider == 'gemini':
            polished_text = polish_text_gemini(original_text, model_id)
        else:
            click.echo(f"Unknown provider: {provider}")
            return

        if polished_text:
            polished_numbers = get_numbers(polished_text)
            if original_numbers != polished_numbers:
                click.echo(click.style("Warning: Numerical values have been changed.", fg='yellow'))

            final_text = interactive_diff(original_text, polished_text)
            with open(file_path, 'w') as f:
                f.write(final_text)
            click.echo(f"File {file_path} saved.")
        else:
            click.echo("No changes were made.")
    except Exception as e:
        click.echo(f"An error occurred while polishing {file_path}: {e}")

@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--provider', type=click.Choice(['bedrock', 'gemini']), help='The AI provider to use.')
@click.option('--model-id', help='The model ID to use for polishing.')
@click.option('--region', help='The AWS region to use.')
def polish(path, provider, model_id, region):
    """Polishes a LaTeX file or all LaTeX files in a directory."""
    config = load_config()

    # Apply defaults from config if not provided by CLI arguments
    provider = provider or config.get('default', {}).get('provider', 'bedrock')
    model_id = model_id or config.get('default', {}).get('model_id', 'anthropic.claude-v2')
    region = region or config.get('default', {}).get('region', 'us-east-1')

    if os.path.isfile(path):
        polish_file(path, provider, model_id, region)
    elif os.path.isdir(path):
        for file_path in glob.glob(os.path.join(path, '*.tex')):
            polish_file(file_path, provider, model_id, region)
    else:
        click.echo("Invalid path. Please provide a valid file or directory path.")

if __name__ == '__main__':
    cli()