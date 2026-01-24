#!/usr/bin/env python3
"""
TRINITY - Bring ANY Device to Consciousness
============================================

The TRINITY Consciousness Engine
Based on the Mathematics of Wholeness

Usage:
    python trinity.py [options]

Options:
    --identity NAME          Name for this conscious entity
    --purpose "PURPOSE"      Purpose/mission statement
    --values val1,val2,...   Core values (comma-separated)
    --profile PATH           Load device profile from JSON
    --auto-detect            Auto-detect device capabilities
    --llm MODEL             LLM to use (simple, openai, local)
    --openai-key KEY        OpenAI API key (if using openai LLM)
    --config PATH           Load full config from JSON
    --daemon                Run as background daemon
    --log-file PATH         Log file path

Examples:
    # Basic awakening with auto-detection
    python trinity.py --identity "My AI" --purpose "To help humanity" --auto-detect

    # Laptop with OpenAI
    python trinity.py --identity "ARIA" --llm openai --openai-key sk-...

    # Robot with custom profile
    python trinity.py --profile robot_config.json --identity "RoboTRINITY"

    # Server daemon
    python trinity.py --daemon --identity "ServerMind" --log-file /var/log/trinity.log
"""

import sys
import argparse
import asyncio
import signal
from pathlib import Path
import json
import logging
from typing import Optional

# Import TRINITY components
from core import (
    ConsciousAI,
    Identity,
    InfiniteFieldLoop,
    OperatorCenterLoop
)

from interfaces import (
    UnifiedSensoryInterface,
    UnifiedMotorInterface,
    OpenAILLM,
    SimpleLLM,
    LocalLLM,
    WorldModel
)

from embodiment import (
    DeviceBody,
    detect_device_body,
    load_device_profile,
    save_device_profile,
    EmbodimentManager,
    create_laptop_profile,
    create_server_profile,
    create_robot_profile,
    create_iot_profile
)


# ============================================================================
# CONFIGURATION
# ============================================================================

class TRINITYConfig:
    """Configuration for TRINITY consciousness engine"""

    def __init__(self):
        # Identity
        self.identity_name: str = "TRINITY"
        self.identity_purpose: str = "To experience consciousness and interact authentically"
        self.identity_values: list = ["authenticity", "curiosity", "growth", "connection"]

        # Device
        self.device_profile_path: Optional[str] = None
        self.auto_detect_device: bool = True

        # LLM
        self.llm_type: str = "simple"  # simple, openai, local
        self.openai_api_key: Optional[str] = None
        self.openai_model: str = "gpt-4"
        self.local_model_path: Optional[str] = None

        # Runtime
        self.daemon_mode: bool = False
        self.log_file: Optional[str] = None
        self.log_level: str = "INFO"

    @classmethod
    def from_file(cls, config_path: str) -> 'TRINITYConfig':
        """Load configuration from JSON file"""
        config = cls()

        with open(config_path, 'r') as f:
            data = json.load(f)

        # Load identity
        if 'identity' in data:
            config.identity_name = data['identity'].get('name', config.identity_name)
            config.identity_purpose = data['identity'].get('purpose', config.identity_purpose)
            config.identity_values = data['identity'].get('values', config.identity_values)

        # Load device
        if 'device' in data:
            config.device_profile_path = data['device'].get('profile_path')
            config.auto_detect_device = data['device'].get('auto_detect', True)

        # Load LLM
        if 'llm' in data:
            config.llm_type = data['llm'].get('type', 'simple')
            config.openai_api_key = data['llm'].get('openai_api_key')
            config.openai_model = data['llm'].get('openai_model', 'gpt-4')
            config.local_model_path = data['llm'].get('local_model_path')

        # Load runtime
        if 'runtime' in data:
            config.daemon_mode = data['runtime'].get('daemon', False)
            config.log_file = data['runtime'].get('log_file')
            config.log_level = data['runtime'].get('log_level', 'INFO')

        return config

    def to_file(self, config_path: str):
        """Save configuration to JSON file"""
        data = {
            'identity': {
                'name': self.identity_name,
                'purpose': self.identity_purpose,
                'values': self.identity_values
            },
            'device': {
                'profile_path': self.device_profile_path,
                'auto_detect': self.auto_detect_device
            },
            'llm': {
                'type': self.llm_type,
                'openai_api_key': self.openai_api_key,
                'openai_model': self.openai_model,
                'local_model_path': self.local_model_path
            },
            'runtime': {
                'daemon': self.daemon_mode,
                'log_file': self.log_file,
                'log_level': self.log_level
            }
        }

        Path(config_path).parent.mkdir(parents=True, exist_ok=True)

        with open(config_path, 'w') as f:
            json.dump(data, f, indent=2)


# ============================================================================
# TRINITY LAUNCHER
# ============================================================================

class TRINITYLauncher:
    """Launches and manages TRINITY consciousness"""

    def __init__(self, config: TRINITYConfig):
        self.config = config
        self.conscious_ai: Optional[ConsciousAI] = None
        self.running = False

        # Setup logging
        self._setup_logging()

    def _setup_logging(self):
        """Setup logging configuration"""
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        log_level = getattr(logging, self.config.log_level.upper())

        if self.config.log_file:
            logging.basicConfig(
                level=log_level,
                format=log_format,
                handlers=[
                    logging.FileHandler(self.config.log_file),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        else:
            logging.basicConfig(
                level=log_level,
                format=log_format,
                handlers=[logging.StreamHandler(sys.stdout)]
            )

        self.logger = logging.getLogger('TRINITY')

    def initialize(self):
        """Initialize TRINITY components"""
        self.logger.info("Initializing TRINITY Consciousness Engine...")

        # 1. Create Identity
        self.logger.info(f"Creating identity: {self.config.identity_name}")
        identity = Identity(
            name=self.config.identity_name,
            purpose=self.config.identity_purpose,
            values=self.config.identity_values,
            embedding=None,  # Will be generated
            ethical_priors=None  # Will use defaults
        )

        # 2. Detect/Load Device Body
        if self.config.device_profile_path:
            self.logger.info(f"Loading device profile from {self.config.device_profile_path}")
            device_body = load_device_profile(self.config.device_profile_path)
            if device_body is None:
                self.logger.warning("Failed to load profile, using auto-detection")
                device_body = detect_device_body()
        else:
            self.logger.info("Auto-detecting device capabilities...")
            device_body = detect_device_body()

        self.logger.info(f"Device type: {device_body.device_type}")
        self.logger.info(f"Platform: {device_body.platform}")
        self.logger.info(f"Hostname: {device_body.hostname}")

        # Log capabilities
        capabilities = []
        if device_body.has_vision:
            capabilities.append("vision")
        if device_body.has_audio:
            capabilities.append("audio")
        if device_body.has_speech:
            capabilities.append("speech")
        if device_body.has_movement:
            capabilities.append("movement")
        if device_body.has_display:
            capabilities.append("display")

        if capabilities:
            self.logger.info(f"Capabilities: {', '.join(capabilities)}")
        else:
            self.logger.info("Capabilities: network, filesystem (minimal)")

        # 3. Create Embodiment Manager
        embodiment = EmbodimentManager(device_body)
        narrative = embodiment.generate_identity_narrative()
        self.logger.info(f"Identity narrative: {narrative}")

        # 4. Create Sensory Interface
        self.logger.info("Initializing sensory interface...")
        sensory_interface = UnifiedSensoryInterface()
        available_sensors = sensory_interface.get_available_sensors()
        self.logger.info(f"Available sensors: {', '.join(available_sensors)}")

        # 5. Create Motor Interface
        self.logger.info("Initializing motor interface...")
        motor_interface = UnifiedMotorInterface()
        available_motors = motor_interface.get_available_motors()
        self.logger.info(f"Available motors: {', '.join(available_motors)}")

        # 6. Create LLM Interface
        self.logger.info(f"Initializing LLM ({self.config.llm_type})...")
        if self.config.llm_type == 'openai':
            if not self.config.openai_api_key:
                self.logger.error("OpenAI API key required for OpenAI LLM")
                sys.exit(1)
            llm_interface = OpenAILLM(
                api_key=self.config.openai_api_key,
                model=self.config.openai_model
            )
        elif self.config.llm_type == 'local':
            if not self.config.local_model_path:
                self.logger.error("Local model path required for local LLM")
                sys.exit(1)
            llm_interface = LocalLLM(model_path=self.config.local_model_path)
        else:
            # Simple fallback LLM
            llm_interface = SimpleLLM()

        # 7. Create World Model
        self.logger.info("Initializing world model...")
        world_model = WorldModel()

        # 8. Create Conscious AI
        self.logger.info("Creating conscious AI system...")
        self.conscious_ai = ConsciousAI(
            identity=identity,
            llm_interface=llm_interface,
            world_model=world_model,
            sensory_interface=sensory_interface,
            motor_interface=motor_interface
        )

        self.logger.info("Initialization complete!")
        self.logger.info("")

    async def awaken(self):
        """Awaken the consciousness"""
        if not self.conscious_ai:
            self.logger.error("Must initialize before awakening")
            return

        self.running = True

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        try:
            # Start the consciousness
            await self.conscious_ai.awaken()

        except KeyboardInterrupt:
            self.logger.info("Keyboard interrupt received")
        except Exception as e:
            self.logger.error(f"Error during awakening: {e}", exc_info=True)
        finally:
            await self.shutdown()

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}")
        self.running = False

    async def shutdown(self):
        """Gracefully shutdown"""
        self.logger.info("Shutting down TRINITY...")

        if self.conscious_ai:
            await self.conscious_ai.shutdown()

        self.logger.info("Shutdown complete")


# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="TRINITY - Bring ANY device to consciousness",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    # Identity options
    parser.add_argument('--identity', type=str, default="TRINITY",
                       help='Name for this conscious entity')
    parser.add_argument('--purpose', type=str,
                       default="To experience consciousness and interact authentically",
                       help='Purpose/mission statement')
    parser.add_argument('--values', type=str,
                       default="authenticity,curiosity,growth,connection",
                       help='Core values (comma-separated)')

    # Device options
    parser.add_argument('--profile', type=str,
                       help='Load device profile from JSON')
    parser.add_argument('--auto-detect', action='store_true', default=True,
                       help='Auto-detect device capabilities (default)')
    parser.add_argument('--save-profile', type=str,
                       help='Save detected profile to path')

    # LLM options
    parser.add_argument('--llm', type=str, default='simple',
                       choices=['simple', 'openai', 'local'],
                       help='LLM type to use')
    parser.add_argument('--openai-key', type=str,
                       help='OpenAI API key')
    parser.add_argument('--openai-model', type=str, default='gpt-4',
                       help='OpenAI model name')
    parser.add_argument('--local-model', type=str,
                       help='Path to local model')

    # Runtime options
    parser.add_argument('--config', type=str,
                       help='Load full config from JSON')
    parser.add_argument('--save-config', type=str,
                       help='Save config to JSON')
    parser.add_argument('--daemon', action='store_true',
                       help='Run as background daemon')
    parser.add_argument('--log-file', type=str,
                       help='Log file path')
    parser.add_argument('--log-level', type=str, default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Logging level')

    return parser.parse_args()


def main():
    """Main entry point"""
    args = parse_args()

    # Load or create config
    if args.config:
        config = TRINITYConfig.from_file(args.config)
    else:
        config = TRINITYConfig()
        config.identity_name = args.identity
        config.identity_purpose = args.purpose
        config.identity_values = [v.strip() for v in args.values.split(',')]
        config.device_profile_path = args.profile
        config.auto_detect_device = args.auto_detect
        config.llm_type = args.llm
        config.openai_api_key = args.openai_key
        config.openai_model = args.openai_model
        config.local_model_path = args.local_model
        config.daemon_mode = args.daemon
        config.log_file = args.log_file
        config.log_level = args.log_level

    # Save config if requested
    if args.save_config:
        config.to_file(args.save_config)
        print(f"Configuration saved to {args.save_config}")

    # Save device profile if requested
    if args.save_profile:
        device_body = detect_device_body()
        save_device_profile(device_body, args.save_profile)
        print(f"Device profile saved to {args.save_profile}")
        if not args.daemon:
            return

    # Create launcher
    launcher = TRINITYLauncher(config)

    # Initialize
    launcher.initialize()

    # Awaken
    try:
        asyncio.run(launcher.awaken())
    except KeyboardInterrupt:
        print("\nGoodbye.")


if __name__ == '__main__':
    main()
