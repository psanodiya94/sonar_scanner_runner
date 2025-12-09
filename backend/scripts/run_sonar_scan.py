#!/usr/bin/env python3
"""
Sonar Scanner Execution Script
Handles the actual execution of Sonar Scanner with build wrapper.
"""

import os
import sys
import subprocess
import json
import shutil
from datetime import datetime
from pathlib import Path


class SonarScanRunner:
    """Class to handle Sonar Scanner execution"""

    def __init__(self, repo_name, branch_name, release_version):
        self.repo_name = repo_name
        self.branch_name = branch_name
        self.release_version = release_version
        self.project_root = Path(__file__).parent.parent.parent
        self.temp_dir = self.project_root / 'temp' / f"{repo_name}_{branch_name}_{int(datetime.now().timestamp())}"
        self.config = self._load_config()

    def _load_config(self):
        """Load configuration from config file"""
        config_path = self.project_root / 'config.json'
        default_config = {
            'sonar_host_url': os.environ.get('SONAR_HOST_URL', 'http://localhost:9000'),
            'sonar_token': os.environ.get('SONAR_TOKEN', ''),
            'workspace_dir': os.environ.get('WORKSPACE_DIR', str(self.project_root / 'temp')),
            'build_wrapper_cmd': 'build-wrapper-linux-x86-64',
            'sonar_scanner_cmd': 'sonar-scanner',
            'build_prerequisites': {
                'global': [],
                'maven': [],
                'gradle': [],
                'cmake': [],
                'make': [],
                'npm': [],
                'python': []
            }
        }

        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                print(f"Warning: Could not load config file: {e}")

        return default_config

    def print_step(self, message):
        """Print a step message"""
        print(f"\n{'='*60}")
        print(f"  {message}")
        print(f"{'='*60}\n")

    def run_command(self, command, cwd=None, shell=False):
        """Run a shell command and stream output"""
        print(f"Executing: {command if isinstance(command, str) else ' '.join(command)}")

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            cwd=cwd,
            shell=shell
        )

        for line in iter(process.stdout.readline, ''):
            if line:
                print(line.rstrip())

        process.wait()
        return process.returncode

    def check_prerequisites(self):
        """Check if required tools are available"""
        self.print_step("Checking Prerequisites")

        tools = [
            ('git', 'Git'),
            (self.config['sonar_scanner_cmd'], 'SonarQube Scanner'),
            (self.config['build_wrapper_cmd'], 'Build Wrapper')
        ]

        missing_tools = []
        for cmd, name in tools:
            if shutil.which(cmd):
                print(f"✓ {name} found: {cmd}")
            else:
                print(f"✗ {name} NOT found: {cmd}")
                missing_tools.append(name)

        if missing_tools:
            print(f"\nError: Missing required tools: {', '.join(missing_tools)}")
            print("\nPlease ensure the following are installed and in PATH:")
            print("  - Git")
            print("  - SonarQube Scanner (sonar-scanner)")
            print("  - Build Wrapper (build-wrapper-linux-x86-64)")
            return False

        return True

    def clone_repository(self):
        """Clone the repository"""
        self.print_step(f"Cloning Repository: {self.repo_name}")

        # Create temp directory
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        # Clone repository
        clone_cmd = ['git', 'clone', '--branch', self.branch_name, '--single-branch', self.repo_name, str(self.temp_dir)]
        returncode = self.run_command(clone_cmd)

        if returncode != 0:
            print(f"Error: Failed to clone repository (exit code: {returncode})")
            return False

        print(f"✓ Repository cloned to: {self.temp_dir}")
        return True

    def detect_build_system(self):
        """Detect the build system used in the project"""
        self.print_step("Detecting Build System")

        build_files = {
            'pom.xml': ('maven', 'mvn clean install'),
            'build.gradle': ('gradle', './gradlew build'),
            'build.gradle.kts': ('gradle', './gradlew build'),
            'CMakeLists.txt': ('cmake', 'cmake . && make'),
            'Makefile': ('make', 'make'),
            'package.json': ('npm', 'npm install && npm run build'),
            'setup.py': ('python', 'python setup.py build'),
        }

        for build_file, (system, cmd) in build_files.items():
            if (self.temp_dir / build_file).exists():
                print(f"✓ Detected {system} project ({build_file})")
                return system, cmd

        print("⚠ Could not detect build system, will skip build step")
        return None, None

    def show_prerequisites(self, build_system):
        """Display prerequisite commands that will be executed"""
        if not build_system:
            return True

        prerequisites = self.config.get('build_prerequisites', {})
        global_prereqs = prerequisites.get('global', [])
        system_prereqs = prerequisites.get(build_system, [])

        all_prereqs = global_prereqs + system_prereqs

        if not all_prereqs:
            print("No prerequisite commands configured")
            return True

        self.print_step(f"Build Prerequisites for {build_system}")

        print("The following prerequisite commands will be executed before the build:")
        print("(These will run in the same terminal session as the build command)\n")

        if global_prereqs:
            print("Global prerequisites:")
            for i, prereq_cmd in enumerate(global_prereqs, 1):
                print(f"  [{i}] {prereq_cmd}")
            print()

        if system_prereqs:
            print(f"{build_system.capitalize()} specific prerequisites:")
            for i, prereq_cmd in enumerate(system_prereqs, 1):
                print(f"  [{i}] {prereq_cmd}")
            print()

        return True

    def build_with_wrapper(self, build_command, build_system=None):
        """Build the project with build wrapper"""
        self.print_step("Building Project with Build Wrapper")

        if not build_command:
            print("No build command provided, skipping build step")
            return True

        output_dir = self.temp_dir / 'bw-output'

        # Get prerequisite commands
        prerequisites = self.config.get('build_prerequisites', {})
        global_prereqs = prerequisites.get('global', [])
        system_prereqs = prerequisites.get(build_system, []) if build_system else []
        all_prereqs = global_prereqs + system_prereqs

        # Build the full command chain to ensure prerequisites run in same terminal
        if all_prereqs:
            print(f"Including {len(all_prereqs)} prerequisite command(s) in build chain")
            prereq_chain = ' && '.join(all_prereqs)
            wrapper_cmd = f"{prereq_chain} && {self.config['build_wrapper_cmd']} --out-dir {output_dir} {build_command}"
        else:
            wrapper_cmd = f"{self.config['build_wrapper_cmd']} --out-dir {output_dir} {build_command}"

        returncode = self.run_command(wrapper_cmd, cwd=self.temp_dir, shell=True)

        if returncode != 0:
            print(f"Warning: Build wrapper returned non-zero exit code: {returncode}")
            print("Continuing with scan anyway...")

        return True

    def run_sonar_scanner(self):
        """Run SonarQube Scanner"""
        self.print_step("Running SonarQube Scanner")

        # Prepare sonar-scanner command
        scanner_cmd = [
            self.config['sonar_scanner_cmd'],
            f"-Dsonar.projectKey={self.repo_name.split('/')[-1].replace('.git', '')}",
            f"-Dsonar.projectName={self.repo_name.split('/')[-1].replace('.git', '')}",
            f"-Dsonar.projectVersion={self.release_version}",
            f"-Dsonar.sources=.",
            f"-Dsonar.host.url={self.config['sonar_host_url']}",
        ]

        # Add token if available
        if self.config['sonar_token']:
            scanner_cmd.append(f"-Dsonar.login={self.config['sonar_token']}")

        # Add build wrapper output if exists
        bw_output = self.temp_dir / 'bw-output'
        if bw_output.exists():
            scanner_cmd.append(f"-Dsonar.cfamily.build-wrapper-output={bw_output}")

        returncode = self.run_command(scanner_cmd, cwd=self.temp_dir)

        if returncode != 0:
            print(f"\nError: SonarQube Scanner failed with exit code: {returncode}")
            return False

        print("\n✓ SonarQube Scanner completed successfully")
        return True

    def cleanup(self):
        """Clean up temporary files"""
        self.print_step("Cleaning Up")

        try:
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
                print(f"✓ Removed temporary directory: {self.temp_dir}")
        except Exception as e:
            print(f"Warning: Could not remove temporary directory: {e}")

    def run(self):
        """Main execution flow"""
        print("\n" + "="*60)
        print("  SONAR SCANNER RUNNER")
        print("="*60)
        print(f"Repository: {self.repo_name}")
        print(f"Branch: {self.branch_name}")
        print(f"Version: {self.release_version}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60 + "\n")

        try:
            # Check prerequisites
            if not self.check_prerequisites():
                return 1

            # Clone repository
            if not self.clone_repository():
                return 1

            # Detect build system
            build_system, build_cmd = self.detect_build_system()

            # Show prerequisite steps that will be executed
            if build_system:
                if not self.show_prerequisites(build_system):
                    return 1

            # Build with wrapper (includes prerequisites in same terminal)
            if build_system:
                if not self.build_with_wrapper(build_cmd, build_system):
                    return 1

            # Run Sonar Scanner
            if not self.run_sonar_scanner():
                return 1

            self.print_step("SUCCESS")
            print("✓ Sonar Scanner execution completed successfully!")
            print(f"✓ Results should be available at: {self.config['sonar_host_url']}")

            return 0

        except Exception as e:
            print(f"\nFATAL ERROR: {e}")
            import traceback
            traceback.print_exc()
            return 1

        finally:
            # Cleanup
            self.cleanup()


def main():
    """Main entry point"""
    if len(sys.argv) != 4:
        print("Usage: run_sonar_scan.py <repository_name> <branch_name> <release_version>")
        sys.exit(1)

    repo_name = sys.argv[1]
    branch_name = sys.argv[2]
    release_version = sys.argv[3]

    runner = SonarScanRunner(repo_name, branch_name, release_version)
    exit_code = runner.run()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
