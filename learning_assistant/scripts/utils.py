import random
import string


def generate_anon_user_string(N = 30):
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(N))

