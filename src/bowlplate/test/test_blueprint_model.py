"""Unit test untuk bowlplate.domain.web_server.controller.blueprint.model"""

import dataclasses

import pytest

from bowlplate.domain.web_server.controller.blueprint.model import (
    BlueprintEntry,
    RegistrationHooks,
    RegistrationPriority,
)


def dummy_target():
    pass


def test_default_priority_is_normal():
    entry = BlueprintEntry(target=dummy_target)
    assert entry.priority == RegistrationPriority.NORMAL


def test_default_tags_is_empty_frozenset():
    entry = BlueprintEntry(target=dummy_target)
    assert entry.tags == frozenset()


def test_entries_sort_by_priority_ascending():
    critical = BlueprintEntry(target=dummy_target, priority=RegistrationPriority.CRITICAL)
    high = BlueprintEntry(target=dummy_target, priority=RegistrationPriority.HIGH)
    low = BlueprintEntry(target=dummy_target, priority=RegistrationPriority.LOW)
    normal = BlueprintEntry(target=dummy_target, priority=RegistrationPriority.NORMAL)

    ordered = sorted([low, normal, critical, high])
    assert ordered == [critical, high, normal, low]


def test_entry_is_frozen_and_immutable():
    entry = BlueprintEntry(target=dummy_target)
    with pytest.raises(dataclasses.FrozenInstanceError):
        entry.priority = RegistrationPriority.HIGH


def test_entry_accepts_custom_tags():
    entry = BlueprintEntry(target=dummy_target, tags=frozenset({"auth", "core"}))
    assert entry.tags == {"auth", "core"}


def test_registration_hooks_defaults_are_none():
    hooks = RegistrationHooks()
    assert hooks.before is None
    assert hooks.after is None
    assert hooks.on_error is None


def test_registration_hooks_invoke_callbacks():
    calls = []
    hooks = RegistrationHooks(
        before=lambda e: calls.append(("before", e)),
        after=lambda e: calls.append(("after", e)),
    )
    entry = BlueprintEntry(target=dummy_target)

    hooks.before(entry)
    hooks.after(entry)

    assert calls == [("before", entry), ("after", entry)]
