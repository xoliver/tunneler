from colorama import Fore


def green(msg):
    return colour(msg, Fore.GREEN)


def red(msg):
    return colour(msg, Fore.RED)


def colour(msg, colour):
    return '{}{}{}'.format(colour, msg, Fore.RESET)


def ok(msg):
    return '[ {} ] {}'.format(green('OK'), msg)


def fail(msg):
    return '[ {} ] {}'.format(red('FAIL'), msg)
