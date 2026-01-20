from mgnipy._internal_functions import (
    get_args, 
    config_loader,
    create_folder
)

from mgnipy._pydantic_models import ConfigModel

def main():

    # Get command line arguments
    args = get_args(prog_name='mgnipy')
    # Load configuration from the specified config file
    config = config_loader(args.config)
    # validate config 
    ConfigModel.model_validate(config)
    # create cache directory if it doesn't exist
    create_folder(config['cache_dir'])

    print("TODO: Implement CLI functionality here.")
