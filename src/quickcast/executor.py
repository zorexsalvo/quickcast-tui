"""Command execution with real-time output streaming."""

import asyncio
import subprocess
from typing import AsyncIterator

from .spell import Spell


class ExecutionError(Exception):
    """Raised when command execution fails."""

    pass


async def execute_spell(spell: Spell) -> AsyncIterator[str]:
    """Execute a spell and yield output lines in real-time.

    Args:
        spell: The Spell to execute

    Yields:
        Lines of output from the command

    Raises:
        ExecutionError: If command execution fails
    """
    try:
        # Use shell=True to allow complex commands with pipes, redirects, etc.
        process = await asyncio.create_subprocess_shell(
            spell.command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )

        if process.stdout is None:
            raise ExecutionError(f"Failed to execute spell {spell.id}")

        # Stream output line by line
        while True:
            line = await process.stdout.readline()
            if not line:
                break
            yield line.decode().rstrip("\n")

        # Wait for process to complete
        await process.wait()

    except Exception as e:
        raise ExecutionError(f"Error executing spell {spell.id}: {e}")


async def execute_spell_and_collect(spell: Spell, timeout: float = 30.0) -> tuple[int, str]:
    """Execute a spell and return exit code and collected output.

    Args:
        spell: The Spell to execute
        timeout: Maximum time to wait for command completion (seconds)

    Returns:
        Tuple of (exit_code, output_text)

    Raises:
        ExecutionError: If command execution fails or times out
    """
    try:
        process = await asyncio.wait_for(
            asyncio.create_subprocess_shell(
                spell.command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            ),
            timeout=timeout,
        )

        stdout_bytes, _ = await asyncio.wait_for(process.communicate(), timeout=timeout)
        stdout = stdout_bytes.decode() if stdout_bytes else ""

        return process.returncode or 0, stdout

    except asyncio.TimeoutError:
        raise ExecutionError(f"Spell {spell.id} timed out after {timeout}s")
    except Exception as e:
        raise ExecutionError(f"Error executing spell {spell.id}: {e}")
