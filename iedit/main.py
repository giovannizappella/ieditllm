import click
import boto3
import json
import difflib
import os
import glob
import re

@click.group()
def cli():
    pass

def polish_text(text, model_id, region):
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

def polish_file(file_path, model_id, region):
    click.echo(f"Polishing {file_path}...")
    with open(file_path, 'r') as f:
        original_text = f.read()
    
    original_numbers = get_numbers(original_text)

    try:
        polished_text = polish_text(original_text, model_id, region)
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
@click.option('--model-id', default='anthropic.claude-v2', help='The model ID to use for polishing.')
@click.option('--region', default='us-east-1', help='The AWS region to use.')
def polish(path, model_id, region):
    """Polishes a LaTeX file or all LaTeX files in a directory."""
    if os.path.isfile(path):
        polish_file(path, model_id, region)
    elif os.path.isdir(path):
        for file_path in glob.glob(os.path.join(path, '*.tex')):
            polish_file(file_path, model_id, region)
    else:
        click.echo("Invalid path. Please provide a valid file or directory path.")

if __name__ == '__main__':
    cli()
