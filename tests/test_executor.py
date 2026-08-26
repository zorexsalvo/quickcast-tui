"""Tests for command execution."""

import asyncio

import pytest

from quickcast.spell import Spell
from quickcast.executor import execute_spell, execute_spell_and_collect, ExecutionError


@pytest.mark.asyncio
async def test_execute_simple_command():
    """Test executing a simple command."""
    spell = Spell(
        id="echo_test",
        name="Echo Test",
        command="echo hello",
    )
    
    lines = []
    async for line in execute_spell(spell):
        lines.append(line)
    
    assert len(lines) > 0
    assert "hello" in lines[0]


@pytest.mark.asyncio
async def test_execute_command_with_output():
    """Test executing command with multiple output lines."""
    spell = Spell(
        id="seq_test",
        name="Sequence Test",
        command="seq 1 3",
    )
    
    lines = []
    async for line in execute_spell(spell):
        lines.append(line)
    
    assert len(lines) == 3
    assert lines[0] == "1"
    assert lines[1] == "2"
    assert lines[2] == "3"


@pytest.mark.asyncio
async def test_collect_output():
    """Test collecting all output at once."""
    spell = Spell(
        id="hello_test",
        name="Hello Test",
        command="echo world",
    )
    
    exit_code, output = await execute_spell_and_collect(spell)
    
    assert exit_code == 0
    assert "world" in output


@pytest.mark.asyncio
async def test_command_failure():
    """Test executing a failing command."""
    spell = Spell(
        id="fail_test",
        name="Fail Test",
        command="false",
    )
    
    exit_code, output = await execute_spell_and_collect(spell)
    assert exit_code != 0


@pytest.mark.asyncio
async def test_invalid_command():
    """Test executing a command that produces an error."""
    spell = Spell(
        id="invalid_test",
        name="Invalid Test",
        command="false",  # Command that just fails
    )
    
    # The command should execute but return non-zero
    exit_code, output = await execute_spell_and_collect(spell)
    assert exit_code != 0
