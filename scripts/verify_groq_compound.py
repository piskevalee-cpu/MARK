
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from mark_cli.config import AVAILABLE_MODELS
from mark_cli.providers.groq import GroqProvider

def verify_groq_compound():
    print("Verifying Groq Compound integration...")
    
    # Check config
    if "groq/compound" in AVAILABLE_MODELS.get("groq", []):
        print("✅ 'groq/compound' found in AVAILABLE_MODELS")
    else:
        print("❌ 'groq/compound' NOT found in AVAILABLE_MODELS")
        return False
        
    # Check provider static lists
    if "groq/compound" in GroqProvider.MODELS:
        print("✅ 'groq/compound' found in GroqProvider.MODELS")
    else:
        print("❌ 'groq/compound' NOT found in GroqProvider.MODELS")
        return False
        
    if "groq/compound" in GroqProvider.MODEL_DISPLAY_NAMES:
        print("✅ 'groq/compound' found in GroqProvider.MODEL_DISPLAY_NAMES")
    else:
        print("❌ 'groq/compound' NOT found in GroqProvider.MODEL_DISPLAY_NAMES")
        return False

    return True

if __name__ == "__main__":
    if verify_groq_compound():
        print("\nSUCCESS: Groq Compound configuration looks correct.")
        sys.exit(0)
    else:
        print("\nFAILURE: Configuration errors found.")
        sys.exit(1)
