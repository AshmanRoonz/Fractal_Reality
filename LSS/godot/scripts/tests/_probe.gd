# Intentionally blank: leftover probe file used to verify is_inside_tree()
# semantics under Godot's `-s` mode. Kept as a minimal SceneTree so the
# project still parses cleanly if someone wildcard-loads the tests directory.
extends SceneTree

func _init() -> void:
	quit(0)
