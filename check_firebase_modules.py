
try:
    from firebase_functions import auth_fn
    print("auth_fn is available")
except ImportError:
    print("auth_fn is NOT available")

try:
    from firebase_functions import auth
    print("auth is available")
    print(dir(auth))
except ImportError:
    print("auth is NOT available")

try:
    from firebase_functions import identity_fn
    print("identity_fn is available")
    print(dir(identity_fn))
except ImportError:
    print("identity_fn is NOT available")
