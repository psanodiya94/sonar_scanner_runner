#!/usr/bin/env ruby
# frozen_string_literal: true

#
# Sonar Scanner Runner - Server Launcher
# This Ruby script starts the Python backend server and optionally opens a browser
#

require 'socket'
require 'timeout'

class SonarServerLauncher
  DEFAULT_PORT = 8080
  DEFAULT_HOST = '0.0.0.0'
  PYTHON_SERVER = File.join(__dir__, 'backend', 'server.py')

  def initialize
    @port = ARGV[0]&.to_i || DEFAULT_PORT
    @host = DEFAULT_HOST
    @server_pid = nil
  end

  def run
    puts '=' * 60
    puts '  Sonar Scanner Runner - Server Launcher'
    puts '=' * 60
    puts

    check_prerequisites
    check_port_availability
    start_server
    wait_for_server
    open_browser
    monitor_server

  rescue Interrupt
    puts "\n\nReceived interrupt signal..."
    stop_server
  rescue StandardError => e
    puts "\nError: #{e.message}"
    puts e.backtrace.join("\n") if ENV['DEBUG']
    stop_server
    exit 1
  end

  private

  def check_prerequisites
    puts 'Checking prerequisites...'

    # Check for Python
    unless system('python3 --version > /dev/null 2>&1')
      puts '✗ Python 3 not found'
      puts '  Please install Python 3 to continue'
      exit 1
    end
    puts '✓ Python 3 found'

    # Check if server file exists
    unless File.exist?(PYTHON_SERVER)
      puts "✗ Server file not found: #{PYTHON_SERVER}"
      exit 1
    end
    puts '✓ Server file found'

    puts
  end

  def check_port_availability
    puts "Checking port #{@port}..."

    begin
      server = TCPServer.new(@host, @port)
      server.close
      puts "✓ Port #{@port} is available"
      puts
    rescue Errno::EADDRINUSE
      puts "✗ Port #{@port} is already in use"
      puts '  Please stop the existing service or use a different port'
      exit 1
    end
  end

  def start_server
    puts "Starting Python server on port #{@port}..."
    puts

    # Start the Python server in the background
    @server_pid = spawn(
      'python3', PYTHON_SERVER, @port.to_s,
      chdir: __dir__,
      out: $stdout,
      err: $stderr
    )

    # Detach so it runs independently
    Process.detach(@server_pid)

    puts "Server started with PID: #{@server_pid}"
    puts
  end

  def wait_for_server
    puts 'Waiting for server to be ready...'

    max_attempts = 30
    attempt = 0

    loop do
      attempt += 1
      break if server_ready?

      if attempt > max_attempts
        puts '✗ Server failed to start within timeout'
        stop_server
        exit 1
      end

      print '.'
      sleep 1
    end

    puts
    puts '✓ Server is ready!'
    puts
  end

  def server_ready?
    Timeout.timeout(1) do
      TCPSocket.new('localhost', @port).close
      true
    end
  rescue Errno::ECONNREFUSED, Errno::EHOSTUNREACH, Timeout::Error
    false
  end

  def open_browser
    url = "http://localhost:#{@port}"

    puts "Server is running at: #{url}"
    puts

    # Try to detect Windows environment
    if windows_environment?
      puts 'Detected Windows environment (via WSL or similar)'
      puts 'Attempting to open browser on Windows...'

      # Try various methods to open Windows browser
      windows_open_browser(url)
    else
      puts 'To access the application, open your browser and navigate to:'
      puts "  #{url}"
    end

    puts
  end

  def windows_environment?
    # Check if running in WSL
    return true if File.exist?('/proc/version') &&
                   File.read('/proc/version').include?('Microsoft')

    # Check environment variables
    return true if ENV['WSL_DISTRO_NAME'] || ENV['WSLENV']

    false
  end

  def windows_open_browser(url)
    commands = [
      "cmd.exe /c start #{url}",                    # WSL1/WSL2
      "powershell.exe -Command Start-Process #{url}", # Alternative for WSL
      "wslview #{url}",                             # wslu package
      "explorer.exe #{url}"                         # Direct explorer
    ]

    opened = false
    commands.each do |cmd|
      if system("#{cmd} > /dev/null 2>&1")
        puts "✓ Browser opened successfully"
        opened = true
        break
      end
    end

    unless opened
      puts "Could not automatically open browser."
      puts "Please manually open: #{url}"
    end
  end

  def monitor_server
    puts 'Server is running. Press Ctrl+C to stop.'
    puts '=' * 60
    puts

    # Keep the script running
    Process.wait(@server_pid) if @server_pid
  rescue Errno::ECHILD
    # Process already finished
    puts 'Server process has ended'
  end

  def stop_server
    return unless @server_pid

    puts 'Stopping server...'

    begin
      Process.kill('TERM', @server_pid)
      sleep 2

      # Force kill if still running
      Process.kill('KILL', @server_pid) if process_running?(@server_pid)
    rescue Errno::ESRCH
      # Process already stopped
    end

    puts 'Server stopped'
  end

  def process_running?(pid)
    Process.kill(0, pid)
    true
  rescue Errno::ESRCH
    false
  end
end

# Run the launcher
if __FILE__ == $PROGRAM_NAME
  SonarServerLauncher.new.run
end
