"""Read-only model connection check used by make doctor."""
import argparse
from .agent import ModelClient, ModelError, settings, validate_role_models


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    config = settings('.env')
    print('Provider:', config['provider'])
    client = ModelClient(config['base_url'], config['api_key'], '', config['provider'])
    try:
        validate_role_models(config['models'])
        available = client.models()
        print('Tool-capable models:', ', '.join(available) or 'none; check provider access')
        missing = []
        for role, model in config['models'].items():
            print(f'{role}: {model}')
            if model not in available:
                missing.append(role)
        if missing:
            print('Update unavailable model selections for: ' + ', '.join(missing))
            return 1
        print('Model connection ready.')
        return 0
    except ModelError as exc:
        print(str(exc))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
