import sys
from unittest.mock import MagicMock

# Mock Google Generative AI
sys.modules["google"] = MagicMock()
sys.modules["google.generativeai"] = MagicMock()

# Mock jwt if needed
sys.modules["jwt"] = MagicMock()
