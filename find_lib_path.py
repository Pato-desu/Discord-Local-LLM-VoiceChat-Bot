import interactions
import os
print(f"Interactions path: {os.path.dirname(interactions.__file__)}")

from interactions.api.voice.encryption import Decryption
import inspect
print(f"Decryption source file: {inspect.getsourcefile(Decryption)}")
