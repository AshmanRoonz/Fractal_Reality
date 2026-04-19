# Intentionally blank: placeholder left by a parse check. Not run by the
# normal test suite (tests are invoked individually via `-s`), but kept as a
# minimal SceneTree so the project still parses cleanly if someone wildcard-
# loads the tests directory. Safe to delete if the filesystem permits.
extends SceneTree

func _init() -> void:
	quit(0)
