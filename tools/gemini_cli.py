import argparse
import os
import sys

import google.generativeai as genai
from rich.console import Console
from rich.markdown import Markdown

# Initialize Rich Console
console = Console()


def configure_gemini():
    """Configure Google Generative AI with API key."""
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        # Try to read from .env.local if not in env
        try:
            env_path = os.path.join(
                os.path.dirname(
                    os.path.dirname(__file__)),
                'web',
                '.env.local')
            if os.path.exists(env_path):
                with open(env_path, 'r') as f:
                    for line in f:
                        if line.startswith("GOOGLE_API_KEY="):
                            api_key = line.split('=')[1].strip()
                            break
        except Exception:
            pass

    if not api_key:
        console.print(
            "[bold red]❌ Error: GOOGLE_API_KEY not found.[/bold red]")
        console.print("Please set it in your environment or web/.env.local")
        return False

    genai.configure(api_key=api_key)
    return True


def generate_response(prompt, model_name="gemini-pro"):
    """Generate response from Gemini programmatically."""
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {e}"

def chat_with_gemini(prompt, model_name="gemini-pro"):
    """Send a prompt to Gemini and print the response."""
    try:
        with console.status(f"[bold green]Asking {model_name}...[/bold green]"):
            response_text = generate_response(prompt, model_name)

        if response_text.startswith("Error:"):
            console.print(f"[bold red]❌ Error communicating with Gemini: {response_text.split('Error: ')[1]}[/bold red]")
        else:
            console.print(f"\n[bold blue]🤖 Gemini ({model_name}):[/bold blue]")
            console.print(Markdown(response_text))

    except Exception as e:
        # This catch is for errors outside of generate_response, e.g., console.status issues
        console.print(
            f"[bold red]❌ An unexpected error occurred: {e}[/bold red]")


def list_models():
    """List available Gemini models."""
    try:
        console.print("[bold]Available Models:[/bold]")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                console.print(f"- [cyan]{m.name}[/cyan]")
    except Exception as e:
        console.print(f"[bold red]Error listing models: {e}[/bold red]")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Gemini CLI - Interface with Google's AI models")
    parser.add_argument(
        "prompt",
        nargs="*",
        help="The prompt to send to Gemini")
    parser.add_argument(
        "--model",
        default="gemini-pro",
        help="Model to use (default: gemini-pro)")
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available models")

    args = parser.parse_args()

    if not configure_gemini():
        sys.exit(1)

    if args.list:
        list_models()
        sys.exit(0)

    if args.prompt:
        prompt_text = " ".join(args.prompt)
        chat_with_gemini(prompt_text, args.model)
    else:
        # Interactive Mode
        console.print(
            "[bold purple]Welcome to Gemini CLI Interactive Mode[/bold purple]")
        console.print("Type 'exit' or 'quit' to leave.")

        while True:
            try:
                user_input = console.input(
                    "\n[bold yellow]You > [/bold yellow]")
                if user_input.lower() in ['exit', 'quit']:
                    break
                if not user_input.strip():
                    continue

                chat_with_gemini(user_input, args.model)
            except KeyboardInterrupt:
                break

    console.print("\n[dim]Goodbye![/dim]")
