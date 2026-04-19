extends SceneTree
# Scratch probe; intentionally inert. The file lives on disk because the
# Cowork workspace blocks deletion, but it is not referenced by any runner
# and does nothing if executed directly.

func _init() -> void:
	quit(0)
