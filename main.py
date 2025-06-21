import os
import anthropic
from typing import List, Dict, Any, Optional

class Colors:
    """ANSI color codes for terminal output"""
    USER = "\033[96m"      # Bright cyan
    CLAUDE = "\033[92m"    # Bright green
    SYSTEM = "\033[93m"    # Yellow
    TOOL = "\033[95m"      # Bright magenta
    ERROR = "\033[91m"     # Bright red
    RESET = "\033[0m"

class FileReaderTool:
    """Tool for reading files from the filesystem"""
    
    # Tool schema definition
    SCHEMA = {
        "name": "read_file",
        "description": "Read the contents of a file from the filesystem",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "The path to the file to read"
                }
            },
            "required": ["file_path"]
        }
    }
    
    @staticmethod
    def read_file(file_path: str) -> str:
        """Read file contents safely with error handling"""
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                return f"Error: File '{file_path}' not found."
            
            # Check if it's actually a file (not a directory)
            if not os.path.isfile(file_path):
                return f"Error: '{file_path}' is not a file."
            
            # Read the file
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            return content
        
        except PermissionError:
            return f"Error: Permission denied reading '{file_path}'."
        except UnicodeDecodeError:
            # Try reading as binary if text fails
            try:
                with open(file_path, 'rb') as file:
                    content = file.read()
                return f"Binary file detected. File size: {len(content)} bytes. Cannot display content as text."
            except Exception as e:
                return f"Error reading file: {str(e)}"
        except Exception as e:
            return f"Error reading file: {str(e)}"

class ListFilesTool:
    """Tool for listing files in a directory. If the path is not specified, it lists the current directory."""
    SCHEMA = {
        "name": "list_files",
        "description": "List files in a directory",
        "input_schema": {
            "type": "object",
            "properties": {
                "directory_path": {
                    "type": "string",
                    "description": "The path to the directory to list files from. Defaults to current directory if not provided."
                }
            },
            "required": []
        }
    }
    
    @staticmethod
    def list_files(directory_path: str = ".") -> str:
        """List files in the specified directory"""
        try:
            # Normalize the path
            directory_path = os.path.abspath(directory_path)

            # Allow listing only directories from current working directory
            if not directory_path.startswith(os.getcwd()):
                return f"Error: Access to '{directory_path}' is not allowed. Only current directory and subdirectories are accessible."
            
            # Check if the path is a directory
            if not os.path.isdir(directory_path):
                return f"Error: '{directory_path}' is not a valid directory."
            
            # List files
            files = os.listdir(directory_path)
            for f in files:
                full_path = os.path.join(directory_path, f)
                if os.path.isfile(full_path):
                    size = os.path.getsize(full_path)
                    files[files.index(f)] = f"{f} (Size: {size} bytes)"
                else:
                    files[files.index(f)] = f"{f} (Directory)"

            return str(files)
        
        except PermissionError:
            return f"Error: Permission denied accessing '{directory_path}'."
        except Exception as e:
            return f"Error listing files: {str(e)}"

class EditFileTool:
    """Tool for editing files in the current directory"""

    SCHEMA = {
        "name": "edit_file",
        "description": "Edit a file in the current directory",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "The path to the file to edit"
                },
                "old_str": {
                    "type": "string",
                    "description": "The string to replace"
                },
                "new_str": {
                    "type": "string",
                    "description": "The string to replace with"
                }
            },
            "required": ["file_path", "old_str", "new_str"]
        }
    }

    @staticmethod
    def edit_file(file_path: str, old_str: str, new_str: str) -> str:
        """Edit a file by replacing old_str with new_str"""
        try:
            # Normalize the path
            file_path = os.path.abspath(file_path)

            # Allow editing only files in the current working directory
            if not file_path.startswith(os.getcwd()):
                return f"Error: Access to '{file_path}' is not allowed. Only files in the current directory are editable."

            # Check if file exists
            if not os.path.exists(file_path):
                file = open(file_path, 'w')  # Create the file if it doesn't exist
                file.close()

            # Check if it's actually a file (not a directory)
            if not os.path.isfile(file_path):
                return f"Error: '{file_path}' is not a file."
            
            # Read the file
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Replace the string
            new_content = content.replace(old_str, new_str)
            
            # Write the changes back to the file
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(new_content)
            return f"File '{file_path}' edited successfully."
        
        except PermissionError:
            return f"Error: Permission denied editing '{file_path}'."
        except Exception as e:
            return f"Error editing file: {str(e)}"

class TerminalChat:
    """Main chat application class"""
    
    def __init__(self):
        self.client = anthropic.Anthropic()
        self.messages: List[Dict[str, Any]] = []
        self.file_tool = FileReaderTool()
        self.list_files_tool = ListFilesTool()
        self.edit_file_tool = EditFileTool()
        self.tools = self._setup_tools()
    
    def _setup_tools(self) -> List[Dict[str, Any]]:
        """Setup tool definitions for Claude"""
        return [
            self.file_tool.SCHEMA,
            self.list_files_tool.SCHEMA,
            self.edit_file_tool.SCHEMA
        ]
    
    def _handle_tool_use(self, tool_call) -> str:
        """Handle tool use requests from Claude"""
        match tool_call.name:
            case "read_file":
                file_path = tool_call.input["file_path"]
                print(f"{Colors.TOOL}Reading file: {file_path}{Colors.RESET}")
                
                # Execute the tool
                result = self.file_tool.read_file(file_path)

            case "list_files":
                directory_path = tool_call.input["directory_path"] if "directory_path" in tool_call.input else "."
                print(f"{Colors.TOOL}Listing files in: {directory_path}{Colors.RESET}")

                # Execute the tool
                result = self.list_files_tool.list_files(directory_path)

            case "edit_file":
                file_path = tool_call.input["file_path"]
                old_str = tool_call.input["old_str"]
                new_str = tool_call.input["new_str"]
                print(f"{Colors.TOOL}Editing file: {file_path}{Colors.RESET}")

                #Execute the tool
                result = self.edit_file_tool.edit_file(file_path, old_str, new_str)
            case _:
                print(f"{Colors.ERROR}Unknown tool: {tool_call.name}{Colors.RESET}")

        # Add tool call and result to messages
        self.messages.append({
            "role": "assistant",
            "content": [tool_call]
        })
        # Ensure result is a dict for Anthropic tool_result
        self.messages.append({
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": tool_call.id,
                    "content": result
                }
            ]
        })
    
    def _process_claude_response(self, response) -> bool:
        """Process Claude's response and handle tool use. Returns True if conversation should continue."""
        if response.stop_reason == "tool_use":
            # Extract text content and tool calls
            tool_call = None
            text_content = ""
            
            for content in response.content:
                if content.type == "text":
                    text_content += content.text
                elif content.type == "tool_use":
                    tool_call = content
            
            # Display any text response first
            if text_content.strip():
                print(f"{Colors.CLAUDE}Claude:{Colors.RESET} {text_content}")
            
            # Handle the tool use
            if tool_call:
                self._handle_tool_use(tool_call)
                return True  # Continue conversation to get Claude's response to tool result
        else:
            # Handle regular text response
            ai_message = ""
            for content in response.content:
                if content.type == "text":
                    ai_message += content.text
            
            print(f"{Colors.CLAUDE}Claude:{Colors.RESET} {ai_message}")
            self.messages.append({"role": "assistant", "content": ai_message})
        
        return False  # End this response cycle
    
    def _get_user_input(self) -> Optional[str]:
        """Get user input and check for exit commands"""
        user_input = input(f"{Colors.USER}You:{Colors.RESET} ")
        if user_input.lower() in ["exit", "quit"]:
            print(f"{Colors.SYSTEM}Exiting chat.{Colors.RESET}")
            return None
        return user_input
    
    def _send_message_to_claude(self):
        """Send current messages to Claude and process response"""
        try:
            response = self.client.messages.create(
                model="claude-3-5-haiku-latest",
                messages=self.messages,
                tools=self.tools,
                max_tokens=1000,
            )
            return response
        except Exception as e:
            print(f"{Colors.ERROR}Error communicating with Claude: {str(e)}{Colors.RESET}")
            return None
    
    def _display_welcome_message(self):
        """Display welcome message"""
        print(f"{Colors.SYSTEM}Welcome to Python AI AGENT! Type 'exit' or 'quit' to stop.{Colors.RESET}")
    
    def run(self):
        """Main chat loop"""
        self._display_welcome_message()
        
        while True:
            # Get user input
            user_input = self._get_user_input()
            if user_input is None:
                break
            
            # Add user message
            self.messages.append({"role": "user", "content": user_input})
            
            # Process Claude's response(s)
            while True:
                response = self._send_message_to_claude()
                if response is None:
                    break
                
                # Process the response and check if we need to continue
                should_continue = self._process_claude_response(response)
                if not should_continue:
                    break

def main():
    """Entry point for the application"""
    chat = TerminalChat()
    chat.run()

if __name__ == "__main__":
    main()