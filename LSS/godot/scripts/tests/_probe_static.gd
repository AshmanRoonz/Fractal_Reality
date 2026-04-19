extends SceneTree
# Scratch probe; intentionally inert. Used to confirm that static-func
# dispatch through a preloaded script with no class_name is broken in `-s`
# mode; the finding drove the DeathCamMath class_name extraction. Kept as a
# minimal SceneTree because the Cowork workspace blocks deletion.

func _init() -> void:
	quit(0)
