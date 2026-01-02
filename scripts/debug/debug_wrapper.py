#!/usr/bin/env python3
"""
Debug wrapper for ask_sdk_local_debug to show what's happening
"""
import sys
import logging
import os
from pathlib import Path

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add workspace and lambda folder to path so imports like `handlers.*` resolve after restructure
# Since this script is now in scripts/debug, go up 2 levels to get workspace root
workspace = Path(__file__).parent.parent.parent
lambda_dir = workspace / "lambda"
sys.path.insert(0, str(lambda_dir))
sys.path.insert(0, str(workspace))

print("=" * 60)
print("Alexa Skill Local Debug Wrapper")
print("=" * 60)

from ask_sdk_local_debug.local_debugger_invoker import LocalDebuggerInvoker

def load_credentials():
    """Load credentials from .alexa-debug file"""
    creds_file = workspace / '.alexa-debug'
    if not creds_file.exists():
        print(f"ERROR: {creds_file} not found!")
        print("Please create this file with your ACCESS_TOKEN, SKILL_ID, and REGION")
        sys.exit(1)
    
    creds = {}
    with open(creds_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    creds[key.strip()] = value.strip()
    
    return creds

if __name__ == "__main__":
    try:
        # Load credentials from file
        creds = load_credentials()
        
        # Validate region
        region = creds.get('REGION', 'NA')
        if region not in ['NA', 'EU', 'FE']:
            print(f"⚠️  Invalid REGION '{region}' in .alexa-debug")
            print("   Valid values are: NA, EU, FE")
            print("   Using 'NA' as default")
            region = 'NA'
        
        # Build arguments
        args = [
            "--accessToken", creds.get('ACCESS_TOKEN', ''),
            "--skillId", creds.get('SKILL_ID', ''),
            "--skillHandler", "lambda_handler",
            "--skillFilePath", str(workspace / "lambda" / "lambda_function.py"),
            "--region", region
        ]
        
        print(f"Skill ID: {creds.get('SKILL_ID', 'NOT SET')}")
        print(f"Region: {region}")
        print(f"Token length: {len(creds.get('ACCESS_TOKEN', ''))}")
        print(f"Token starts: {creds.get('ACCESS_TOKEN', '')[:30]}...")
        print(f"Handler: lambda_handler")
        print(f"Skill File: {workspace / 'lambda' / 'lambda_function.py'}")
        print()
        print("DEBUG - Arguments being passed:")
        for i in range(0, len(args), 2):
            if i+1 < len(args):
                arg_name = args[i]
                arg_value = args[i+1]
                if arg_name == '--accessToken':
                    print(f"  {arg_name}: {arg_value[:30]}... (length: {len(arg_value)})")
                else:
                    print(f"  {arg_name}: {arg_value}")
        print()
        
        print("Creating LocalDebuggerInvoker...")
        invoker = LocalDebuggerInvoker(args)
        print("Invoker created successfully!")
        print()
        
        print("Starting WebSocket connection...")
        print("This will connect to Alexa and wait for requests...")
        print("Keep this running and test your skill in the Alexa Developer Console")
        print("=" * 60)
        
        invoker.invoke()
        
    except KeyboardInterrupt:
        print("\n\nDebugger stopped by user")
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
