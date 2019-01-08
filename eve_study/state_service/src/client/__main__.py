import sys
import logging

from command_line_parser import parse_command_line

def execute_command_line(args = None):
    global log 
    log = logging.getLogger(__name__)
    args = parse_command_line() if args is None else args
    logging.basicConfig(format='\n%(asctime)s - %(name)s - %(levelname)s: %(message)s',
                        level=logging.getLevelName(args.loglevel),
                        filename=args.log_file,
                        filemode='w')
    log.info("Logging set to level: " + str(args.loglevel.upper()))
    exit_code = args.func(**vars(args))
    return exit_code

if __name__ == "__main__":
    exit_code = execute_command_line()
    sys.exit(exit_code)
