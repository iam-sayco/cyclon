"""Application state management module.

This module provides centralized state management for the Cyclon application,
separating state logic from UI components for better testability and maintainability.
"""

from __future__ import annotations

import asyncio
from typing import Callable, TypeVar
from ptyprocess import PtyProcessUnicode

T = TypeVar("T")


class AppState:
    """Centralized application state manager.
    
    This class manages all reactive application state, providing observer pattern
    for UI updates and clean separation between state and UI logic.
    
    Attributes:
        current_process: Currently running subprocess (if any)
        current_process_pid: PID of the current process
        current_pty: PTY process for interactive mode (if any)
        pty_mode: Whether application is in PTY interactive mode
        should_stop_processing: Flag to signal processing loop to stop
        throbber_timer: Reference to throbber animation timer
        throbber_active: Whether throbber animation is active
        process_running: Whether a process is currently running
        
    Example:
        >>> state = AppState()
        >>> state.add_pty_mode_observer(lambda old, new: print(f"PTY mode: {new}"))
        >>> state.pty_mode = True  # Triggers observer
    """
    
    def __init__(self) -> None:
        """Initialize application state with default values."""
        # Process state
        self._current_process: asyncio.subprocess.Process | None = None
        self._current_process_pid: int | None = None
        self._current_pty: PtyProcessUnicode | None = None
        
        # UI state
        self._pty_mode: bool = False
        self._should_stop_processing: bool = False
        self._throbber_active: bool = False
        self._process_running: bool = False
        
        # References (not state per se, but managed here for consistency)
        self._throbber_timer = None
        self._throbber_ref = None
        self._process_status_ref = None
        
        # Observer callbacks
        self._pty_mode_observers: list[Callable[[bool, bool], None]] = []
        self._throbber_observers: list[Callable[[bool, bool], None]] = []
        self._process_running_observers: list[Callable[[bool, bool], None]] = []
    
    # Process state properties
    
    @property
    def current_process(self) -> asyncio.subprocess.Process | None:
        """Get current subprocess (if any)."""
        return self._current_process
    
    @current_process.setter
    def current_process(self, value: asyncio.subprocess.Process | None) -> None:
        """Set current subprocess."""
        self._current_process = value
        if value is not None:
            self._current_process_pid = value.pid
        else:
            self._current_process_pid = None
    
    @property
    def current_process_pid(self) -> int | None:
        """Get PID of current process."""
        return self._current_process_pid
    
    @property
    def current_pty(self) -> PtyProcessUnicode | None:
        """Get current PTY process (if any)."""
        return self._current_pty
    
    @current_pty.setter
    def current_pty(self, value: PtyProcessUnicode | None) -> None:
        """Set current PTY process and update pty_mode accordingly."""
        old_pty_mode = self._pty_mode
        self._current_pty = value
        self._pty_mode = value is not None
        
        if old_pty_mode != self._pty_mode:
            self._notify_pty_mode_observers(old_pty_mode, self._pty_mode)
    
    # UI state properties
    
    @property
    def pty_mode(self) -> bool:
        """Whether application is in PTY interactive mode."""
        return self._pty_mode
    
    @pty_mode.setter
    def pty_mode(self, value: bool) -> None:
        """Set PTY mode and notify observers."""
        if self._pty_mode != value:
            old_value = self._pty_mode
            self._pty_mode = value
            self._notify_pty_mode_observers(old_value, value)
    
    @property
    def should_stop_processing(self) -> bool:
        """Flag indicating processing should stop."""
        return self._should_stop_processing
    
    @should_stop_processing.setter
    def should_stop_processing(self, value: bool) -> None:
        """Set stop processing flag."""
        self._should_stop_processing = value
    
    @property
    def throbber_active(self) -> bool:
        """Whether throbber animation is active."""
        return self._throbber_active
    
    @throbber_active.setter
    def throbber_active(self, value: bool) -> None:
        """Set throbber state and notify observers."""
        if self._throbber_active != value:
            old_value = self._throbber_active
            self._throbber_active = value
            self._notify_throbber_observers(old_value, value)
    
    @property
    def process_running(self) -> bool:
        """Whether a process is currently running."""
        return self._process_running
    
    @process_running.setter
    def process_running(self, value: bool) -> None:
        """Set process running state and notify observers."""
        if self._process_running != value:
            old_value = self._process_running
            self._process_running = value
            self._notify_process_running_observers(old_value, value)
    
    # Reference properties (not reactive, just stored)
    
    @property
    def throbber_timer(self):
        """Get throbber animation timer reference."""
        return self._throbber_timer
    
    @throbber_timer.setter
    def throbber_timer(self, value) -> None:
        """Set throbber animation timer reference."""
        self._throbber_timer = value
    
    @property
    def throbber_ref(self):
        """Get throbber widget reference."""
        return self._throbber_ref
    
    @throbber_ref.setter
    def throbber_ref(self, value) -> None:
        """Set throbber widget reference."""
        self._throbber_ref = value
    
    @property
    def process_status_ref(self):
        """Get process status widget reference."""
        return self._process_status_ref
    
    @process_status_ref.setter
    def process_status_ref(self, value) -> None:
        """Set process status widget reference."""
        self._process_status_ref = value
    
    # Observer pattern methods
    
    def add_pty_mode_observer(self, callback: Callable[[bool, bool], None]) -> None:
        """Add observer for PTY mode changes.
        
        Args:
            callback: Function called with (old_value, new_value) when PTY mode changes.
        """
        self._pty_mode_observers.append(callback)
    
    def remove_pty_mode_observer(self, callback: Callable[[bool, bool], None]) -> None:
        """Remove PTY mode observer.
        
        Args:
            callback: Observer callback to remove.
        """
        if callback in self._pty_mode_observers:
            self._pty_mode_observers.remove(callback)
    
    def add_throbber_observer(self, callback: Callable[[bool, bool], None]) -> None:
        """Add observer for throbber state changes.
        
        Args:
            callback: Function called with (old_value, new_value) when throbber state changes.
        """
        self._throbber_observers.append(callback)
    
    def remove_throbber_observer(self, callback: Callable[[bool, bool], None]) -> None:
        """Remove throbber observer.
        
        Args:
            callback: Observer callback to remove.
        """
        if callback in self._throbber_observers:
            self._throbber_observers.remove(callback)
    
    def add_process_running_observer(self, callback: Callable[[bool, bool], None]) -> None:
        """Add observer for process running state changes.
        
        Args:
            callback: Function called with (old_value, new_value) when process state changes.
        """
        self._process_running_observers.append(callback)
    
    def remove_process_running_observer(self, callback: Callable[[bool, bool], None]) -> None:
        """Remove process running observer.
        
        Args:
            callback: Observer callback to remove.
        """
        if callback in self._process_running_observers:
            self._process_running_observers.remove(callback)
    
    def _notify_pty_mode_observers(self, old_value: bool, new_value: bool) -> None:
        """Notify all PTY mode observers."""
        for callback in self._pty_mode_observers:
            try:
                callback(old_value, new_value)
            except Exception:
                # Silently ignore observer errors to prevent cascading failures
                pass
    
    def _notify_throbber_observers(self, old_value: bool, new_value: bool) -> None:
        """Notify all throbber observers."""
        for callback in self._throbber_observers:
            try:
                callback(old_value, new_value)
            except Exception:
                pass
    
    def _notify_process_running_observers(self, old_value: bool, new_value: bool) -> None:
        """Notify all process running observers."""
        for callback in self._process_running_observers:
            try:
                callback(old_value, new_value)
            except Exception:
                pass
    
    # Utility methods
    
    def reset(self) -> None:
        """Reset all state to default values.
        
        This is useful when starting a new session or cleaning up.
        """
        old_pty_mode = self._pty_mode
        old_throbber = self._throbber_active
        old_running = self._process_running
        
        self._current_process = None
        self._current_process_pid = None
        self._current_pty = None
        self._pty_mode = False
        self._should_stop_processing = False
        self._throbber_active = False
        self._process_running = False
        self._throbber_timer = None
        self._throbber_ref = None
        self._process_status_ref = None
        
        # Notify observers about changes
        if old_pty_mode != self._pty_mode:
            self._notify_pty_mode_observers(old_pty_mode, self._pty_mode)
        if old_throbber != self._throbber_active:
            self._notify_throbber_observers(old_throbber, self._throbber_active)
        if old_running != self._process_running:
            self._notify_process_running_observers(old_running, self._process_running)
    
    def is_process_active(self) -> bool:
        """Check if any process is currently active (running or PTY)."""
        return self._current_process is not None or self._current_pty is not None
    
    def stop_all(self) -> None:
        """Signal all processes to stop and reset state."""
        self._should_stop_processing = True
        self._process_running = False
        self._throbber_active = False
        
        # Stop timer if present
        if self._throbber_timer is not None:
            try:
                self._throbber_timer.stop()
            except Exception:
                pass
            self._throbber_timer = None
    
    def __repr__(self) -> str:
        """Return string representation of state."""
        return (
            f"AppState(\n"
            f"  pty_mode={self._pty_mode},\n"
            f"  process_running={self._process_running},\n"
            f"  throbber_active={self._throbber_active},\n"
            f"  should_stop={self._should_stop_processing},\n"
            f"  has_process={self._current_process is not None},\n"
            f"  has_pty={self._current_pty is not None}\n"
            f")"
        )
