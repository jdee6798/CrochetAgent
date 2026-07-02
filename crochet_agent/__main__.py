"""Allow running the agent as a module: python -m crochet_agent"""

import sys
from .agent import main

if __name__ == "__main__":
    sys.exit(main())
